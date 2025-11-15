import os
from typing import Any, Dict, List, Tuple
from config.sqlserver_connection import get_sqlserver_connection
from config.mysql_connection import get_mysql_connection

# ------------------- Helper -------------------

def get_db_vendor() -> str:
    """Trả về vendor hiện tại: sqlserver hoặc mysql"""
    return os.environ.get("DB_VENDOR", "sqlserver").strip().lower()

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
    actual_vendor = vendor or get_db_vendor()
    try:
        conn = _get_connection(actual_vendor)
        cursor = conn.cursor()
        cursor.execute(sql_query, params)
        columns = [col[0] for col in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]
    finally:
        if conn:
            conn.close()

# ------------------- Position Service -------------------

def get_positions() -> List[Dict[str, Any]]:
    """Lấy danh sách chức vụ"""
    vendor = get_db_vendor()
    query = "SELECT PositionID, PositionName FROM positions"
    return fetch_data_from_db(query, (), vendor)

def get_position_by_id(position_id: int) -> Dict[str, Any] | None:
    """Xem chi tiết chức vụ"""
    vendor = get_db_vendor()
    query = f"SELECT PositionID, PositionName FROM positions WHERE PositionID = {_placeholder(vendor)}"
    rows = fetch_data_from_db(query, (position_id,), vendor)
    return rows[0] if rows else None

def create_position(name: str) -> int:
    """Thêm chức vụ mới, đồng bộ ID từ SQL Server sang MySQL"""
    conn_sqlserver = get_sqlserver_connection()
    conn_mysql = get_mysql_connection()
    try:
        cursor_sql = conn_sqlserver.cursor()
        cursor_my = conn_mysql.cursor()

        # Bắt đầu transaction
        conn_sqlserver.autocommit = False
        conn_mysql.autocommit = False

        # Thêm vào SQL Server và lấy ID
        query_sql = f"INSERT INTO positions (PositionName) OUTPUT INSERTED.PositionID VALUES ({_placeholder('sqlserver')})"
        cursor_sql.execute(query_sql, (name,))
        new_id = cursor_sql.fetchone()[0]

        # Thêm vào MySQL với ID từ SQL Server
        query_my = f"INSERT INTO positions (PositionID, PositionName) VALUES ({_placeholder('mysql')}, {_placeholder('mysql')})"
        cursor_my.execute(query_my, (new_id, name))

        # Commit cả 2 DB
        conn_sqlserver.commit()
        conn_mysql.commit()

        return int(new_id)
    except Exception as e:
        conn_sqlserver.rollback()
        conn_mysql.rollback()
        raise e
    finally:
        cursor_sql.close()
        cursor_my.close()
        conn_sqlserver.close()
        conn_mysql.close()

def update_position(position_id: int, name: str):
    """Cập nhật tên chức vụ trên cả SQL Server và MySQL"""
    conn_sqlserver = get_sqlserver_connection()
    conn_mysql = get_mysql_connection()
    try:
        cursor_sql = conn_sqlserver.cursor()
        cursor_my = conn_mysql.cursor()

        conn_sqlserver.autocommit = False
        conn_mysql.autocommit = False

        # SQL Server
        query_sql = f"UPDATE positions SET PositionName={_placeholder('sqlserver')} WHERE PositionID={_placeholder('sqlserver')}"
        cursor_sql.execute(query_sql, (name, position_id))

        # MySQL
        query_my = f"UPDATE positions SET PositionName={_placeholder('mysql')} WHERE PositionID={_placeholder('mysql')}"
        cursor_my.execute(query_my, (name, position_id))

        # Commit cả 2 DB
        conn_sqlserver.commit()
        conn_mysql.commit()
    except Exception as e:
        conn_sqlserver.rollback()
        conn_mysql.rollback()
        raise e
    finally:
        cursor_sql.close()
        cursor_my.close()
        conn_sqlserver.close()
        conn_mysql.close()

def delete_position(position_id: int) -> int:
    """Xóa chức vụ nhưng không xóa nhân viên — tự cascade bằng code (KHÔNG sửa DB)"""
    conn_sqlserver = get_sqlserver_connection()
    conn_mysql = get_mysql_connection()
    try:
        cursor_sql = conn_sqlserver.cursor()
        cursor_my = conn_mysql.cursor()

        conn_sqlserver.autocommit = False
        conn_mysql.autocommit = False

        # STEP 1: Set NULL cho Employees trước (tránh lỗi FK)
        cursor_sql.execute(
            "UPDATE employees SET PositionID = NULL WHERE PositionID = ?",
            (position_id,)
        )
        cursor_my.execute(
            "UPDATE employees SET PositionID = NULL WHERE PositionID = %s",
            (position_id,)
        )

        # STEP 2: Xóa position
        cursor_sql.execute(
            "DELETE FROM positions WHERE PositionID = ?",
            (position_id,)
        )
        cursor_my.execute(
            "DELETE FROM positions WHERE PositionID = %s",
            (position_id,)
        )

        conn_sqlserver.commit()
        conn_mysql.commit()
        return cursor_sql.rowcount

    except Exception as e:
        conn_sqlserver.rollback()
        conn_mysql.rollback()
        raise e
    finally:
        cursor_sql.close()
        cursor_my.close()
        conn_sqlserver.close()
        conn_mysql.close()
