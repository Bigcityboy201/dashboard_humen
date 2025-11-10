import mysql.connector  # Cần thư viện mysql.connector cho MySQL
import os
def get_mysql_connection():
    """Tạo và trả về đối tượng kết nối MySQL."""
    # Giả định các tham số kết nối
    return mysql.connector.connect(
        host=os.environ.get('MYSQL_HOST'),
        user=os.environ.get('MYSQL_USER'),
        password=os.environ.get('MYSQL_PASSWORD'),
        database=os.environ.get('MYSQL_DB_NAME')
    )