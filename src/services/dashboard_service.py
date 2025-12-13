from typing import Dict, Any, List
from config.sqlserver_connection import get_sqlserver_connection
from config.mysql_connection import get_mysql_connection
import os
import logging
import calendar
from datetime import datetime, timedelta

def get_db_vendor() -> str:
	return os.environ.get("DB_VENDOR", "sqlserver").strip().lower()

def get_salary_db_vendor() -> str:
	"""Trả về vendor cho database salary"""
	return os.environ.get("SALARY_DB_VENDOR", "mysql").strip().lower()

def get_attendance_db_vendor() -> str:
	"""Trả về vendor cho database attendance"""
	return os.environ.get("ATTENDANCE_DB_VENDOR", "mysql").strip().lower()

def _get_connection(vendor: str):
	if vendor == "mysql":
		return get_mysql_connection()
	return get_sqlserver_connection()

def _placeholder(vendor: str) -> str:
	return "?" if vendor == "sqlserver" else "%s"

def _get_previous_month(date: datetime) -> datetime:
	"""Tính tháng trước của một ngày, không cần dateutil"""
	first_day = date.replace(day=1)
	prev_month = first_day - timedelta(days=1)
	return prev_month.replace(day=1)

def _get_months_ago(date: datetime, months: int) -> datetime:
	"""Tính N tháng trước của một ngày"""
	result = date
	for _ in range(months):
		result = _get_previous_month(result)
	return result

def _get_last_day_of_month(year_month: str) -> str:
	"""
	Tính ngày cuối cùng của tháng từ string YYYY-MM
	Ví dụ: '2025-11' -> '2025-11-30', '2025-02' -> '2025-02-28'
	"""
	try:
		year, month = year_month.split("-")
		year_int = int(year)
		month_int = int(month)
		# Sử dụng calendar.monthrange để lấy số ngày trong tháng
		last_day = calendar.monthrange(year_int, month_int)[1]
		# Format đúng: month đã là string, cần convert sang int rồi format lại
		return f"{year_int:04d}-{month_int:02d}-{last_day:02d}"
	except Exception as e:
		logging.error(f"Error calculating last day for {year_month}: {e}", exc_info=True)
		# Fallback: trả về ngày 28 (an toàn cho mọi tháng)
		return f"{year_month}-28"

def fetch_scalar_from_db(sql_query: str, params: tuple, vendor: str | None = None, return_float: bool = False) -> int | float:
	conn = None
	actual_vendor = vendor or get_db_vendor()
	try:
		conn = _get_connection(actual_vendor)
		db_cursor = conn.cursor()
		db_cursor.execute(sql_query, params)
		row = db_cursor.fetchone()
		if return_float:
			return float(row[0]) if row and row[0] is not None else 0.0
		return int(row[0]) if row and row[0] is not None else 0
	except Exception as e:
		print(f"Error in fetch_scalar_from_db: {e}, Query: {sql_query}, Params: {params}")
		raise
	finally:
		if conn:
			conn.close()

def fetch_data_from_db(sql_query: str, params: tuple, vendor: str | None = None) -> List[Dict[str, Any]]:
	"""Fetch multiple rows from database"""
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
		raise
	finally:
		if conn:
			conn.close()

def get_dashboard_overview() -> Dict[str, Any]:
	"""
	Lấy thống kê tổng hợp cho dashboard
	"""
	vendor = get_db_vendor()
	placeholder = _placeholder(vendor)
	
	try:
		# Tổng số nhân viên
		total_employees_query = "SELECT COUNT(*) FROM employees"
		total_employees = fetch_scalar_from_db(total_employees_query, (), vendor)
	except Exception as e:
		print(f"Error fetching total employees: {e}")
		total_employees = 0
	
	try:
		# Tổng số phòng ban
		total_departments_query = "SELECT COUNT(*) FROM departments"
		total_departments = fetch_scalar_from_db(total_departments_query, (), vendor)
	except Exception as e:
		print(f"Error fetching total departments: {e}")
		total_departments = 0
	
	try:
		# Tổng số chức vụ
		total_positions_query = "SELECT COUNT(*) FROM positions"
		total_positions = fetch_scalar_from_db(total_positions_query, (), vendor)
	except Exception as e:
		print(f"Error fetching total positions: {e}")
		total_positions = 0
	
	# Tổng lương tháng hiện tại
	# SalaryMonth là STRING (YYYY-MM), dùng LIKE
	# Dùng salary_db_vendor vì salaries có thể ở database khác
	salary_vendor = get_salary_db_vendor()
	salary_placeholder = _placeholder(salary_vendor)
	current_month = datetime.now().strftime("%Y-%m")
	current_month_pattern = f"{current_month}-%"
	total_salary_query = f"""
		SELECT COALESCE(SUM(NetSalary), 0) 
		FROM salaries 
		WHERE SalaryMonth LIKE {salary_placeholder}
	"""
	try:
		total_salary = fetch_scalar_from_db(total_salary_query, (current_month_pattern,), salary_vendor, return_float=True)
	except Exception as e:
		print(f"Error fetching total salary: {e}")
		total_salary = 0.0
	
	# Tổng số ngày công tháng hiện tại
	# AttendanceMonth có thể là DATE hoặc STRING, dùng LIKE
	# Dùng attendance_db_vendor vì attendance có thể ở database khác
	attendance_vendor = get_attendance_db_vendor()
	attendance_placeholder = _placeholder(attendance_vendor)
	total_workdays_query = f"""
		SELECT COALESCE(SUM(WorkDays), 0) 
		FROM attendance 
		WHERE AttendanceMonth LIKE {attendance_placeholder}
	"""
	try:
		total_workdays = fetch_scalar_from_db(total_workdays_query, (current_month_pattern,), attendance_vendor)
	except Exception as e:
		print(f"Error fetching total workdays: {e}")
		total_workdays = 0
	
	# Tổng số nhân viên đang làm việc
	active_employees_query = f"SELECT COUNT(*) FROM employees WHERE Status = {placeholder}"
	try:
		active_employees = fetch_scalar_from_db(active_employees_query, ("Đang làm việc",), vendor)
	except Exception as e:
		print(f"Error fetching active employees: {e}")
		active_employees = 0
	
	# Tổng cổ tức năm hiện tại
	current_year = datetime.now().strftime("%Y")
	# Xử lý khác nhau cho SQL Server và MySQL
	if vendor == "sqlserver":
		total_dividends_query = f"""
			SELECT COALESCE(SUM(DividendAmount), 0) 
			FROM dividends 
			WHERE YEAR(DividendDate) = {placeholder}
		"""
	else:
		total_dividends_query = f"""
			SELECT COALESCE(SUM(DividendAmount), 0) 
			FROM dividends 
			WHERE YEAR(DividendDate) = {placeholder}
		"""
	try:
		total_dividends = fetch_scalar_from_db(total_dividends_query, (current_year,), vendor, return_float=True)
	except Exception as e:
		print(f"Error fetching total dividends: {e}")
		total_dividends = 0.0
	
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

def get_dashboard_comparison() -> Dict[str, Any]:
    """
    So sánh dữ liệu hiện tại với kỳ trước (tháng trước, năm trước)
    """
    vendor = get_db_vendor()
    placeholder = _placeholder(vendor)
    
    current_month = datetime.now().strftime("%Y-%m")
    current_year = datetime.now().strftime("%Y")
    prev_month_date = _get_previous_month(datetime.now()).strftime("%Y-%m")
    prev_year = str(int(current_year) - 1)
    
    result = {}

    # So sánh tổng nhân viên
    try:
        current_employees = fetch_scalar_from_db(
            "SELECT COUNT(*) FROM employees", (), vendor
        )

        prev_query = "SELECT COUNT(*) FROM employees WHERE HireDate <= ?"
        if vendor == "mysql":
            prev_query = "SELECT COUNT(*) FROM employees WHERE HireDate <= %s"

        # Tính ngày cuối cùng của tháng trước (không phải cố định -31)
        prev_month_end = _get_last_day_of_month(prev_month_date)
        prev_month_employees = fetch_scalar_from_db(
            prev_query,
            (prev_month_end,),
            vendor
        )

        employee_change = current_employees - prev_month_employees
        if prev_month_employees == 0 and current_employees > 0:
            employee_change_percentage = None
        else:
            employee_change_percentage = (employee_change / prev_month_employees * 100) if prev_month_employees > 0 else 0

        result["total_employees_change"] = {
            "value": employee_change,
            "percentage": round(employee_change_percentage, 2) if employee_change_percentage is not None else None,
            "trend": "up" if employee_change > 0 else "down" if employee_change < 0 else "stable"
        }

    except Exception as e:
        logging.error(f"Error calculating employee comparison: {e}")
        result["total_employees_change"] = {"value": 0, "percentage": 0, "trend": "stable"}

    # So sánh lương tháng hiện tại vs tháng trước
    try:
        # SalaryMonth là STRING, dùng LIKE
        # Dùng salary_db_vendor vì salaries có thể ở database khác
        salary_vendor = get_salary_db_vendor()
        salary_placeholder = _placeholder(salary_vendor)
        current_month_pattern = f"{current_month}-%"
        prev_month_pattern = f"{prev_month_date}-%"
        query = f"SELECT COALESCE(SUM(NetSalary), 0) FROM salaries WHERE SalaryMonth LIKE {salary_placeholder}"

        current_salary = fetch_scalar_from_db(query, (current_month_pattern,), salary_vendor, return_float=True)
        prev_salary = fetch_scalar_from_db(query, (prev_month_pattern,), salary_vendor, return_float=True)

        salary_change = current_salary - prev_salary
        if prev_salary == 0 and current_salary > 0:
            salary_change_percentage = None
        else:
            salary_change_percentage = (salary_change / prev_salary * 100) if prev_salary > 0 else 0

        result["total_salary_change"] = {
            "value": round(salary_change, 2),
            "percentage": round(salary_change_percentage, 2) if salary_change_percentage is not None else None,
            "trend": "up" if salary_change > 0 else "down" if salary_change < 0 else "stable",
            "current": round(current_salary, 2),
            "previous": round(prev_salary, 2)
        }

    except Exception as e:
        logging.error(f"Error calculating salary comparison: {e}")
        result["total_salary_change"] = {"value": 0, "percentage": 0, "trend": "stable", "current": 0, "previous": 0}

    # So sánh ngày công
    try:
        # AttendanceMonth có thể là DATE hoặc STRING, dùng LIKE
        # Dùng attendance_db_vendor vì attendance có thể ở database khác
        attendance_vendor = get_attendance_db_vendor()
        attendance_placeholder = _placeholder(attendance_vendor)
        current_month_pattern = f"{current_month}-%"
        prev_month_pattern = f"{prev_month_date}-%"
        query = f"SELECT COALESCE(SUM(WorkDays), 0) FROM attendance WHERE AttendanceMonth LIKE {attendance_placeholder}"

        current_workdays = fetch_scalar_from_db(query, (current_month_pattern,), attendance_vendor)
        prev_workdays = fetch_scalar_from_db(query, (prev_month_pattern,), attendance_vendor)

        workdays_change = current_workdays - prev_workdays
        if prev_workdays == 0 and current_workdays > 0:
            workdays_change_percentage = None
        else:
            workdays_change_percentage = (workdays_change / prev_workdays * 100) if prev_workdays > 0 else 0

        result["total_workdays_change"] = {
            "value": workdays_change,
            "percentage": round(workdays_change_percentage, 2) if workdays_change_percentage is not None else None,
            "trend": "up" if workdays_change > 0 else "down" if workdays_change < 0 else "stable"
        }

    except Exception as e:
        logging.error(f"Error calculating workdays comparison: {e}")
        result["total_workdays_change"] = {"value": 0, "percentage": 0, "trend": "stable"}

    # So sánh cổ tức năm hiện tại vs năm trước
    try:
        query = f"SELECT COALESCE(SUM(DividendAmount), 0) FROM dividends WHERE YEAR(DividendDate) = {placeholder}"

        current_dividends = fetch_scalar_from_db(query, (current_year,), vendor, return_float=True)
        prev_dividends = fetch_scalar_from_db(query, (prev_year,), vendor, return_float=True)

        dividends_change = current_dividends - prev_dividends
        if prev_dividends == 0 and current_dividends > 0:
            dividends_change_percentage = None
        else:
            dividends_change_percentage = (dividends_change / prev_dividends * 100) if prev_dividends > 0 else 0

        result["total_dividends_change"] = {
            "value": round(dividends_change, 2),
            "percentage": round(dividends_change_percentage, 2) if dividends_change_percentage is not None else None,
            "trend": "up" if dividends_change > 0 else "down" if dividends_change < 0 else "stable"
        }

    except Exception as e:
        logging.error(f"Error calculating dividends comparison: {e}")
        result["total_dividends_change"] = {"value": 0, "percentage": 0, "trend": "stable"}

    return result

def get_top_employees(limit: int = 5) -> List[Dict[str, Any]]:
	"""
	Lấy top employees mới nhất (sắp xếp theo HireDate)
	"""
	vendor = get_db_vendor()
	placeholder = _placeholder(vendor)
	
	try:
		query = f"""
			SELECT TOP {limit if vendor == "sqlserver" else ""}
				e.EmployeeID,
				e.FullName,
				e.HireDate,
				e.Email,
				e.PhoneNumber,
				e.Status,
				COALESCE(d.DepartmentName, '') AS DepartmentName,
				COALESCE(p.PositionName, '') AS PositionName
			FROM employees e
			LEFT JOIN departments d ON e.DepartmentID = d.DepartmentID
			LEFT JOIN positions p ON e.PositionID = p.PositionID
			ORDER BY e.HireDate DESC
		"""
		if vendor == "mysql":
			query = f"""
				SELECT 
					e.EmployeeID,
					e.FullName,
					e.HireDate,
					e.Email,
					e.PhoneNumber,
					e.Status,
					COALESCE(d.DepartmentName, '') AS DepartmentName,
					COALESCE(p.PositionName, '') AS PositionName
				FROM employees e
				LEFT JOIN departments d ON e.DepartmentID = d.DepartmentID
				LEFT JOIN positions p ON e.PositionID = p.PositionID
				ORDER BY e.HireDate DESC
				LIMIT {limit}
			"""
		
		rows = fetch_data_from_db(query, (), vendor)
		
		result = []
		for row in rows:
			result.append({
				"EmployeeID": row.get("EmployeeID"),
				"FullName": row.get("FullName"),
				"HireDate": row.get("HireDate").strftime("%Y-%m-%d") if row.get("HireDate") else None,
				"Email": row.get("Email"),
				"PhoneNumber": row.get("PhoneNumber"),
				"Status": row.get("Status"),
				"DepartmentName": row.get("DepartmentName"),
				"PositionName": row.get("PositionName")
			})
		
		return result
	except Exception as e:
		print(f"Error fetching top employees: {e}")
		return []

def get_top_departments(limit: int = 5) -> List[Dict[str, Any]]:
	"""
	Lấy top departments có nhiều nhân viên nhất
	"""
	vendor = get_db_vendor()
	placeholder = _placeholder(vendor)
	
	try:
		query = f"""
			SELECT TOP {limit if vendor == "sqlserver" else ""}
				d.DepartmentID,
				d.DepartmentName,
				COUNT(e.EmployeeID) AS EmployeeCount
			FROM departments d
			LEFT JOIN employees e ON d.DepartmentID = e.DepartmentID
			GROUP BY d.DepartmentID, d.DepartmentName
			ORDER BY EmployeeCount DESC
		"""
		if vendor == "mysql":
			query = f"""
				SELECT 
					d.DepartmentID,
					d.DepartmentName,
					COUNT(e.EmployeeID) AS EmployeeCount
				FROM departments d
				LEFT JOIN employees e ON d.DepartmentID = e.DepartmentID
				GROUP BY d.DepartmentID, d.DepartmentName
				ORDER BY EmployeeCount DESC
				LIMIT {limit}
			"""
		
		rows = fetch_data_from_db(query, (), vendor)
		
		result = []
		for row in rows:
			result.append({
				"DepartmentID": row.get("DepartmentID"),
				"DepartmentName": row.get("DepartmentName"),
				"EmployeeCount": row.get("EmployeeCount") or 0
			})
		
		return result
	except Exception as e:
		print(f"Error fetching top departments: {e}")
		return []

def get_dashboard_trends(months: int = 6) -> Dict[str, Any]:
	"""
	Lấy xu hướng dữ liệu trong N tháng gần đây
	"""
	vendor = get_db_vendor()
	placeholder = _placeholder(vendor)
	
	result = {
		"employee_trend": [],
		"salary_trend": [],
		"workdays_trend": []
	}
	
	try:
		# Lấy các tháng có dữ liệu gần đây nhất từ database
		# Thay vì tính từ tháng hiện tại, lấy các tháng thực tế có dữ liệu
		# Dùng salary_db_vendor vì salaries có thể ở database khác
		salary_vendor = get_salary_db_vendor()
		months_list = []
		try:
			if salary_vendor == "sqlserver":
				# SQL Server: Lấy các tháng có dữ liệu salary, extract YYYY-MM từ YYYY-MM-DD
				# Thử LEFT trực tiếp (nếu là string) hoặc CONVERT (nếu là DATE)
				# Nếu lỗi, sẽ fallback về cách tính tháng
				try:
					months_query = f"""
						SELECT DISTINCT TOP {months}
							LEFT(SalaryMonth, 7) AS MonthKey
						FROM salaries
						WHERE SalaryMonth IS NOT NULL
						ORDER BY MonthKey DESC
					"""
					existing_months_data = fetch_data_from_db(months_query, (), salary_vendor)
				except:
					# Fallback: thử CONVERT nếu LEFT không work
					months_query = f"""
						SELECT DISTINCT TOP {months}
							LEFT(CONVERT(VARCHAR(10), SalaryMonth, 120), 7) AS MonthKey
						FROM salaries
						WHERE SalaryMonth IS NOT NULL
						ORDER BY MonthKey DESC
					"""
					existing_months_data = fetch_data_from_db(months_query, (), salary_vendor)
			else:
				# MySQL: Lấy các tháng có dữ liệu salary, extract YYYY-MM từ YYYY-MM-DD
				months_query = f"""
					SELECT DISTINCT
						LEFT(SalaryMonth, 7) AS MonthKey
					FROM salaries
					WHERE SalaryMonth IS NOT NULL
					ORDER BY MonthKey DESC
					LIMIT {months}
				"""
				existing_months_data = fetch_data_from_db(months_query, (), salary_vendor)
			
			months_list = [m.get('MonthKey') or m.get('monthkey') for m in existing_months_data if m.get('MonthKey') or m.get('monthkey')]
			months_list.reverse()  # Từ cũ đến mới
			logging.info(f"Found {len(months_list)} months with salary data: {months_list}")
		except Exception as e:
			logging.warning(f"Could not fetch months from database, using calculated months: {e}")
			# Fallback: Tính các tháng gần đây từ tháng hiện tại
			current_date = datetime.now()
			logging.info(f"Current date: {current_date.strftime('%Y-%m-%d')}")
			for i in range(months):
				month_date = _get_months_ago(current_date, i)
				month_str = month_date.strftime("%Y-%m")
				months_list.append(month_str)
			months_list.reverse()
			logging.info(f"Using calculated months (oldest to newest): {months_list}")
		
		# Employee trend - đếm số nhân viên đến cuối mỗi tháng
		employee_trend = []
		for month in months_list:
			try:
				# Tính ngày cuối cùng của tháng (không phải cố định -31)
				month_end = _get_last_day_of_month(month)
				query = f"SELECT COUNT(*) FROM employees WHERE HireDate <= {placeholder}"
				if vendor == "mysql":
					query = f"SELECT COUNT(*) FROM employees WHERE HireDate <= %s"
				count = fetch_scalar_from_db(query, (month_end,), vendor)
				logging.info(f"Employee trend for {month} (end date: {month_end}): {count}")
				employee_trend.append({
					"month": month,
					"count": count
				})
			except Exception as e:
				logging.error(f"Error fetching employee trend for {month}: {e}", exc_info=True)
				employee_trend.append({
					"month": month,
					"count": 0
				})
		result["employee_trend"] = employee_trend
		
		# Debug: Lấy danh sách các SalaryMonth có trong database
		try:
			if salary_vendor == "sqlserver":
				debug_query = "SELECT DISTINCT TOP 20 SalaryMonth FROM salaries ORDER BY SalaryMonth DESC"
			else:
				debug_query = "SELECT DISTINCT SalaryMonth FROM salaries ORDER BY SalaryMonth DESC LIMIT 20"
			existing_months = fetch_data_from_db(debug_query, (), salary_vendor)
			logging.info(f"Existing SalaryMonth values in database: {[m.get('SalaryMonth') for m in existing_months]}")
		except Exception as e:
			logging.warning(f"Could not fetch existing SalaryMonth values: {e}")
		
		# Salary trend - tổng lương mỗi tháng
		# SalaryMonth là STRING (YYYY-MM hoặc YYYY-MM-DD), không phải DATE, nên dùng LIKE
		salary_placeholder = _placeholder(salary_vendor)
		salary_trend = []
		for month in months_list:
			try:
				# Dùng LIKE để match cả YYYY-MM và YYYY-MM-DD
				month_pattern = f"{month}-%"
				query = f"SELECT COALESCE(SUM(NetSalary), 0) FROM salaries WHERE SalaryMonth LIKE {salary_placeholder}"
				total = fetch_scalar_from_db(query, (month_pattern,), salary_vendor, return_float=True)
				logging.info(f"Salary trend for {month} (pattern: {month_pattern}): {total}")
				salary_trend.append({
					"month": month,
					"total": round(total, 2)
				})
			except Exception as e:
				logging.error(f"Error fetching salary trend for {month}: {e}", exc_info=True)
				salary_trend.append({
					"month": month,
					"total": 0.0
				})
		result["salary_trend"] = salary_trend
		
		# Workdays trend - tổng ngày công mỗi tháng
		# AttendanceMonth có thể là DATE hoặc STRING, thử cả hai cách
		# Dùng attendance_db_vendor vì attendance có thể ở database khác
		attendance_vendor = get_attendance_db_vendor()
		attendance_placeholder = _placeholder(attendance_vendor)
		workdays_trend = []
		for month in months_list:
			try:
				# Thử dùng LIKE trước (nếu là string)
				month_pattern = f"{month}-%"
				query = f"SELECT COALESCE(SUM(WorkDays), 0) FROM attendance WHERE AttendanceMonth LIKE {attendance_placeholder}"
				total = fetch_scalar_from_db(query, (month_pattern,), attendance_vendor)
				logging.info(f"Workdays trend for {month} (LIKE pattern: {month_pattern}): {total}")
				workdays_trend.append({
					"month": month,
					"total": total
				})
			except Exception as e:
				logging.error(f"Error fetching workdays trend for {month} with LIKE: {e}")
				# Fallback: thử dùng YEAR và MONTH (nếu là DATE)
				try:
					year, month_num = month.split("-")
					year_int = int(year)
					month_int = int(month_num)
					query = f"SELECT COALESCE(SUM(WorkDays), 0) FROM attendance WHERE YEAR(AttendanceMonth) = {attendance_placeholder} AND MONTH(AttendanceMonth) = {attendance_placeholder}"
					total = fetch_scalar_from_db(query, (year_int, month_int), attendance_vendor)
					logging.info(f"Workdays trend for {month} (YEAR/MONTH fallback): {total}")
					workdays_trend.append({
						"month": month,
						"total": total
					})
				except Exception as e2:
					logging.error(f"Error in fallback query for {month}: {e2}")
					workdays_trend.append({
						"month": month,
						"total": 0
					})
		result["workdays_trend"] = workdays_trend
		
		# Tính growth rate
		if len(employee_trend) >= 2:
			first_count = employee_trend[0]["count"]
			last_count = employee_trend[-1]["count"]
			if first_count > 0:
				growth_rate = ((last_count - first_count) / first_count) * 100
				result["employee_growth_rate"] = round(growth_rate, 2)
		
		if len(salary_trend) >= 2:
			first_total = salary_trend[0]["total"]
			last_total = salary_trend[-1]["total"]
			if first_total > 0:
				growth_rate = ((last_total - first_total) / first_total) * 100
				result["salary_growth_rate"] = round(growth_rate, 2)
		
		logging.info(f"Trends result: employee={len(employee_trend)}, salary={len(salary_trend)}, workdays={len(workdays_trend)}")
		
	except Exception as e:
		logging.error(f"Error fetching trends: {e}", exc_info=True)
		print(f"Error fetching trends: {e}")
		import traceback
		traceback.print_exc()
	
	return result

