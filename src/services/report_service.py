from typing import Dict, Any, List
from config.sqlserver_connection import get_sqlserver_connection
from config.mysql_connection import get_mysql_connection
import os

def get_db_vendor() -> str:
	return os.environ.get("DB_VENDOR", "sqlserver").strip().lower()

def get_salary_db_vendor() -> str:
	return os.environ.get("SALARY_DB_VENDOR", get_db_vendor()).strip().lower()

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

def fetch_scalar_from_db(sql_query: str, params: tuple, vendor: str | None = None) -> float:
	conn = None
	actual_vendor = vendor or get_db_vendor()
	try:
		conn = _get_connection(actual_vendor)
		db_cursor = conn.cursor()
		db_cursor.execute(sql_query, params)
		row = db_cursor.fetchone()
		return float(row[0]) if row and row[0] else 0.0
	finally:
		if conn:
			conn.close()

def get_salary_report_by_year(year: str) -> Dict[str, Any]:
	"""
	Báo cáo lương theo năm
	"""
	vendor = get_salary_db_vendor()
	placeholder = _placeholder(vendor)
	
	# Lấy tổng lương theo từng tháng
	monthly_query = f"""
		SELECT 
			SalaryMonth,
			COUNT(*) as total_records,
			SUM(NetSalary) as total_salary,
			AVG(NetSalary) as avg_salary,
			MIN(NetSalary) as min_salary,
			MAX(NetSalary) as max_salary
		FROM salaries
		WHERE YEAR(SalaryMonth) = {placeholder}
		GROUP BY SalaryMonth
		ORDER BY SalaryMonth
	"""
	monthly_data = fetch_data_from_db(monthly_query, (year,), vendor)
	
	# Tổng lương cả năm
	total_query = f"""
		SELECT 
			SUM(NetSalary) as total_salary,
			COUNT(*) as total_records,
			AVG(NetSalary) as avg_salary
		FROM salaries
		WHERE YEAR(SalaryMonth) = {placeholder}
	"""
	total_row = fetch_data_from_db(total_query, (year,), vendor)
	total_summary = total_row[0] if total_row else {}
	
	return {
		"year": year,
		"monthly_breakdown": monthly_data,
		"yearly_summary": total_summary
	}

def get_attendance_report_by_year(year: str) -> Dict[str, Any]:
	"""
	Báo cáo chấm công theo năm
	"""
	vendor = get_db_vendor()
	placeholder = _placeholder(vendor)
	
	# Lấy thống kê theo từng tháng
	monthly_query = f"""
		SELECT 
			AttendanceMonth,
			COUNT(*) as total_records,
			SUM(WorkDays) as total_workdays,
			SUM(LeaveDays) as total_leavedays,
			SUM(AbsentDays) as total_absentdays,
			AVG(WorkDays) as avg_workdays
		FROM attendance
		WHERE YEAR(AttendanceMonth) = {placeholder}
		GROUP BY AttendanceMonth
		ORDER BY AttendanceMonth
	"""
	monthly_data = fetch_data_from_db(monthly_query, (year,), vendor)
	
	# Tổng hợp cả năm
	total_query = f"""
		SELECT 
			COUNT(*) as total_records,
			SUM(WorkDays) as total_workdays,
			SUM(LeaveDays) as total_leavedays,
			SUM(AbsentDays) as total_absentdays,
			AVG(WorkDays) as avg_workdays
		FROM attendance
		WHERE YEAR(AttendanceMonth) = {placeholder}
	"""
	total_row = fetch_data_from_db(total_query, (year,), vendor)
	total_summary = total_row[0] if total_row else {}
	
	return {
		"year": year,
		"monthly_breakdown": monthly_data,
		"yearly_summary": total_summary
	}

def get_financial_report(year: str) -> Dict[str, Any]:
	"""
	Báo cáo tài chính tổng hợp (lương + cổ tức) theo năm
	"""
	salary_vendor = get_salary_db_vendor()
	vendor = get_db_vendor()
	placeholder_salary = _placeholder(salary_vendor)
	placeholder = _placeholder(vendor)
	
	# Tổng lương năm
	salary_query = f"""
		SELECT SUM(NetSalary) as total_salary
		FROM salaries
		WHERE YEAR(SalaryMonth) = {placeholder_salary}
	"""
	total_salary = fetch_scalar_from_db(salary_query, (year,), salary_vendor)
	
	# Tổng cổ tức năm
	dividend_query = f"""
		SELECT SUM(Amount) as total_dividends
		FROM dividends
		WHERE YEAR(DividendDate) = {placeholder}
	"""
	total_dividends = fetch_scalar_from_db(dividend_query, (year,), vendor)
	
	# Chi tiết theo tháng
	monthly_salary_query = f"""
		SELECT 
			SalaryMonth as month,
			SUM(NetSalary) as salary_amount
		FROM salaries
		WHERE YEAR(SalaryMonth) = {placeholder_salary}
		GROUP BY SalaryMonth
		ORDER BY SalaryMonth
	"""
	monthly_salary = fetch_data_from_db(monthly_salary_query, (year,), salary_vendor)
	
	monthly_dividend_query = f"""
		SELECT 
			FORMAT(DividendDate, 'yyyy-MM') as month,
			SUM(Amount) as dividend_amount
		FROM dividends
		WHERE YEAR(DividendDate) = {placeholder}
		GROUP BY FORMAT(DividendDate, 'yyyy-MM')
		ORDER BY FORMAT(DividendDate, 'yyyy-MM')
	""" if vendor == "sqlserver" else f"""
		SELECT 
			DATE_FORMAT(DividendDate, '%%Y-%%m') as month,
			SUM(Amount) as dividend_amount
		FROM dividends
		WHERE YEAR(DividendDate) = {placeholder}
		GROUP BY DATE_FORMAT(DividendDate, '%%Y-%%m')
		ORDER BY DATE_FORMAT(DividendDate, '%%Y-%%m')
	"""
	monthly_dividend = fetch_data_from_db(monthly_dividend_query, (year,), vendor)
	
	return {
		"year": year,
		"total_salary": total_salary,
		"total_dividends": total_dividends,
		"total_financial": total_salary + total_dividends,
		"monthly_salary": monthly_salary,
		"monthly_dividends": monthly_dividend
	}





