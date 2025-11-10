import pyodbc  # Cần thư viện pyodbc cho SQL Server
import os

def get_sqlserver_connection():
    """Tạo và trả về đối tượng kết nối SQL Server."""
    # Giả định chuỗi kết nối được lấy từ biến môi trường
    conn_str = os.environ.get('SQL_SERVER_CONN_STRING')
    if not conn_str:
        raise ConnectionError("SQL_SERVER_CONN_STRING environment variable not set.")
    
    # Kết nối
    return pyodbc.connect(conn_str)