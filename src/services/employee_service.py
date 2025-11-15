import os
from typing import Any, Dict, List, Tuple
import datetime
from config.sqlserver_connection import get_sqlserver_connection
from config.mysql_connection import get_mysql_connection

def get_db_vendor() -> str:
	return os.environ.get("DB_VENDOR", "sqlserver").strip().lower()


def get_salary_db_vendor() -> str:
	return os.environ.get("SALARY_DB_VENDOR", get_db_vendor()).strip().lower()


def _get_connection(vendor: str):
	if vendor == "mysql":
		return get_mysql_connection()
	return get_sqlserver_connection()


def fetch_data_from_db(sql_query: str, params: Tuple[Any, ...], vendor: str | None = None):
	conn = None
	actual_vendor = vendor or get_db_vendor()
	try:
		conn = _get_connection(actual_vendor)
		db_cursor = conn.cursor()
		db_cursor.execute(sql_query, params)
		columns = [column[0] for column in db_cursor.description]
		return [dict(zip(columns, row)) for row in db_cursor.fetchall()]
	except Exception as e:
		raise Exception(f"Lỗi DTB: {e}")
	finally:
		if conn:
			conn.close()


def fetch_scalar_from_db(sql_query: str, params: Tuple[Any, ...], vendor: str | None = None) -> int:
	conn = None
	actual_vendor = vendor or get_db_vendor()
	try:
		conn = _get_connection(actual_vendor)
		db_cursor = conn.cursor()
		db_cursor.execute(sql_query, params)
		row = db_cursor.fetchone()
		return int(row[0]) if row else 0
	finally:
		if conn:
			conn.close()


def _placeholder(vendor: str) -> str:
	return "?" if vendor == "sqlserver" else "%s"


def fetch_latest_salaries(employee_ids: List[int]) -> Dict[int, Dict[str, Any]]:
	if not employee_ids:
		return {}

	vendor = get_salary_db_vendor()
	placeholder = _placeholder(vendor)
	in_clause = ", ".join([placeholder] * len(employee_ids))

	query = f"""
SELECT s.EmployeeID,
       s.SalaryMonth,
       s.BaseSalary,
       s.Bonus,
       s.Deductions,
       s.NetSalary
FROM salaries s
JOIN (
	SELECT EmployeeID, MAX(SalaryMonth) AS LatestMonth
	FROM salaries
	WHERE EmployeeID IN ({in_clause})
	GROUP BY EmployeeID
) latest ON latest.EmployeeID = s.EmployeeID AND latest.LatestMonth = s.SalaryMonth
"""

	rows = fetch_data_from_db(query, tuple(employee_ids), vendor=vendor)
	result: Dict[int, Dict[str, Any]] = {}
	for row in rows:
		result[row["EmployeeID"]] = {
			"SalaryDate": row.get("SalaryMonth"),
			"BasicSalary": row.get("BaseSalary"),
			"Bonus": row.get("Bonus"),
			"Deduction": row.get("Deductions"),
			"TotalSalary": row.get("NetSalary"),
		}
	return result


def get_all_employees(department_id=None, status=None, page=1, size=10):
	vendor = get_db_vendor()
	placeholder = _placeholder(vendor)

	base_query = """
SELECT 
	e.EmployeeID,
	e.FullName,
	e.Status,
	e.Email,
	e.PhoneNumber,
	d.DepartmentName,
	p.PositionName
FROM employees e
JOIN departments d ON e.DepartmentID = d.DepartmentID
JOIN positions p ON e.PositionID = p.PositionID
WHERE 1 = 1
"""

	filters: List[str] = []
	params: List[Any] = []

	if department_id is not None:
		filters.append(f"e.DepartmentID = {placeholder}")
		params.append(department_id)

	if status:
		filters.append(f"e.Status = {placeholder}")
		params.append(status)

	if filters:
		base_query += " AND " + " AND ".join(filters)

	offset = (page - 1) * size
	if vendor == "mysql":
		paginated_query = f"{base_query} ORDER BY e.EmployeeID LIMIT {size} OFFSET {offset}"
	else:
		paginated_query = f"{base_query} ORDER BY e.EmployeeID OFFSET {offset} ROWS FETCH NEXT {size} ROWS ONLY"

	employee_rows = fetch_data_from_db(paginated_query, tuple(params), vendor=vendor)

	count_query = "SELECT COUNT(e.EmployeeID) FROM employees e WHERE 1 = 1"
	if filters:
		count_query += " AND " + " AND ".join(filters)

	total_count = fetch_scalar_from_db(count_query, tuple(params), vendor=vendor)

	employee_ids = [row["EmployeeID"] for row in employee_rows]

	salary_map: Dict[int, Dict[str, Any]] = {}
	try:
		salary_map = fetch_latest_salaries(employee_ids)
	except Exception as e:
		# Đưa thông tin lỗi vào salary_map dưới dạng None để không chặn toàn bộ API
		salary_map = {}

	employees: List[Dict[str, Any]] = []
	for row in employee_rows:
		employee_id = row.get("EmployeeID")
		employee = {
			"EmployeeID": employee_id,
			"FullName": row.get("FullName"),
			"DepartmentName": row.get("DepartmentName"),
			"Email": row.get("Email"),
			"PhoneNumber": row.get("PhoneNumber"),
			"PositionName": row.get("PositionName"),
			"Status": row.get("Status"),
			"Salary": salary_map.get(employee_id)
		}
		employees.append(employee)

	return {
		"total_records": total_count,
		"page": page,
		"size": size,
		"employees": employees
	}
 
def create_employee_transaction(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Tạo nhân viên mới + lương trong cả 2 DB (SQL Server + MySQL) trong 1 transaction thủ công.
    - SQL Server: insert nhân viên, ID tự động tăng
    - MySQL: insert nhân viên + salary, dùng EmployeeID từ SQL Server
    - Kiểm tra EmployeeID trên MySQL để tránh duplicate key
    """
    vendors = ["sqlserver", "mysql"]
    connections = {}
    cursors = {}
    employee_id = None

    try:
        # Mở kết nối và bắt đầu transaction
        for v in vendors:
            conn = _get_connection(v)
            conn.autocommit = False
            connections[v] = conn
            cursors[v] = conn.cursor()

        # --- SQL SERVER INSERT ---
        cursor_sql = cursors["sqlserver"]
        placeholder_sql = _placeholder("sqlserver")

        full_name = data.get("FullName")
        dept_id = data.get("DepartmentID")
        pos_id = data.get("PositionID")
        status = data.get("Status", "Thực tập")
        email = data.get("Email")
        dob_str = data.get("DateOfBirth")
        date_of_birth = datetime.datetime.strptime(dob_str, "%Y-%m-%d").date() if dob_str else datetime.date(2000,1,1)
        hire_date = datetime.date.today()

        insert_sql = f"""
        INSERT INTO employees (FullName, DepartmentID, PositionID, Email, Status, DateOfBirth, HireDate)
        OUTPUT INSERTED.EmployeeID
        VALUES ({placeholder_sql},{placeholder_sql},{placeholder_sql},{placeholder_sql},{placeholder_sql},{placeholder_sql},{placeholder_sql})
        """
        cursor_sql.execute(insert_sql, (full_name, dept_id, pos_id, email, status, date_of_birth, hire_date))
        
        # Lấy EmployeeID vừa tạo từ OUTPUT clause
        row = cursor_sql.fetchone()
        if not row or row[0] is None:
            raise Exception("Không lấy được employee_id từ SQL Server")
        employee_id = int(row[0])

        # --- MYSQL CHECK EMPLOYEEID ---
        cursor_mysql = cursors["mysql"]
        placeholder_mysql = _placeholder("mysql")

        cursor_mysql.execute(f"SELECT COUNT(*) FROM employees WHERE EmployeeID = {placeholder_mysql}", (employee_id,))
        count = cursor_mysql.fetchone()[0]
        if count > 0:
            raise Exception(f"EmployeeID {employee_id} đã tồn tại trên MySQL, không thể insert")

        # --- MYSQL INSERT EMPLOYEE ---
        insert_mysql = f"""
        INSERT INTO employees (EmployeeID, FullName, DepartmentID, PositionID, Status)
        VALUES ({placeholder_mysql},{placeholder_mysql},{placeholder_mysql},{placeholder_mysql},{placeholder_mysql})
        """
        cursor_mysql.execute(insert_mysql, (employee_id, full_name, dept_id, pos_id, status))

        # --- MYSQL INSERT SALARY ---
        salary = float(data.get("Salary", 0))
        salary_date = datetime.date.today().replace(day=1)
        bonus = 0.0
        deductions = 0.0
        net_salary = salary + bonus - deductions

        insert_salary = f"""
        INSERT INTO salaries (EmployeeID, SalaryMonth, BaseSalary, Bonus, Deductions, NetSalary)
        VALUES ({placeholder_mysql},{placeholder_mysql},{placeholder_mysql},{placeholder_mysql},{placeholder_mysql},{placeholder_mysql})
        """
        cursor_mysql.execute(insert_salary, (employee_id, salary_date, salary, bonus, deductions, net_salary))

        # Commit cả 2 DB
        connections["sqlserver"].commit()
        connections["mysql"].commit()

        return {
            "EmployeeID": employee_id,
            "FullName": full_name,
            "DepartmentID": dept_id,
            "PositionID": pos_id,
            "Status": status,
            "Salary": {
                "BasicSalary": salary,
                "Bonus": bonus,
                "Deduction": deductions,
                "SalaryDate": salary_date.strftime("%Y-%m-%d"),
                "TotalSalary": net_salary
            }
        }

    except Exception as e:
        # Rollback cả 2 DB nếu lỗi
        for conn in connections.values():
            try:
                conn.rollback()
            except:
                pass
        raise Exception(f"Lỗi khi thêm nhân viên mới: {e}")

    finally:
        # Đóng kết nối
        for conn in connections.values():
            conn.close()

def delete_employee_service(employee_id: int) -> dict:
    """
    Xóa nhân viên trong MySQL + SQL Server theo kiểu AUTO CASCADE
    (không sửa CSDL, tự tìm tất cả bảng con)
    """
    vendors = ["mysql", "sqlserver"]
    connections = {}
    cursors = {}

    try:
        # Mở kết nối
        for v in vendors:
            conn = _get_connection(v)
            conn.autocommit = False
            connections[v] = conn
            cursors[v] = conn.cursor()

        # ----------- MYSQL -----------
        cursor_mysql = cursors["mysql"]
        placeholder_mysql = _placeholder("mysql")

        # Lấy danh sách bảng con trỏ tới employees
        cursor_mysql.execute("""
            SELECT TABLE_NAME
            FROM information_schema.KEY_COLUMN_USAGE
            WHERE REFERENCED_TABLE_NAME = 'employees'
              AND REFERENCED_COLUMN_NAME = 'EmployeeID'
              AND TABLE_SCHEMA = DATABASE();
        """)
        child_tables_mysql = [row[0] for row in cursor_mysql.fetchall()]

        # Xóa bảng con
        for table in child_tables_mysql:
            cursor_mysql.execute(f"DELETE FROM {table} WHERE EmployeeID = {placeholder_mysql}", (employee_id,))

        # Xóa employee cuối cùng
        cursor_mysql.execute(f"DELETE FROM employees WHERE EmployeeID = {placeholder_mysql}", (employee_id,))

        # ----------- SQL SERVER -----------
        cursor_sql = cursors["sqlserver"]
        placeholder_sql = _placeholder("sqlserver")

        # Lấy danh sách bảng con trỏ tới employees
        cursor_sql.execute("""
            SELECT OBJECT_NAME(fk.parent_object_id)
            FROM sys.foreign_keys fk
            INNER JOIN sys.foreign_key_columns fkc
                ON fk.object_id = fkc.constraint_object_id
            INNER JOIN sys.columns c
                ON fkc.parent_object_id = c.object_id AND fkc.parent_column_id = c.column_id
            WHERE fk.referenced_object_id = OBJECT_ID('employees')
              AND c.name = 'EmployeeID';
        """)
        child_tables_sql = [row[0] for row in cursor_sql.fetchall()]

        # Xóa bảng con SQL Server
        for table in child_tables_sql:
            cursor_sql.execute(f"DELETE FROM {table} WHERE EmployeeID = ?", (employee_id,))

        # Xóa employee SQL Server cuối cùng
        cursor_sql.execute(f"DELETE FROM employees WHERE EmployeeID = ?", (employee_id,))

        # Commit cả 2 DB
        connections["mysql"].commit()
        connections["sqlserver"].commit()

        return {"success": True, "message": f"Đã xóa nhân viên {employee_id} trong MySQL + SQL Server"}

    except Exception as e:
        # Rollback khi lỗi
        for conn in connections.values():
            try:
                conn.rollback()
            except:
                pass
        return {"success": False, "message": f"Lỗi khi xóa nhân viên: {str(e)}"}

    finally:
        # Đóng kết nối
        for conn in connections.values():
            try:
                conn.close()
            except:
                pass

def get_employee_by_id(employee_id: int) -> Dict[str, Any]:
    """
    Lấy thông tin chi tiết nhân viên theo ID
    """
    vendor = get_db_vendor()
    placeholder = _placeholder(vendor)

    try:
        # Query lấy thông tin chi tiết nhân viên
        query = f"""
        SELECT 
            e.EmployeeID,
            e.FullName,
            e.Email,
            e.PhoneNumber,
            e.Status,
            e.DateOfBirth,
            e.HireDate,
            d.DepartmentID,
            d.DepartmentName,
            p.PositionID,
            p.PositionName,
            e.Gender
        FROM employees e
        JOIN departments d ON e.DepartmentID = d.DepartmentID
        JOIN positions p ON e.PositionID = p.PositionID
        WHERE e.EmployeeID = {placeholder}
        """

        employee_data = fetch_data_from_db(query, (employee_id,), vendor=vendor)
        
        if not employee_data:
            return {'success': False, 'message': f'Nhân viên ID {employee_id} không tồn tại'}

        employee = employee_data[0]
        
        # Lấy thông tin lương mới nhất từ MySQL
        salary_map = fetch_latest_salaries([employee_id])
        salary_info = salary_map.get(employee_id, {})

        # Format kết quả
        result = {
            'success': True,
            'employee': {
                'EmployeeID': employee.get('EmployeeID'),
                'FullName': employee.get('FullName'),
                'Email': employee.get('Email'),
                'PhoneNumber': employee.get('PhoneNumber'),
                'Status': employee.get('Status'),
                'DateOfBirth': employee.get('DateOfBirth').strftime('%Y-%m-%d') if employee.get('DateOfBirth') else None,
                'HireDate': employee.get('HireDate').strftime('%Y-%m-%d') if employee.get('HireDate') else None,
                'Department': {
                    'DepartmentID': employee.get('DepartmentID'),
                    'DepartmentName': employee.get('DepartmentName')
                },
                'Position': {
                    'PositionID': employee.get('PositionID'),
                    'PositionName': employee.get('PositionName')
                },              
                'Gender': employee.get('Gender'),
                'Salary': salary_info if salary_info else None
            }
        }

        return result

    except Exception as e:
        return {'success': False, 'message': f'Lỗi khi lấy thông tin nhân viên: {str(e)}'}
    
def update_employee_service(employee_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Cập nhật thông tin nhân viên trong cả 2 DB (SQL Server + MySQL)
    """
    vendors = ["sqlserver", "mysql"]
    connections = {}
    cursors = {}

    try:
        # Mở kết nối và bắt đầu transaction
        for v in vendors:
            conn = _get_connection(v)
            conn.autocommit = False
            connections[v] = conn
            cursors[v] = conn.cursor()

        # Kiểm tra nhân viên có tồn tại không
        cursor_sql = cursors["sqlserver"]
        placeholder_sql = _placeholder("sqlserver")
        
        check_sql = f"SELECT COUNT(*) FROM employees WHERE EmployeeID = {placeholder_sql}"
        cursor_sql.execute(check_sql, (employee_id,))
        count_sql = cursor_sql.fetchone()[0]
        
        if count_sql == 0:
            return {'success': False, 'message': f'Nhân viên ID {employee_id} không tồn tại'}

        # Extract data từ request
        full_name = data.get("FullName")
        department_id = data.get("DepartmentID")
        position_id = data.get("PositionID")
        status = data.get("Status")
        email = data.get("Email")
        phone_number = data.get("PhoneNumber")
        gender = data.get("Gender")
        
        # Xử lý DateOfBirth nếu có
        dob_str = data.get("DateOfBirth")
        date_of_birth = None
        if dob_str:
            date_of_birth = datetime.datetime.strptime(dob_str, "%Y-%m-%d").date()

        # --- CẬP NHẬT SQL SERVER ---
        update_fields_sql = []
        params_sql = []
        
        if full_name is not None:
            update_fields_sql.append(f"FullName = {placeholder_sql}")
            params_sql.append(full_name)
        if department_id is not None:
            update_fields_sql.append(f"DepartmentID = {placeholder_sql}")
            params_sql.append(department_id)
        if position_id is not None:
            update_fields_sql.append(f"PositionID = {placeholder_sql}")
            params_sql.append(position_id)
        if status is not None:
            update_fields_sql.append(f"Status = {placeholder_sql}")
            params_sql.append(status)
        if email is not None:
            update_fields_sql.append(f"Email = {placeholder_sql}")
            params_sql.append(email)
        if phone_number is not None:
            update_fields_sql.append(f"PhoneNumber = {placeholder_sql}")
            params_sql.append(phone_number)
        if date_of_birth is not None:
            update_fields_sql.append(f"DateOfBirth = {placeholder_sql}")
            params_sql.append(date_of_birth)
        if gender is not None:
            update_fields_sql.append(f"Gender = {placeholder_sql}")
            params_sql.append(gender)

        if update_fields_sql:
            update_sql = f"UPDATE employees SET {', '.join(update_fields_sql)} WHERE EmployeeID = {placeholder_sql}"
            params_sql.append(employee_id)
            cursor_sql.execute(update_sql, tuple(params_sql))

        # --- CẬP NHẬT MYSQL ---
        cursor_mysql = cursors["mysql"]
        placeholder_mysql = _placeholder("mysql")

        # Kiểm tra nhân viên có tồn tại trong MySQL không
        cursor_mysql.execute(f"SELECT COUNT(*) FROM employees WHERE EmployeeID = {placeholder_mysql}", (employee_id,))
        count_mysql = cursor_mysql.fetchone()[0]

        if count_mysql > 0:
            update_fields_mysql = []
            params_mysql = []
            
            if full_name is not None:
                update_fields_mysql.append(f"FullName = {placeholder_mysql}")
                params_mysql.append(full_name)
            if department_id is not None:
                update_fields_mysql.append(f"DepartmentID = {placeholder_mysql}")
                params_mysql.append(department_id)
            if position_id is not None:
                update_fields_mysql.append(f"PositionID = {placeholder_mysql}")
                params_mysql.append(position_id)
            if status is not None:
                update_fields_mysql.append(f"Status = {placeholder_mysql}")
                params_mysql.append(status)

            if update_fields_mysql:
                update_mysql = f"UPDATE employees SET {', '.join(update_fields_mysql)} WHERE EmployeeID = {placeholder_mysql}"
                params_mysql.append(employee_id)
                cursor_mysql.execute(update_mysql, tuple(params_mysql))

        # Commit cả 2 DB
        connections["sqlserver"].commit()
        connections["mysql"].commit()

        # Lấy thông tin nhân viên sau khi cập nhật
        updated_employee = get_employee_by_id(employee_id)
        if updated_employee.get('success'):
            return {
                'success': True, 
                'message': f'Cập nhật nhân viên ID {employee_id} thành công',
                'employee': updated_employee.get('employee')
            }
        else:
            return {
                'success': True, 
                'message': f'Cập nhật nhân viên ID {employee_id} thành công',
                'employee': None
            }

    except Exception as e:
        # Rollback cả 2 DB nếu lỗi
        for conn in connections.values():
            try:
                conn.rollback()
            except:
                pass
        return {'success': False, 'message': f'Lỗi khi cập nhật nhân viên: {str(e)}'}

    finally:
        # Đóng kết nối
        for conn in connections.values():
            try:
                conn.close()
            except:
                pass