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

from typing import Dict, Any
from datetime import datetime

def normalize_attendance_month(attendance_month: str) -> str:
    """
    Chấp nhận YYYY-MM hoặc YYYY-MM-DD
    Trả về YYYY-MM-DD để MySQL DATE accept
    """
    if not attendance_month:
        raise ValueError("Thiếu AttendanceMonth")
    
    s = str(attendance_month).strip()
    
    # YYYY-MM-DD
    try:
        dt = datetime.strptime(s, "%Y-%m-%d")
        return dt.strftime("%Y-%m-%d")
    except ValueError:
        pass
    
    # YYYY-MM -> thêm ngày 01
    try:
        dt = datetime.strptime(s, "%Y-%m")
        return dt.strftime("%Y-%m-01")
    except ValueError:
        raise ValueError(f"AttendanceMonth phải có format YYYY-MM hoặc YYYY-MM-DD. Received: {attendance_month}")


def create_attendance(data: Dict[str, Any]) -> Dict[str, Any]:
    """Tạo một bản ghi Timesheet (bảng chấm công) cho nhân viên/tháng"""
    vendor = get_attendance_db_vendor()
    placeholder = _placeholder(vendor)
    
    try:
        # Hỗ trợ nhiều format field names
        employee_id = data.get("EmployeeID") or data.get("employee_id")
        attendance_month = data.get("AttendanceMonth") or data.get("attendance_month") or data.get("Month") or data.get("month")
        work_days = data.get("WorkDays") or data.get("work_days") or data.get("WorkingDays") or data.get("working_days") or 0
        absent_days = data.get("AbsentDays") or data.get("absent_days") or 0
        leave_days = data.get("LeaveDays") or data.get("leave_days") or 0
        
        # Convert sang int
        try:
            employee_id = int(employee_id) if employee_id else None
        except (ValueError, TypeError):
            employee_id = None
        try:
            work_days = int(work_days)
        except (ValueError, TypeError):
            work_days = 0
        try:
            absent_days = int(absent_days)
        except (ValueError, TypeError):
            absent_days = 0
        try:
            leave_days = int(leave_days)
        except (ValueError, TypeError):
            leave_days = 0
        
        if not employee_id or not attendance_month:
            raise Exception(f"Thiếu EmployeeID hoặc AttendanceMonth. Received data: {data}")
        
        # -----------------------------
        # Chuẩn hóa attendance_month về YYYY-MM-01
        # -----------------------------
        try:
            attendance_month = normalize_attendance_month(attendance_month)
        except ValueError as e:
            raise Exception(str(e))
        
        # Kiểm tra đã có attendance chưa
        try:
            check_query = f"""
            SELECT AttendanceID FROM attendance 
            WHERE EmployeeID = {placeholder} AND AttendanceMonth = {placeholder}
            """
            existing = fetch_data_from_db(check_query, (employee_id, attendance_month), vendor)
            if existing:
                raise Exception(f"Đã tồn tại bản ghi chấm công cho nhân viên {employee_id} trong tháng {attendance_month}. Vui lòng cập nhật thay vì tạo mới.")
        except Exception as check_error:
            # Nếu lỗi khi check, bỏ qua và tiếp tục tạo
            print(f"Warning: Could not check for existing attendance: {check_error}")
        
        print(f"Creating attendance: EmployeeID={employee_id}, Month={attendance_month}, WorkDays={work_days}, AbsentDays={absent_days}, LeaveDays={leave_days}")
        
        query = f"""
        INSERT INTO attendance (EmployeeID, AttendanceMonth, WorkDays, AbsentDays, LeaveDays)
        VALUES ({placeholder}, {placeholder}, {placeholder}, {placeholder}, {placeholder})
        """
        
        try:
            if vendor == "sqlserver":
                query += " OUTPUT INSERTED.AttendanceID, INSERTED.EmployeeID, INSERTED.AttendanceMonth, INSERTED.WorkDays, INSERTED.AbsentDays, INSERTED.LeaveDays, INSERTED.CreatedAt"
                print(f"Executing SQL Server query: {query}")
                result = fetch_data_from_db(query, (employee_id, attendance_month, work_days, absent_days, leave_days), vendor)
                if result:
                    result[0]["message"] = "Timesheet created successfully"
                    return result[0]
                raise Exception("Không thể tạo bản ghi chấm công (SQL Server) - không có kết quả trả về")
            else:
                # MySQL
                print(f"Executing MySQL query: {query}")
                execute_db(query, (employee_id, attendance_month, work_days, absent_days, leave_days), vendor)
                # Lấy bản ghi vừa tạo
                get_query = f"""
                SELECT AttendanceID, EmployeeID, AttendanceMonth, WorkDays, AbsentDays, LeaveDays, CreatedAt
                FROM attendance 
                WHERE EmployeeID = {placeholder} AND AttendanceMonth = {placeholder}
                ORDER BY AttendanceID DESC LIMIT 1
                """
                result = fetch_data_from_db(get_query, (employee_id, attendance_month), vendor)
                if result:
                    result[0]["message"] = "Timesheet created successfully"
                    return result[0]
                raise Exception("Không thể tạo bản ghi chấm công (MySQL) - không tìm thấy bản ghi sau khi insert")
        except Exception as db_error:
            import traceback
            db_trace = traceback.format_exc()
            print(f"Database error in create_attendance: {str(db_error)}")
            print(f"Database traceback: {db_trace}")
            raise Exception(f"Lỗi database khi tạo chấm công: {str(db_error)}")
            
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f"Error in create_attendance: {str(e)}")
        print(f"Traceback: {error_trace}")
        raise Exception(f"Lỗi khi tạo chấm công: {str(e)}")


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
        result = fetch_data_from_db(query, params, vendor)
        stats = result[0] if result else {}
        
        total_work_days = int(stats.get("total_work_days", 0) or 0)
        total_absent_days = int(stats.get("total_absent_days", 0) or 0)
        total_leave_days = int(stats.get("total_leave_days", 0) or 0)
        total_records = int(stats.get("total_records", 0) or 0)
        
        # Tính attendance_rate
        total_days = total_work_days + total_absent_days
        if total_days > 0:
            attendance_rate = (total_work_days / total_days) * 100
            attendance_rate_str = f"{attendance_rate:.1f}%"
        else:
            attendance_rate_str = "0%"
        
        return {
            "month": attendance_month,
            "total_records": total_records,
            "total_work_days": total_work_days,
            "total_absent_days": total_absent_days,
            "total_leave_days": total_leave_days,
            "attendance_rate": attendance_rate_str
        }
    elif year:
        # Thống kê theo năm - trả về dữ liệu theo tháng cho dashboard
        monthly_query = f"""
        SELECT 
            AttendanceMonth as month,
            COUNT(*) as employee_count,
            SUM(WorkDays) as total_work_days,
            SUM(AbsentDays) as total_absent_days,
            SUM(LeaveDays) as total_leave_days
        FROM attendance 
        WHERE AttendanceMonth LIKE {placeholder}
        GROUP BY AttendanceMonth
        ORDER BY AttendanceMonth
        """
        monthly_params = (f"{year}-%",)
        
        try:
            monthly_data = fetch_data_from_db(monthly_query, monthly_params, vendor)
        except Exception as e:
            print(f"Error fetching monthly attendance data: {e}")
            monthly_data = []
        
        # Tính tổng hợp cả năm
        total_query = f"""
        SELECT 
            COUNT(*) as total_records,
            SUM(WorkDays) as total_work_days,
            SUM(AbsentDays) as total_absent_days,
            SUM(LeaveDays) as total_leave_days
        FROM attendance 
        WHERE AttendanceMonth LIKE {placeholder}
        """
        try:
            total_result = fetch_data_from_db(total_query, monthly_params, vendor)
            total_stats = total_result[0] if total_result else {}
        except Exception as e:
            print(f"Error fetching total attendance stats: {e}")
            total_stats = {}
        
        # Format monthly_data để phù hợp với dashboard
        formatted_monthly_data = []
        for month_row in monthly_data:
            formatted_monthly_data.append({
                "month": month_row.get("month", ""),
                "employee_count": int(month_row.get("employee_count", 0)),
                "total_work_days": int(month_row.get("total_work_days", 0) or 0),
                "total_absent_days": int(month_row.get("total_absent_days", 0) or 0),
                "total_leave_days": int(month_row.get("total_leave_days", 0) or 0)
            })
        
        # Tính tổng hợp
        total_work_days = int(total_stats.get("total_work_days", 0) or 0)
        total_absent_days = int(total_stats.get("total_absent_days", 0) or 0)
        total_leave_days = int(total_stats.get("total_leave_days", 0) or 0)
        total_records = int(total_stats.get("total_records", 0) or 0)
        
        # Tính attendance_rate
        total_days = total_work_days + total_absent_days
        if total_days > 0:
            attendance_rate = (total_work_days / total_days) * 100
            attendance_rate_str = f"{attendance_rate:.1f}%"
        else:
            attendance_rate_str = "0%"
        
        return {
            "year": year,
            "month": None,
            "monthly_data": formatted_monthly_data,
            "total_records": total_records,
            "total_work_days": total_work_days,
            "total_absent_days": total_absent_days,
            "total_leave_days": total_leave_days,
            "attendance_rate": attendance_rate_str
        }
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
        
        # Tính attendance_rate
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