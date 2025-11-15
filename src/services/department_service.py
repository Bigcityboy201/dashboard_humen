# src/services/department_service.py

import os
from typing import Any, Dict, List, Tuple
from config.sqlserver_connection import get_sqlserver_connection
from config.mysql_connection import get_mysql_connection

# ------------------- Helper functions -------------------

def get_db_vendor() -> str:
    """Trả về vendor hiện tại: sqlserver hoặc mysql"""
    return os.environ.get("DB_VENDOR", "sqlserver").strip().lower()

def _get_connection(vendor: str):
    """Tạo connection dựa theo vendor"""
    if vendor == "mysql":
        return get_mysql_connection()
    return get_sqlserver_connection()

def _placeholder(vendor: str) -> str:
    """Trả về ký tự placeholder cho query"""
    return "?" if vendor == "sqlserver" else "%s"

def fetch_data_from_db(sql_query: str, params: Tuple[Any, ...], vendor: str | None = None) -> List[Dict[str, Any]]:
    """Lấy danh sách records từ DB"""
    conn = None
    actual_vendor = vendor or get_db_vendor()
    try:
        conn = _get_connection(actual_vendor)
        cursor = conn.cursor()
        cursor.execute(sql_query, params)
        columns = [col[0] for col in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]
    except Exception as e:
        raise Exception(f"Lỗi DB: {e}")
    finally:
        if conn:
            conn.close()

def fetch_scalar_from_db(sql_query: str, params: Tuple[Any, ...], vendor: str | None = None) -> int:
    """Lấy giá trị scalar từ DB"""
    conn = None
    actual_vendor = vendor or get_db_vendor()
    try:
        conn = _get_connection(actual_vendor)
        cursor = conn.cursor()
        cursor.execute(sql_query, params)
        row = cursor.fetchone()
        return int(row[0]) if row else 0
    finally:
        if conn:
            conn.close()

# ------------------- Department Service -------------------

def get_departments() -> List[Dict[str, Any]]:
    """Lấy danh sách phòng ban"""
    vendor = get_db_vendor()
    query = "SELECT DepartmentID, DepartmentName FROM departments"
    return fetch_data_from_db(query, (), vendor)

def get_department_by_id(department_id: int) -> Dict[str, Any] | None:
    """Xem chi tiết phòng ban"""
    vendor = get_db_vendor()
    query = "SELECT DepartmentID, DepartmentName FROM departments WHERE DepartmentID = " + _placeholder(vendor)
    rows = fetch_data_from_db(query, (department_id,), vendor)
    return rows[0] if rows else None

def create_department(name: str) -> int:
    conn_sqlserver = get_sqlserver_connection()  # autocommit=False mặc định
    conn_mysql = get_mysql_connection()
    try:
        cursor_sql = conn_sqlserver.cursor()
        cursor_my = conn_mysql.cursor()

        # Thêm vào SQL Server và lấy ID
        cursor_sql.execute(
            "INSERT INTO departments (DepartmentName) OUTPUT INSERTED.DepartmentID VALUES (?)", 
            (name,)
        )
        new_id = cursor_sql.fetchone()[0]

        # Thêm vào MySQL với ID lấy từ SQL Server
        cursor_my.execute(
            "INSERT INTO departments (DepartmentID, DepartmentName) VALUES (%s, %s)", 
            (new_id, name)
        )

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


def update_department(department_id: int, name: str) -> int:
    conn_sqlserver = get_sqlserver_connection()
    conn_mysql = get_mysql_connection()
    try:
        cursor_sql = conn_sqlserver.cursor()
        cursor_my = conn_mysql.cursor()

        # Update SQL Server
        cursor_sql.execute(
            "UPDATE departments SET DepartmentName = ? WHERE DepartmentID = ?", 
            (name, department_id)
        )

        # Update MySQL
        cursor_my.execute(
            "UPDATE departments SET DepartmentName = %s WHERE DepartmentID = %s", 
            (name, department_id)
        )

        # Commit cả 2 DB
        conn_sqlserver.commit()
        conn_mysql.commit()
        return 1
    except Exception as e:
        conn_sqlserver.rollback()
        conn_mysql.rollback()
        raise e
    finally:
        cursor_sql.close()
        cursor_my.close()
        conn_sqlserver.close()
        conn_mysql.close()

def delete_department(department_id: int) -> int:
    conn_sqlserver = get_sqlserver_connection()
    conn_mysql = get_mysql_connection()
    try:
        cursor_sql = conn_sqlserver.cursor()
        cursor_my = conn_mysql.cursor()

        # STEP 1: SET NULL cho Employee.DepartmentID trước khi xóa
        cursor_sql.execute(
            "UPDATE employees SET DepartmentID = NULL WHERE DepartmentID = ?", 
            (department_id,)
        )
        cursor_my.execute(
            "UPDATE employees SET DepartmentID = NULL WHERE DepartmentID = %s", 
            (department_id,)
        )

        # STEP 2: XÓA department
        cursor_sql.execute(
            "DELETE FROM departments WHERE DepartmentID = ?", 
            (department_id,)
        )
        cursor_my.execute(
            "DELETE FROM departments WHERE DepartmentID = %s", 
            (department_id,)
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
