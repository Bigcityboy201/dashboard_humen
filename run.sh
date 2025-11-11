#!/bin/bash

# Thiết lập môi trường và cấu hình DTB
source venv/Scripts/activate
export SQL_SERVER_CONN_STRING="DRIVER={ODBC Driver 17 for SQL Server};SERVER=DESKTOP-74S139L\SQLEXPRESS;DATABASE=HUMAN_2025;Trusted_Connection=Yes"
export MYSQL_PASSWORD="quangtruong1"
export MYSQL_DB_NAME="payroll"
export MYSQL_USER="root"
export MYSQL_HOST="127.0.0.1"
export PYTHONPATH=src

# Chạy ứng dụng Flask
python -m flask --app src.app run