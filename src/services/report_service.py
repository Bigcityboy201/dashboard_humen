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
		print(f"Error in fetch_data_from_db: {e}, Query: {sql_query}, Params: {params}")
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
		return float(row[0]) if row and row[0] is not None else 0.0
	except Exception as e:
		print(f"Error in fetch_scalar_from_db: {e}, Query: {sql_query}, Params: {params}")
		raise
	finally:
		if conn:
			conn.close()

def get_salary_report_by_year(year: str) -> Dict[str, Any]:
	"""
	Báo cáo lương theo năm
	"""
	vendor = get_salary_db_vendor()
	placeholder = _placeholder(vendor)
	
	# SalaryMonth là string (YYYY-MM), không phải date, nên dùng LIKE thay vì YEAR()
	year_pattern = f"{year}-%"
	
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
		WHERE SalaryMonth LIKE {placeholder}
		GROUP BY SalaryMonth
		ORDER BY SalaryMonth
	"""
	try:
		monthly_data = fetch_data_from_db(monthly_query, (year_pattern,), vendor)
	except Exception as e:
		print(f"Error fetching monthly salary data: {e}")
		monthly_data = []
	
	# Tổng lương cả năm
	total_query = f"""
		SELECT 
			SUM(NetSalary) as total_salary,
			COUNT(*) as total_records,
			AVG(NetSalary) as avg_salary
		FROM salaries
		WHERE SalaryMonth LIKE {placeholder}
	"""
	try:
		total_row = fetch_data_from_db(total_query, (year_pattern,), vendor)
		total_summary = total_row[0] if total_row else {}
	except Exception as e:
		print(f"Error fetching total salary summary: {e}")
		total_summary = {}
	
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
	
	# AttendanceMonth là string (YYYY-MM), không phải date, nên dùng LIKE thay vì YEAR()
	year_pattern = f"{year}-%"
	
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
		WHERE AttendanceMonth LIKE {placeholder}
		GROUP BY AttendanceMonth
		ORDER BY AttendanceMonth
	"""
	try:
		monthly_data = fetch_data_from_db(monthly_query, (year_pattern,), vendor)
	except Exception as e:
		print(f"Error fetching monthly attendance data: {e}")
		monthly_data = []
	
	# Tổng hợp cả năm
	total_query = f"""
		SELECT 
			COUNT(*) as total_records,
			SUM(WorkDays) as total_workdays,
			SUM(LeaveDays) as total_leavedays,
			SUM(AbsentDays) as total_absentdays,
			AVG(WorkDays) as avg_workdays
		FROM attendance
		WHERE AttendanceMonth LIKE {placeholder}
	"""
	try:
		total_row = fetch_data_from_db(total_query, (year_pattern,), vendor)
		total_summary = total_row[0] if total_row else {}
	except Exception as e:
		print(f"Error fetching total attendance summary: {e}")
		total_summary = {}
	
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
	
	# SalaryMonth là string (YYYY-MM), không phải date
	year_pattern = f"{year}-%"
	
	# Tổng lương năm
	salary_query = f"""
		SELECT SUM(NetSalary) as total_salary
		FROM salaries
		WHERE SalaryMonth LIKE {placeholder_salary}
	"""
	try:
		total_salary = fetch_scalar_from_db(salary_query, (year_pattern,), salary_vendor)
	except Exception as e:
		print(f"Error fetching total salary: {e}")
		total_salary = 0.0
	
	# Tổng cổ tức năm - DividendDate là date, có thể dùng YEAR()
	# Column name là DividendAmount, không phải Amount
	dividend_query = f"""
		SELECT SUM(DividendAmount) as total_dividends
		FROM dividends
		WHERE YEAR(DividendDate) = {placeholder}
	"""
	try:
		total_dividends = fetch_scalar_from_db(dividend_query, (year,), vendor)
	except Exception as e:
		print(f"Error fetching total dividends: {e}")
		total_dividends = 0.0
	
	# Chi tiết theo tháng
	monthly_salary_query = f"""
		SELECT 
			SalaryMonth as month,
			SUM(NetSalary) as salary_amount
		FROM salaries
		WHERE SalaryMonth LIKE {placeholder_salary}
		GROUP BY SalaryMonth
		ORDER BY SalaryMonth
	"""
	try:
		monthly_salary = fetch_data_from_db(monthly_salary_query, (year_pattern,), salary_vendor)
	except Exception as e:
		print(f"Error fetching monthly salary: {e}")
		monthly_salary = []
	
	# Chi tiết cổ tức theo tháng - Column name là DividendAmount
	monthly_dividend_query = f"""
		SELECT 
			FORMAT(DividendDate, 'yyyy-MM') as month,
			SUM(DividendAmount) as dividend_amount
		FROM dividends
		WHERE YEAR(DividendDate) = {placeholder}
		GROUP BY FORMAT(DividendDate, 'yyyy-MM')
		ORDER BY FORMAT(DividendDate, 'yyyy-MM')
	""" if vendor == "sqlserver" else f"""
		SELECT 
			DATE_FORMAT(DividendDate, '%%Y-%%m') as month,
			SUM(DividendAmount) as dividend_amount
		FROM dividends
		WHERE YEAR(DividendDate) = {placeholder}
		GROUP BY DATE_FORMAT(DividendDate, '%%Y-%%m')
		ORDER BY DATE_FORMAT(DividendDate, '%%Y-%%m')
	"""
	try:
		monthly_dividend = fetch_data_from_db(monthly_dividend_query, (year,), vendor)
	except Exception as e:
		print(f"Error fetching monthly dividend: {e}")
		monthly_dividend = []
	
	return {
		"year": year,
		"total_salary": total_salary,
		"total_dividends": total_dividends,
		"total_financial": total_salary + total_dividends,
		"monthly_salary": monthly_salary,
		"monthly_dividends": monthly_dividend
	}







