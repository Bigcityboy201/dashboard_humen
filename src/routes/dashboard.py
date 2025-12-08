from flask import Blueprint, request, jsonify, g
from services.dashboard_service import get_dashboard_overview
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








