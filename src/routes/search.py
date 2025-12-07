from flask import Blueprint, request, jsonify, g
from services.search_service import search_all
from utils.response import wrap_success, wrap_error

search_bp = Blueprint('search', __name__)

@search_bp.route('/search', methods=['GET'])
def global_search():
    """
    API Endpoint: GET /search?keyword={keyword}
    Tìm kiếm toàn hệ thống: nhân viên, phòng ban, chức vụ, lương, chấm công
    """
    try:
        keyword = request.args.get('keyword', type=str)
        if not keyword:
            return jsonify(wrap_error(
                code='BAD_REQUEST',
                message='Thiếu tham số keyword.',
                domain='search',
                details={},
                trace_id=getattr(g, 'trace_id', None)
            )), 400
        
        result = search_all(keyword)
        return jsonify(wrap_success(result, trace_id=getattr(g, 'trace_id', None))), 200
    except Exception as e:
        return jsonify(wrap_error(
            code='INTERNAL_SERVER',
            message='Lỗi khi tìm kiếm.',
            domain='search',
            details={"error": str(e)},
            trace_id=getattr(g, 'trace_id', None)
        )), 500





