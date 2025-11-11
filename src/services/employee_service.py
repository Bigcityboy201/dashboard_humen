import os
from typing import Any, Dict, List, Tuple

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