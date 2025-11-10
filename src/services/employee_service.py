# src/services/employee_service.py

# Giả định bạn đã có logic chọn CSDL dựa trên cấu hình ứng dụng (app.config)
from config.sqlserver_connection import get_sqlserver_connection 
# from config.mysql_connection import get_mysql_connection 
# Sử dụng SQL Server làm ví dụ chính cho phần dưới

def fetch_data_from_db(sql_query, params):
    """Hàm chung để thực thi truy vấn và trả về kết quả."""
    conn = None
    try:
        # Chọn CSDL: Ở đây ta dùng SQL Server
        conn = get_sqlserver_connection()
        cursor = conn.cursor()
        
        # Thực thi truy vấn
        cursor.execute(sql_query, params)
        
        # Lấy tên cột để định dạng kết quả thành JSON/Dictionary
        columns = [column[0] for column in cursor.description]
        results = []
        for row in cursor.fetchall():
            results.append(dict(zip(columns, row)))
            
        return results

    except Exception as e:
        # Xử lý rollback hoặc ghi log vào logging_service
        # Đây là nơi logic của src/services/logging_service.py được gọi
        raise Exception(f"Lỗi DTB: {e}")
        
    finally:
        if conn:
            conn.close()

def get_all_employees(department_id=None, status=None, page=1, size=10):
    """Lấy danh sách nhân viên với JOIN và phân trang/lọc."""
    
    # 1. Xây dựng câu lệnh SQL (Với JOIN cho Departments và Positions)
    sql_base = """
    SELECT 
        e.EmployeeID, e.FullName, e.HireDate, e.Status, e.Email, e.PhoneNumber,
        d.DepartmentID, d.DepartmentName, 
        p.PositionID, p.PositionName
    FROM employees e
    JOIN departments d ON e.DepartmentID = d.DepartmentID
    JOIN positions p ON e.PositionID = p.PositionID
    WHERE 1=1 
    """
    params = []
    
    # 2. Xử lý các tham số lọc (WHERE clauses)
    if department_id:
        sql_base += " AND e.DepartmentID = %s"  
        params.append(department_id)
    
    if status:
        sql_base += " AND e.Status = %s"
        params.append(status)
    
    # 3. Xử lý Phân trang (OFFSET FETCH NEXT - Tối ưu cho SQL Server)
    offset = (page - 1) * size
    sql_base += f" ORDER BY e.EmployeeID OFFSET {offset} ROWS FETCH NEXT {size} ROWS ONLY"

    # 4. Truy vấn tổng số bản ghi (không phân trang)
    total_query = "SELECT COUNT(e.EmployeeID) FROM employees e WHERE 1=1"
    # Cần lặp lại logic WHERE cho total_query
    # ...
    # Giả lập:
    total_count = 58 
    
    # 5. Thực thi truy vấn chính
    employee_data = fetch_data_from_db(sql_base, tuple(params))
    
    return {
        "total_records": total_count,
        "page": page,
        "size": size,
        "employees": employee_data
    }