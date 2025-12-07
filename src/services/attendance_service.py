import os
from typing import Any, Dict, List, Tuple, Optional
from datetime import datetime
import calendar
from config.mysql_connection import get_mysql_connection
from config.sqlserver_connection import get_sqlserver_connection

def get_attendance_db_vendor() -> str:
    """Trả về vendor cho database attendance"""
    return os.environ.get("ATTENDANCE_DB_VENDOR", "mysql").strip().lower()

def _placeholder(vendor: str) -> str:
    return "?" if vendor == "sqlserver" else "%s"

def fetch_data_from_db(sql_query: str, params: Tuple[Any, ...], vendor: str) -> List[Dict[str, Any]]:
    """Lấy danh sách records từ DB"""
    conn = None
    try:
        if vendor == "mysql":
            conn = get_mysql_connection()
        else:
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
            conn = get_mysql_connection()
        else:
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

def get_total_days_in_month(attendance_month: str) -> int:
    """Tính tổng số ngày trong tháng từ AttendanceMonth (format: YYYY-MM-DD)"""
    try:
        date_obj = datetime.strptime(attendance_month, "%Y-%m-%d")
        return calendar.monthrange(date_obj.year, date_obj.month)[1]
    except:
        return 30  # Default fallback

def get_attendances(employee_id: Optional[int] = None, attendance_month: Optional[str] = None, year: Optional[int] = None) -> List[Dict[str, Any]]:
    """Lấy danh sách bản ghi chấm công với filter"""
    vendor = get_attendance_db_vendor()
    placeholder = _placeholder(vendor)
    
    # Join với employees để lấy FullName
    if vendor == "sqlserver":
        query = """
        SELECT 
            a.AttendanceID,
            a.EmployeeID,
            e.FullName,
            a.AttendanceMonth,
            a.WorkDays,
            a.AbsentDays,
            a.LeaveDays,
            a.CreatedAt,
            DAY(EOMONTH(a.AttendanceMonth)) as TotalDaysInMonth
        FROM attendance a
        LEFT JOIN employees e ON a.EmployeeID = e.EmployeeID
        WHERE 1=1
        """
    else:
        # MySQL
        query = """
        SELECT 
            a.AttendanceID,
            a.EmployeeID,
            e.FullName,
            a.AttendanceMonth,
            a.WorkDays,
            a.AbsentDays,
            a.LeaveDays,
            a.CreatedAt,
            DAY(LAST_DAY(a.AttendanceMonth)) as TotalDaysInMonth
        FROM attendance a
        LEFT JOIN employees e ON a.EmployeeID = e.EmployeeID
        WHERE 1=1
        """
    
    params = []
    
    if employee_id:
        query += f" AND a.EmployeeID = {placeholder}"
        params.append(employee_id)
        
    if attendance_month:
        query += f" AND a.AttendanceMonth = {placeholder}"
        params.append(attendance_month)
    elif year:
        # Filter theo năm: AttendanceMonth LIKE 'YYYY-%'
        query += f" AND a.AttendanceMonth LIKE {placeholder}"
        params.append(f"{year}-%")
        
    query += " ORDER BY a.AttendanceMonth DESC, a.EmployeeID"
    
    result = fetch_data_from_db(query, tuple(params), vendor)
    
    # Đảm bảo TotalDaysInMonth được tính nếu SQL không trả về
    for record in result:
        if not record.get("TotalDaysInMonth"):
            record["TotalDaysInMonth"] = get_total_days_in_month(str(record.get("AttendanceMonth", "")))
    
    return result

def create_attendance(data: Dict[str, Any]) -> Dict[str, Any]:
    """Tạo một bản ghi Timesheet (bảng chấm công) cho nhân viên/tháng"""
    vendor = get_attendance_db_vendor()
    placeholder = _placeholder(vendor)
    
    employee_id = data.get("EmployeeID")
    attendance_month = data.get("AttendanceMonth")
    work_days = data.get("WorkDays", 0)
    absent_days = data.get("AbsentDays", 0)
    leave_days = data.get("LeaveDays", 0)
    
    if not employee_id or not attendance_month:
        raise Exception("Thiếu EmployeeID hoặc AttendanceMonth")
    
    query = f"""
    INSERT INTO attendance (EmployeeID, AttendanceMonth, WorkDays, AbsentDays, LeaveDays)
    VALUES ({placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder})
    """
    
    if vendor == "sqlserver":
        query += " OUTPUT INSERTED.AttendanceID, INSERTED.EmployeeID, INSERTED.AttendanceMonth, INSERTED.WorkDays, INSERTED.AbsentDays, INSERTED.LeaveDays, INSERTED.CreatedAt"
        result = fetch_data_from_db(query, (employee_id, attendance_month, work_days, absent_days, leave_days), vendor)
        if result:
            result[0]["message"] = "Timesheet created successfully"
            return result[0]
        return {}
    else:
        # MySQL
        execute_db(query, (employee_id, attendance_month, work_days, absent_days, leave_days), vendor)
        # Lấy bản ghi vừa tạo
        get_query = """
        SELECT AttendanceID, EmployeeID, AttendanceMonth, WorkDays, AbsentDays, LeaveDays, CreatedAt
        FROM attendance 
        WHERE EmployeeID = %s AND AttendanceMonth = %s
        ORDER BY AttendanceID DESC LIMIT 1
        """
        result = fetch_data_from_db(get_query, (employee_id, attendance_month), vendor)
        if result:
            result[0]["message"] = "Timesheet created successfully"
            return result[0]
        return {}

def get_attendance_by_id(attendance_id: int) -> Optional[Dict[str, Any]]:
    """Lấy chi tiết bản ghi chấm công theo ID"""
    vendor = get_attendance_db_vendor()
    placeholder = _placeholder(vendor)
    
    if vendor == "sqlserver":
        query = f"""
        SELECT 
            a.AttendanceID,
            a.EmployeeID,
            e.FullName,
            a.AttendanceMonth,
            a.WorkDays,
            a.AbsentDays,
            a.LeaveDays,
            a.CreatedAt,
            DAY(EOMONTH(a.AttendanceMonth)) as TotalDaysInMonth
        FROM attendance a
        LEFT JOIN employees e ON a.EmployeeID = e.EmployeeID
        WHERE a.AttendanceID = {placeholder}
        """
    else:
        query = f"""
        SELECT 
            a.AttendanceID,
            a.EmployeeID,
            e.FullName,
            a.AttendanceMonth,
            a.WorkDays,
            a.AbsentDays,
            a.LeaveDays,
            a.CreatedAt,
            DAY(LAST_DAY(a.AttendanceMonth)) as TotalDaysInMonth
        FROM attendance a
        LEFT JOIN employees e ON a.EmployeeID = e.EmployeeID
        WHERE a.AttendanceID = {placeholder}
        """
    
    result = fetch_data_from_db(query, (attendance_id,), vendor)
    
    if result:
        record = result[0]
        if not record.get("TotalDaysInMonth"):
            record["TotalDaysInMonth"] = get_total_days_in_month(str(record.get("AttendanceMonth", "")))
        return record
    
    return None

def update_attendance(attendance_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
    """Cập nhật bản ghi chấm công (ví dụ: điều chỉnh ngày nghỉ phép, ngày vắng mặt)"""
    vendor = get_attendance_db_vendor()
    placeholder = _placeholder(vendor)
    
    # Lấy thông tin hiện tại
    current_attendance = get_attendance_by_id(attendance_id)
    if not current_attendance:
        raise Exception("Không tìm thấy bản ghi chấm công")
    
    # Cập nhật các trường được cung cấp
    work_days = data.get("WorkDays")
    absent_days = data.get("AbsentDays")
    leave_days = data.get("LeaveDays")
    
    if work_days is None and absent_days is None and leave_days is None:
        raise Exception("Cần cung cấp ít nhất một trường để cập nhật")
    
    # Sử dụng giá trị hiện tại nếu không được cung cấp
    new_work_days = work_days if work_days is not None else current_attendance["WorkDays"]
    new_absent_days = absent_days if absent_days is not None else current_attendance["AbsentDays"]
    new_leave_days = leave_days if leave_days is not None else current_attendance["LeaveDays"]
    
    query = f"""
    UPDATE attendance 
    SET WorkDays = {placeholder}, AbsentDays = {placeholder}, LeaveDays = {placeholder}
    WHERE AttendanceID = {placeholder}
    """
    
    execute_db(query, (new_work_days, new_absent_days, new_leave_days, attendance_id), vendor)
    
    # Trả về bản ghi đã cập nhật
    updated = get_attendance_by_id(attendance_id)
    if updated:
        updated["message"] = "Timesheet updated"
    return updated

def delete_attendance(attendance_id: int) -> Dict[str, Any]:
    """Xóa bản ghi chấm công"""
    vendor = get_attendance_db_vendor()
    placeholder = _placeholder(vendor)
    
    # Lấy thông tin trước khi xóa
    attendance_record = get_attendance_by_id(attendance_id)
    if not attendance_record:
        raise Exception("Không tìm thấy bản ghi chấm công")
    
    query = f"DELETE FROM attendance WHERE AttendanceID = {placeholder}"
    rowcount = execute_db(query, (attendance_id,), vendor)
    
    if rowcount == 0:
        raise Exception("Không tìm thấy bản ghi chấm công để xóa")
    
    return {
        "message": f"Attendance record with ID {attendance_id} deleted successfully"
    }

def get_attendance_statistics(attendance_month: Optional[str] = None, year: Optional[int] = None) -> Dict[str, Any]:
    """Thống kê tổng số ngày công, vắng mặt theo tháng/quý"""
    vendor = get_attendance_db_vendor()
    placeholder = _placeholder(vendor)
    
    if attendance_month:
        # Thống kê theo tháng cụ thể
        query = f"""
        SELECT 
            COUNT(*) as total_records,
            SUM(WorkDays) as total_work_days,
            SUM(AbsentDays) as total_absent_days,
            SUM(LeaveDays) as total_leave_days
        FROM attendance 
        WHERE AttendanceMonth = {placeholder}
        """
        params = (attendance_month,)
    elif year:
        # Thống kê theo năm
        query = f"""
        SELECT 
            COUNT(*) as total_records,
            SUM(WorkDays) as total_work_days,
            SUM(AbsentDays) as total_absent_days,
            SUM(LeaveDays) as total_leave_days
        FROM attendance 
        WHERE AttendanceMonth LIKE {placeholder}
        """
        params = (f"{year}-%",)
    else:
        # Thống kê tổng quát (tất cả các tháng)
        query = """
        SELECT 
            COUNT(*) as total_records,
            SUM(WorkDays) as total_work_days,
            SUM(AbsentDays) as total_absent_days,
            SUM(LeaveDays) as total_leave_days
        FROM attendance
        """
        params = ()
    
    result = fetch_data_from_db(query, params, vendor)
    stats = result[0] if result else {}
    
    total_work_days = int(stats.get("total_work_days", 0) or 0)
    total_absent_days = int(stats.get("total_absent_days", 0) or 0)
    total_leave_days = int(stats.get("total_leave_days", 0) or 0)
    total_records = int(stats.get("total_records", 0) or 0)
    
    # Tính attendance_rate: (total_work_days / (total_work_days + total_absent_days)) * 100
    total_days = total_work_days + total_absent_days
    if total_days > 0:
        attendance_rate = (total_work_days / total_days) * 100
        attendance_rate_str = f"{attendance_rate:.1f}%"
    else:
        attendance_rate_str = "0%"
    
    return {
        "total_records": total_records,
        "total_work_days": total_work_days,
        "total_absent_days": total_absent_days,
        "total_leave_days": total_leave_days,
        "attendance_rate": attendance_rate_str
    }