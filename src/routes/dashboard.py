from flask import Blueprint, request, jsonify, g
from services.dashboard_service import (
    get_dashboard_overview,
    get_dashboard_comparison,
    get_top_employees,
    get_top_departments,
    get_dashboard_trends
)
from utils.response import wrap_success, wrap_error

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/dashboard/overview', methods=['GET'])
def get_overview():
    """
    API Endpoint: GET /dashboard/overview
    Lấy thống kê tổng hợp cho trang chủ.
    """
    try:
        result = get_dashboard_overview()
        return jsonify(wrap_success(result, trace_id=getattr(g, 'trace_id', None))), 200
    except Exception as e:
        return jsonify(wrap_error(
            code='INTERNAL_SERVER',
            message='Lỗi khi lấy thống kê tổng hợp.',
            domain='dashboard',
            details={"error": str(e)},
            trace_id=getattr(g, 'trace_id', None)
        )), 500

@dashboard_bp.route('/dashboard/comparison', methods=['GET'])
def get_comparison():
    """
    API Endpoint: GET /dashboard/comparison
    So sánh dữ liệu hiện tại với kỳ trước (tháng trước, năm trước).
    """
    try:
        result = get_dashboard_comparison()
        return jsonify(wrap_success(result, trace_id=getattr(g, 'trace_id', None))), 200
    except Exception as e:
        return jsonify(wrap_error(
            code='INTERNAL_SERVER',
            message='Lỗi khi lấy dữ liệu so sánh.',
            domain='dashboard',
            details={"error": str(e)},
            trace_id=getattr(g, 'trace_id', None)
        )), 500

@dashboard_bp.route('/dashboard/top-employees', methods=['GET'])
def get_top_employees_endpoint():
    """
    API Endpoint: GET /dashboard/top-employees?limit=5
    Lấy top employees mới nhất (sắp xếp theo HireDate).
    """
    try:
        limit = request.args.get('limit', default=5, type=int)
        if limit > 20:
            limit = 20  # Giới hạn tối đa
        result = get_top_employees(limit)
        return jsonify(wrap_success(result, trace_id=getattr(g, 'trace_id', None))), 200
    except Exception as e:
        return jsonify(wrap_error(
            code='INTERNAL_SERVER',
            message='Lỗi khi lấy danh sách nhân viên mới nhất.',
            domain='dashboard',
            details={"error": str(e)},
            trace_id=getattr(g, 'trace_id', None)
        )), 500

@dashboard_bp.route('/dashboard/top-departments', methods=['GET'])
def get_top_departments_endpoint():
    """
    API Endpoint: GET /dashboard/top-departments?limit=5
    Lấy top departments có nhiều nhân viên nhất.
    """
    try:
        limit = request.args.get('limit', default=5, type=int)
        if limit > 20:
            limit = 20  # Giới hạn tối đa
        result = get_top_departments(limit)
        return jsonify(wrap_success(result, trace_id=getattr(g, 'trace_id', None))), 200
    except Exception as e:
        return jsonify(wrap_error(
            code='INTERNAL_SERVER',
            message='Lỗi khi lấy danh sách phòng ban.',
            domain='dashboard',
            details={"error": str(e)},
            trace_id=getattr(g, 'trace_id', None)
        )), 500

@dashboard_bp.route('/dashboard/trends', methods=['GET'])
def get_trends():
    """
    API Endpoint: GET /dashboard/trends?months=6
    Lấy xu hướng dữ liệu trong N tháng gần đây (mặc định 6 tháng).
    """
    try:
        months = request.args.get('months', default=6, type=int)
        if months > 12:
            months = 12  # Giới hạn tối đa 12 tháng
        if months < 1:
            months = 1
        result = get_dashboard_trends(months)
        return jsonify(wrap_success(result, trace_id=getattr(g, 'trace_id', None))), 200
    except Exception as e:
        return jsonify(wrap_error(
            code='INTERNAL_SERVER',
            message='Lỗi khi lấy dữ liệu xu hướng.',
            domain='dashboard',
            details={"error": str(e)},
            trace_id=getattr(g, 'trace_id', None)
        )), 500

@dashboard_bp.route('/dashboard/debug-data', methods=['GET'])
def debug_data():
    """
    API Endpoint: GET /dashboard/debug-data
    Debug endpoint để kiểm tra format dữ liệu thực tế trong database.
    """
    try:
        from services.dashboard_service import get_db_vendor, fetch_data_from_db
        
        vendor = get_db_vendor()
        
        # Lấy sample data từ salaries và attendance
        if vendor == "sqlserver":
            salary_query = "SELECT TOP 10 SalaryMonth, SUM(NetSalary) as Total FROM salaries GROUP BY SalaryMonth ORDER BY SalaryMonth DESC"
            attendance_query = "SELECT TOP 10 AttendanceMonth, SUM(WorkDays) as Total FROM attendance GROUP BY AttendanceMonth ORDER BY AttendanceMonth DESC"
        else:
            salary_query = "SELECT SalaryMonth, SUM(NetSalary) as Total FROM salaries GROUP BY SalaryMonth ORDER BY SalaryMonth DESC LIMIT 10"
            attendance_query = "SELECT AttendanceMonth, SUM(WorkDays) as Total FROM attendance GROUP BY AttendanceMonth ORDER BY AttendanceMonth DESC LIMIT 10"
        
        salary_data = fetch_data_from_db(salary_query, (), vendor)
        attendance_data = fetch_data_from_db(attendance_query, (), vendor)
        
        return jsonify(wrap_success({
            "vendor": vendor,
            "salary_samples": salary_data,
            "attendance_samples": attendance_data
        }, trace_id=getattr(g, 'trace_id', None))), 200
    except Exception as e:
        import traceback
        return jsonify(wrap_error(
            code='INTERNAL_SERVER',
            message='Lỗi khi debug dữ liệu.',
            domain='dashboard',
            details={"error": str(e), "traceback": traceback.format_exc()},
            trace_id=getattr(g, 'trace_id', None)
        )), 500











