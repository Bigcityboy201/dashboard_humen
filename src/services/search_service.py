from typing import Dict, Any, List
from config.sqlserver_connection import get_sqlserver_connection
from config.mysql_connection import get_mysql_connection
import os

def get_db_vendor() -> str:
	return os.environ.get("DB_VENDOR", "sqlserver").strip().lower()

def _get_connection(vendor: str):
	if vendor == "mysql":
		return get_mysql_connection()
	return get_sqlserver_connection()

def _placeholder(vendor: str) -> str:
	return "?" if vendor == "sqlserver" else "%s"

def fetch_data_from_db(sql_query: str, params: tuple, vendor: str | None = None) -> List[Dict[str, Any]]:
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

def search_all(keyword: str) -> Dict[str, Any]:
	"""
	Tìm kiếm toàn hệ thống
	"""
	vendor = get_db_vendor()
	placeholder = _placeholder(vendor)
	keyword_pattern = f"%{keyword}%"
	
	results = {
		"employees": [],
		"departments": [],
		"positions": [],
		"salaries": [],
		"attendance": []
	}
	
	# Tìm kiếm nhân viên
	employees_query = f"""
		SELECT e.EmployeeID, e.FullName, e.Email, e.PhoneNumber, 
		       d.DepartmentName, p.PositionName
		FROM employees e
		LEFT JOIN departments d ON e.DepartmentID = d.DepartmentID
		LEFT JOIN positions p ON e.PositionID = p.PositionID
		WHERE e.FullName LIKE {placeholder} 
		   OR e.Email LIKE {placeholder} 
		   OR e.PhoneNumber LIKE {placeholder}
		LIMIT 10
	""" if vendor == "mysql" else f"""
		SELECT TOP 10 e.EmployeeID, e.FullName, e.Email, e.PhoneNumber, 
		       d.DepartmentName, p.PositionName
		FROM employees e
		LEFT JOIN departments d ON e.DepartmentID = d.DepartmentID
		LEFT JOIN positions p ON e.PositionID = p.PositionID
		WHERE e.FullName LIKE {placeholder} 
		   OR e.Email LIKE {placeholder} 
		   OR e.PhoneNumber LIKE {placeholder}
	"""
	results["employees"] = fetch_data_from_db(employees_query, (keyword_pattern, keyword_pattern, keyword_pattern), vendor)
	
	# Tìm kiếm phòng ban
	departments_query = f"""
		SELECT DepartmentID, DepartmentName
		FROM departments
		WHERE DepartmentName LIKE {placeholder}
		LIMIT 10
	""" if vendor == "mysql" else f"""
		SELECT TOP 10 DepartmentID, DepartmentName
		FROM departments
		WHERE DepartmentName LIKE {placeholder}
	"""
	results["departments"] = fetch_data_from_db(departments_query, (keyword_pattern,), vendor)
	
	# Tìm kiếm chức vụ
	positions_query = f"""
		SELECT PositionID, PositionName
		FROM positions
		WHERE PositionName LIKE {placeholder}
		LIMIT 10
	""" if vendor == "mysql" else f"""
		SELECT TOP 10 PositionID, PositionName
		FROM positions
		WHERE PositionName LIKE {placeholder}
	"""
	results["positions"] = fetch_data_from_db(positions_query, (keyword_pattern,), vendor)
	
	# Tìm kiếm lương (theo tên nhân viên)
	salaries_query = f"""
		SELECT s.SalaryID, s.SalaryMonth, s.NetSalary, e.FullName
		FROM salaries s
		JOIN employees e ON s.EmployeeID = e.EmployeeID
		WHERE e.FullName LIKE {placeholder}
		ORDER BY s.SalaryMonth DESC
		LIMIT 10
	""" if vendor == "mysql" else f"""
		SELECT TOP 10 s.SalaryID, s.SalaryMonth, s.NetSalary, e.FullName
		FROM salaries s
		JOIN employees e ON s.EmployeeID = e.EmployeeID
		WHERE e.FullName LIKE {placeholder}
		ORDER BY s.SalaryMonth DESC
	"""
	results["salaries"] = fetch_data_from_db(salaries_query, (keyword_pattern,), vendor)
	
	# Tìm kiếm chấm công (theo tên nhân viên)
	attendance_query = f"""
		SELECT a.AttendanceID, a.AttendanceMonth, a.WorkDays, e.FullName
		FROM attendance a
		JOIN employees e ON a.EmployeeID = e.EmployeeID
		WHERE e.FullName LIKE {placeholder}
		ORDER BY a.AttendanceMonth DESC
		LIMIT 10
	""" if vendor == "mysql" else f"""
		SELECT TOP 10 a.AttendanceID, a.AttendanceMonth, a.WorkDays, e.FullName
		FROM attendance a
		JOIN employees e ON a.EmployeeID = e.EmployeeID
		WHERE e.FullName LIKE {placeholder}
		ORDER BY a.AttendanceMonth DESC
	"""
	results["attendance"] = fetch_data_from_db(attendance_query, (keyword_pattern,), vendor)
	
	return results





