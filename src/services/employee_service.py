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
  	e.HireDate,
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
      		"HireDate": row.get("HireDate").strftime("%Y-%m-%d") if row.get("HireDate") else None,
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
            "HireDate": hire_date.strftime("%Y-%m-%d"),
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
