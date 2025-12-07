import os
from typing import Any, Dict, List, Tuple, Optional
from config.mysql_connection import get_mysql_connection

def get_salary_db_vendor() -> str:
    """Trả về vendor cho database salary"""
    return os.environ.get("SALARY_DB_VENDOR", "mysql").strip().lower()

def _placeholder(vendor: str) -> str:
    return "?" if vendor == "sqlserver" else "%s"

def fetch_data_from_db(sql_query: str, params: Tuple[Any, ...], vendor: str) -> List[Dict[str, Any]]:
    """Lấy danh sách records từ DB"""
    conn = None
    try:
        if vendor == "mysql":
            from config.mysql_connection import get_mysql_connection
            conn = get_mysql_connection()
        else:
            from config.sqlserver_connection import get_sqlserver_connection
            conn = get_sqlserver_connection()
            
        cursor = conn.cursor()
        cursor.execute(sql_query, params)
        columns = [col[0] for col in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]
    except Exception as e:
        raise Exception(f"Lỗi DB: {e}")
    finally:
        if conn:
            conn.close()

def execute_db(sql_query: str, params: Tuple[Any, ...], vendor: str) -> int:
    """Thực thi query và trả về rowcount"""
    conn = None
    try:
        if vendor == "mysql":
            from config.mysql_connection import get_mysql_connection
            conn = get_mysql_connection()
        else:
            from config.sqlserver_connection import get_sqlserver_connection
            conn = get_sqlserver_connection()
            
        cursor = conn.cursor()
        cursor.execute(sql_query, params)
        conn.commit()
        return cursor.rowcount
    except Exception as e:
        if conn:
            conn.rollback()
        raise Exception(f"Lỗi DB: {e}")
    finally:
        if conn:
            conn.close()

def get_salaries(employee_id: Optional[int] = None, salary_month: Optional[str] = None, year: Optional[int] = None) -> List[Dict[str, Any]]:
    """Lấy danh sách bản ghi lương với filter"""
    vendor = get_salary_db_vendor()
    placeholder = _placeholder(vendor)
    
    # Join với employees để lấy tên nhân viên
    query = f"""
    SELECT 
        s.SalaryID, 
        s.EmployeeID, 
        s.SalaryMonth, 
        s.BaseSalary AS BasicSalary,
        s.Bonus, 
        s.Deductions AS Deduction,
        s.NetSalary AS TotalSalary,
        s.CreatedAt,
        e.FullName AS EmployeeName
    FROM salaries s
    LEFT JOIN employees e ON s.EmployeeID = e.EmployeeID
    WHERE 1=1
    """
    params = []
    
    if employee_id:
        query += f" AND s.EmployeeID = {placeholder}"
        params.append(employee_id)
        
    if salary_month:
        query += f" AND s.SalaryMonth = {placeholder}"
        params.append(salary_month)
    elif year:
        # Filter theo năm: SalaryMonth LIKE 'YYYY-%'
        query += f" AND s.SalaryMonth LIKE {placeholder}"
        params.append(f"{year}-%")
        
    query += " ORDER BY s.SalaryMonth DESC, s.EmployeeID"
    
    return fetch_data_from_db(query, tuple(params), vendor)

def generate_salary(data: Dict[str, Any]) -> Dict[str, Any]:
    """Tạo/Tính lương cho một tháng"""
    vendor = get_salary_db_vendor()
    placeholder = _placeholder(vendor)
    
    # TODO: Implement logic tính lương từ attendance và employees
    # Hiện tại nhận dữ liệu trực tiếp từ request
    employee_id = data.get("EmployeeID")
    salary_month = data.get("SalaryMonth")
    base_salary = data.get("BaseSalary", 0.0)
    bonus = data.get("Bonus", 0.0)
    deductions = data.get("Deductions", 0.0)
    net_salary = base_salary + bonus - deductions
    
    query = f"""
    INSERT INTO salaries (EmployeeID, SalaryMonth, BaseSalary, Bonus, Deductions, NetSalary)
    VALUES ({placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder})
    """
    
    if vendor == "sqlserver":
        query += " OUTPUT INSERTED.SalaryID, INSERTED.EmployeeID, INSERTED.SalaryMonth, INSERTED.BaseSalary, INSERTED.Bonus, INSERTED.Deductions, INSERTED.NetSalary, INSERTED.CreatedAt"
        result = fetch_data_from_db(query, (employee_id, salary_month, base_salary, bonus, deductions, net_salary), vendor)
        return result[0] if result else {}
    else:
        # MySQL
        execute_db(query, (employee_id, salary_month, base_salary, bonus, deductions, net_salary), vendor)
        # Lấy bản ghi vừa tạo
        get_query = """
        SELECT SalaryID, EmployeeID, SalaryMonth, BaseSalary, Bonus, Deductions, NetSalary, CreatedAt
        FROM salaries 
        WHERE EmployeeID = %s AND SalaryMonth = %s
        ORDER BY SalaryID DESC LIMIT 1
        """
        result = fetch_data_from_db(get_query, (employee_id, salary_month), vendor)
        return result[0] if result else {}

def get_salary_by_id(salary_id: int) -> Optional[Dict[str, Any]]:
    """Lấy chi tiết bản ghi lương theo ID"""
    vendor = get_salary_db_vendor()
    placeholder = _placeholder(vendor)
    
    # Join với employees để lấy tên nhân viên
    query = f"""
    SELECT 
        s.SalaryID, 
        s.EmployeeID, 
        s.SalaryMonth, 
        s.BaseSalary AS BasicSalary,
        s.Bonus, 
        s.Deductions AS Deduction,
        s.NetSalary AS TotalSalary,
        s.CreatedAt,
        e.FullName AS EmployeeName
    FROM salaries s
    LEFT JOIN employees e ON s.EmployeeID = e.EmployeeID
    WHERE s.SalaryID = {placeholder}
    """
    
    result = fetch_data_from_db(query, (salary_id,), vendor)
    return result[0] if result else None

def update_salary(salary_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
    """Cập nhật bản ghi lương (Bonus/Deductions)"""
    vendor = get_salary_db_vendor()
    placeholder = _placeholder(vendor)
    
    # Chỉ cho phép cập nhật Bonus và Deductions
    bonus = data.get("Bonus")
    deductions = data.get("Deductions")
    
    if bonus is None and deductions is None:
        raise Exception("Cần cung cấp ít nhất một trường Bonus hoặc Deductions")
    
    # Lấy thông tin hiện tại
    current_salary = get_salary_by_id(salary_id)
    if not current_salary:
        raise Exception("Không tìm thấy bản ghi lương")
    
    # Tính toán NetSalary mới
    # Map field names: BasicSalary -> BaseSalary, Deduction -> Deductions
    base_salary = current_salary.get("BaseSalary") or current_salary.get("BasicSalary", 0)
    current_bonus = current_salary.get("Bonus", 0)
    current_deductions = current_salary.get("Deductions") or current_salary.get("Deduction", 0)
    
    new_bonus = bonus if bonus is not None else current_bonus
    new_deductions = deductions if deductions is not None else current_deductions
    new_net_salary = base_salary + new_bonus - new_deductions
    
    query = f"""
    UPDATE salaries 
    SET Bonus = {placeholder}, Deductions = {placeholder}, NetSalary = {placeholder}
    WHERE SalaryID = {placeholder}
    """
    
    execute_db(query, (new_bonus, new_deductions, new_net_salary, salary_id), vendor)
    
    # Trả về bản ghi đã cập nhật
    return get_salary_by_id(salary_id)

def delete_salary(salary_id: int) -> Dict[str, Any]:
    """Xóa bản ghi lương"""
    vendor = get_salary_db_vendor()
    placeholder = _placeholder(vendor)
    
    # Lấy thông tin trước khi xóa
    salary_record = get_salary_by_id(salary_id)
    if not salary_record:
        raise Exception("Không tìm thấy bản ghi lương")
    
    query = f"DELETE FROM salaries WHERE SalaryID = {placeholder}"
    rowcount = execute_db(query, (salary_id,), vendor)
    
    if rowcount == 0:
        raise Exception("Không tìm thấy bản ghi lương để xóa")
    
    return {
        "message": f"Salary record with ID {salary_id} deleted successfully",
        "deleted_record": salary_record
    }

def get_my_salaries(employee_id: int) -> List[Dict[str, Any]]:
    """Lấy lịch sử lương của nhân viên"""
    vendor = get_salary_db_vendor()
    placeholder = _placeholder(vendor)
    
    query = f"""
    SELECT SalaryID, EmployeeID, SalaryMonth, BaseSalary, Bonus, Deductions, NetSalary, CreatedAt
    FROM salaries 
    WHERE EmployeeID = {placeholder}
    ORDER BY SalaryMonth DESC
    """
    
    return fetch_data_from_db(query, (employee_id,), vendor)

def get_salary_statistics(salary_month: Optional[str] = None, year: Optional[int] = None) -> Dict[str, Any]:
    """Thống kê tổng chi phí lương theo tháng hoặc năm"""
    vendor = get_salary_db_vendor()
    placeholder = _placeholder(vendor)
    
    if salary_month:
        # Thống kê theo tháng cụ thể
        query = f"""
        SELECT 
            COUNT(*) as total_records,
            SUM(BaseSalary) as total_base_salary,
            SUM(Bonus) as total_bonus,
            SUM(Deductions) as total_deductions,
            SUM(NetSalary) as total_amount
        FROM salaries 
        WHERE SalaryMonth = {placeholder}
        """
        params = (salary_month,)
    elif year:
        # Thống kê theo năm
        query = f"""
        SELECT 
            COUNT(*) as total_records,
            SUM(BaseSalary) as total_base_salary,
            SUM(Bonus) as total_bonus,
            SUM(Deductions) as total_deductions,
            SUM(NetSalary) as total_amount
        FROM salaries 
        WHERE SalaryMonth LIKE {placeholder}
        """
        params = (f"{year}-%",)
    else:
        # Thống kê tổng quát
        query = """
        SELECT 
            COUNT(*) as total_records,
            SUM(BaseSalary) as total_base_salary,
            SUM(Bonus) as total_bonus,
            SUM(Deductions) as total_deductions,
            SUM(NetSalary) as total_amount
        FROM salaries
        """
        params = ()
    
    result = fetch_data_from_db(query, params, vendor)
    stats = result[0] if result else {}
    
    return {
        "year": year,
        "month": salary_month,
        "total_records": int(stats.get("total_records", 0)),
        "total_base_salary": float(stats.get("total_base_salary", 0) or 0),
        "total_bonus": float(stats.get("total_bonus", 0) or 0),
        "total_deductions": float(stats.get("total_deductions", 0) or 0),
        "total_amount": float(stats.get("total_amount", 0) or 0)
    }