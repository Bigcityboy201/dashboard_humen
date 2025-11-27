import datetime
from typing import Any, Dict, List, Optional
from config.sqlserver_connection import get_sqlserver_connection

# ------------------- Helper -------------------

def _placeholder() -> str:
    """Placeholder cho SQL Server"""
    return "?"

def fetch_data_from_db(sql_query: str, params: tuple = ()) -> List[Dict[str, Any]]:
    """Lấy danh sách dữ liệu từ SQL Server"""
    conn = None
    try:
        conn = get_sqlserver_connection()
        cursor = conn.cursor()
        cursor.execute(sql_query, params)
        columns = [col[0] for col in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]
    finally:
        if conn:
            conn.close()

# ------------------- Dividend Service -------------------

def get_dividends() -> List[Dict[str, Any]]:
    """Lấy danh sách các đợt chi cổ tức từ SQL Server"""
    query = """
    SELECT DividendID, EmployeeID, DividendAmount, DividendDate, CreatedAt
    FROM dividends 
    ORDER BY DividendDate DESC, DividendID
    """
    return fetch_data_from_db(query)

def create_dividend(data: Dict[str, Any]) -> Dict[str, Any]:
    """Thêm mới một đợt chi cổ tức vào SQL Server"""
    conn = get_sqlserver_connection()
    try:
        cursor = conn.cursor()
        conn.autocommit = False

        employee_id = data.get("EmployeeID")
        dividend_amount = data.get("DividendAmount", 0.0)
        dividend_date = data.get("DividendDate", datetime.datetime.now().strftime("%Y-%m-%d"))

        query = f"""
        INSERT INTO dividends (EmployeeID, DividendAmount, DividendDate)
        OUTPUT INSERTED.DividendID, INSERTED.EmployeeID, INSERTED.DividendAmount,
               INSERTED.DividendDate, INSERTED.CreatedAt
        VALUES ({_placeholder()}, {_placeholder()}, {_placeholder()})
        """
        cursor.execute(query, (employee_id, dividend_amount, dividend_date))
        result = cursor.fetchone()
        if not result:
            raise Exception("Không lấy được dữ liệu sau khi insert")

        columns = [col[0] for col in cursor.description]
        conn.commit()
        return {**dict(zip(columns, result)), "message": "Dividend record created"}

    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cursor.close()
        conn.close()

def get_dividend_by_id(dividend_id: int) -> Optional[Dict[str, Any]]:
    """Lấy chi tiết đợt chi cổ tức theo ID"""
    query = """
    SELECT DividendID, EmployeeID, DividendAmount, DividendDate, CreatedAt
    FROM dividends
    WHERE DividendID = ?
    """
    result = fetch_data_from_db(query, (dividend_id,))
    return result[0] if result else None

def delete_dividend(dividend_id: int) -> Dict[str, Any]:
    """Xóa đợt chi cổ tức trên SQL Server"""
    conn = get_sqlserver_connection()
    try:
        cursor = conn.cursor()
        conn.autocommit = False

        dividend_record = get_dividend_by_id(dividend_id)
        if not dividend_record:
            raise Exception("Không tìm thấy bản ghi cổ tức")

        query = "DELETE FROM dividends WHERE DividendID = ?"
        cursor.execute(query, (dividend_id,))

        conn.commit()
        return {
            "message": f"Dividend record with ID {dividend_id} deleted successfully",
            "deleted_record": dividend_record
        }

    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cursor.close()
        conn.close()
def update_dividend_record(dividend_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
    """Cập nhật thông tin một đợt chi cổ tức trong SQL Server"""
    conn = get_sqlserver_connection()
    try:
        cursor = conn.cursor()
        conn.autocommit = False

        # Lấy bản ghi hiện tại
        existing = get_dividend_by_id(dividend_id)
        if not existing:
            raise Exception("Không tìm thấy bản ghi cổ tức")

        # Dữ liệu mới
        employee_id = data.get("EmployeeID", existing["EmployeeID"])
        dividend_amount = data.get("DividendAmount", existing["DividendAmount"])
        dividend_date = data.get("DividendDate", existing["DividendDate"])

        query = f"""
        UPDATE dividends
        SET EmployeeID = {_placeholder()},
            DividendAmount = {_placeholder()},
            DividendDate = {_placeholder()}
        OUTPUT INSERTED.DividendID, INSERTED.EmployeeID, INSERTED.DividendAmount,
               INSERTED.DividendDate, INSERTED.CreatedAt
        WHERE DividendID = {_placeholder()}
        """
        cursor.execute(query, (employee_id, dividend_amount, dividend_date, dividend_id))
        result = cursor.fetchone()
        if not result:
            raise Exception("Cập nhật thất bại")

        columns = [col[0] for col in cursor.description]
        conn.commit()
        return {**dict(zip(columns, result)), "message": "Dividend record updated successfully"}

    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cursor.close()
        conn.close()
