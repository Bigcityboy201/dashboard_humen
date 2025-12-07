from typing import Dict, Any
from config.sqlserver_connection import get_sqlserver_connection
from config.mysql_connection import get_mysql_connection
import os
from datetime import datetime

def get_db_vendor() -> str:
	return os.environ.get("DB_VENDOR", "sqlserver").strip().lower()

def _get_connection(vendor: str):
	if vendor == "mysql":
		return get_mysql_connection()
	return get_sqlserver_connection()

def _placeholder(vendor: str) -> str:
	return "?" if vendor == "sqlserver" else "%s"

def fetch_scalar_from_db(sql_query: str, params: tuple, vendor: str | None = None) -> int:
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

def get_dashboard_overview() -> Dict[str, Any]:
	"""
	Lấy thống kê tổng hợp cho dashboard
	"""
	vendor = get_db_vendor()
	placeholder = _placeholder(vendor)
	
	# Tổng số nhân viên
	total_employees_query = "SELECT COUNT(*) FROM employees"
	total_employees = fetch_scalar_from_db(total_employees_query, (), vendor)
	
	# Tổng số phòng ban
	total_departments_query = "SELECT COUNT(*) FROM departments"
	total_departments = fetch_scalar_from_db(total_departments_query, (), vendor)
	
	# Tổng số chức vụ
	total_positions_query = "SELECT COUNT(*) FROM positions"
	total_positions = fetch_scalar_from_db(total_positions_query, (), vendor)
	
	# Tổng lương tháng hiện tại
	current_month = datetime.now().strftime("%Y-%m")
	total_salary_query = f"""
		SELECT COALESCE(SUM(NetSalary), 0) 
		FROM salaries 
		WHERE SalaryMonth = {placeholder}
	"""
	total_salary = fetch_scalar_from_db(total_salary_query, (current_month,), vendor)
	
	# Tổng số ngày công tháng hiện tại
	total_workdays_query = f"""
		SELECT COALESCE(SUM(WorkDays), 0) 
		FROM attendance 
		WHERE AttendanceMonth = {placeholder}
	"""
	total_workdays = fetch_scalar_from_db(total_workdays_query, (current_month,), vendor)
	
	# Tổng số nhân viên đang làm việc
	active_employees_query = f"SELECT COUNT(*) FROM employees WHERE Status = {placeholder}"
	active_employees = fetch_scalar_from_db(active_employees_query, ("Đang làm việc",), vendor)
	
	# Tổng cổ tức năm hiện tại
	current_year = datetime.now().strftime("%Y")
	total_dividends_query = f"""
		SELECT COALESCE(SUM(Amount), 0) 
		FROM dividends 
		WHERE YEAR(DividendDate) = {placeholder}
	"""
	total_dividends = fetch_scalar_from_db(total_dividends_query, (current_year,), vendor)
	
	return {
		"total_employees": total_employees,
		"total_departments": total_departments,
		"total_positions": total_positions,
		"active_employees": active_employees,
		"current_month": current_month,
		"current_year": current_year,
		"total_salary_current_month": total_salary,
		"total_workdays_current_month": total_workdays,
		"total_dividends_current_year": total_dividends
	}

