import os
from typing import Any, Dict, List, Tuple, Optional
from config.sqlserver_connection import get_sqlserver_connection
from config.mysql_connection import get_mysql_connection
import datetime

# ------------------- Helper -------------------

def get_salary_db_vendor() -> str:
    """Trả về vendor cho salary database"""
    return os.environ.get("SALARY_DB_VENDOR", "mysql").strip().lower()

def _get_connection(vendor: str):
    """Tạo connection DB"""
    if vendor == "mysql":
        return get_mysql_connection()
    return get_sqlserver_connection()

def _placeholder(vendor: str) -> str:
    """Placeholder theo vendor"""
    return "?" if vendor == "sqlserver" else "%s"

def fetch_data_from_db(sql_query: str, params: Tuple[Any, ...], vendor: str | None = None) -> List[Dict[str, Any]]:
    """Lấy danh sách dữ liệu"""
    conn = None
    actual_vendor = vendor or get_salary_db_vendor()
    try:
        conn = _get_connection(actual_vendor)
        cursor = conn.cursor()
        cursor.execute(sql_query, params)
        columns = [col[0] for col in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]
    finally:
        if conn:
            conn.close()

# ------------------- Dividend Service -------------------

def get_dividends() -> List[Dict[str, Any]]:
    """Lấy danh sách các đợt chi cổ tức (chỉ từ MySQL)"""
    vendor = get_salary_db_vendor()
    
    query = """
    SELECT DividendID, EmployeeID, DividendAmount, DividendDate, CreatedAt
    FROM dividends 
    ORDER BY DividendDate DESC, DividendID
    """
    
    return fetch_data_from_db(query, (), vendor)

def create_dividend(data: Dict[str, Any]) -> Dict[str, Any]:
    """Thêm mới một đợt chi cổ tức và đồng bộ cả 2 DB"""
    conn_sqlserver = get_sqlserver_connection()
    conn_mysql = get_mysql_connection()
    
    try:
        cursor_sql = conn_sqlserver.cursor()
        cursor_my = conn_mysql.cursor()

        # Bắt đầu transaction
        conn_sqlserver.autocommit = False
        conn_mysql.autocommit = False

        # Dữ liệu từ request
        employee_id = data.get("EmployeeID")
        dividend_amount = data.get("DividendAmount", 0.0)
        dividend_date = data.get("DividendDate", datetime.datetime.now().strftime("%Y-%m-%d"))

        # Thêm vào SQL Server và lấy ID
        query_sql = f"""
        INSERT INTO dividends (EmployeeID, DividendAmount, DividendDate) 
        OUTPUT INSERTED.DividendID, INSERTED.EmployeeID, INSERTED.DividendAmount, 
               INSERTED.DividendDate, INSERTED.CreatedAt
        VALUES ({_placeholder('sqlserver')}, {_placeholder('sqlserver')}, {_placeholder('sqlserver')})
        """
        cursor_sql.execute(query_sql, (employee_id, dividend_amount, dividend_date))
        
        # Lấy kết quả từ SQL Server
        sql_result = cursor_sql.fetchone()
        if not sql_result:
            raise Exception("Không lấy được dữ liệu từ SQL Server sau khi insert")
            
        dividend_id = sql_result[0]
        columns = [col[0] for col in cursor_sql.description]
        dividend_data = dict(zip(columns, sql_result))

        # Thêm vào MySQL với cùng ID
        query_my = f"""
        INSERT INTO dividends (DividendID, EmployeeID, DividendAmount, DividendDate)
        VALUES ({_placeholder('mysql')}, {_placeholder('mysql')}, {_placeholder('mysql')}, {_placeholder('mysql')})
        """
        cursor_my.execute(query_my, (dividend_id, employee_id, dividend_amount, dividend_date))

        # Commit cả 2 DB
        conn_sqlserver.commit()
        conn_mysql.commit()

        return {
            **dividend_data,
            "message": "Dividend record created"
        }

    except Exception as e:
        conn_sqlserver.rollback()
        conn_mysql.rollback()
        raise e
    finally:
        cursor_sql.close()
        cursor_my.close()
        conn_sqlserver.close()
        conn_mysql.close()

def get_dividend_by_id(dividend_id: int) -> Optional[Dict[str, Any]]:
    """Lấy chi tiết đợt chi cổ tức theo ID"""
    vendor = get_salary_db_vendor()
    placeholder = _placeholder(vendor)
    
    query = f"""
    SELECT DividendID, EmployeeID, DividendAmount, DividendDate, CreatedAt
    FROM dividends 
    WHERE DividendID = {placeholder}
    """
    
    result = fetch_data_from_db(query, (dividend_id,), vendor)
    return result[0] if result else None

def delete_dividend(dividend_id: int) -> Dict[str, Any]:
    """Xóa đợt chi cổ tức trên cả 2 DB"""
    conn_sqlserver = get_sqlserver_connection()
    conn_mysql = get_mysql_connection()
    
    try:
        cursor_sql = conn_sqlserver.cursor()
        cursor_my = conn_mysql.cursor()

        # Bắt đầu transaction
        conn_sqlserver.autocommit = False
        conn_mysql.autocommit = False

        # Lấy thông tin trước khi xóa
        dividend_record = get_dividend_by_id(dividend_id)
        if not dividend_record:
            raise Exception("Không tìm thấy bản ghi cổ tức")

        # Xóa từ SQL Server
        query_sql = f"DELETE FROM dividends WHERE DividendID = {_placeholder('sqlserver')}"
        cursor_sql.execute(query_sql, (dividend_id,))

        # Xóa từ MySQL
        query_my = f"DELETE FROM dividends WHERE DividendID = {_placeholder('mysql')}"
        cursor_my.execute(query_my, (dividend_id,))

        # Commit cả 2 DB
        conn_sqlserver.commit()
        conn_mysql.commit()

        return {
            "message": f"Dividend record with ID {dividend_id} deleted successfully",
            "deleted_record": dividend_record
        }

    except Exception as e:
        conn_sqlserver.rollback()
        conn_mysql.rollback()
        raise e
    finally:
        cursor_sql.close()
        cursor_my.close()
        conn_sqlserver.close()
        conn_mysql.close()