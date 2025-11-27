from flask import Blueprint, request, jsonify, g
from services.dividend_service import (
    get_dividends, create_dividend, get_dividend_by_id, delete_dividend,update_dividend_record
)
from utils.response import wrap_success, wrap_error

dividends_bp = Blueprint('dividends', __name__)

@dividends_bp.route('/dividends', methods=['GET'])
def list_dividends():
    """
    GET /dividends
    Lấy danh sách các đợt chi cổ tức
    Chỉ xử lý khi có query params (API call), còn lại để route HTML xử lý
    """
    # Kiểm tra nếu là browser request (có Accept: text/html) và không có query params
    # thì render HTML trực tiếp
    accept_header = request.headers.get('Accept', '')
    has_query_params = len(request.args) > 0
    
    if 'text/html' in accept_header and 'application/json' not in accept_header and not has_query_params:
        from flask import render_template
        return render_template('dividends.html'), 200
    
    try:
        result = get_dividends()
        return jsonify(wrap_success(result, trace_id=getattr(g, 'trace_id', None))), 200
    except Exception as e:
        return jsonify(wrap_error(
            code='INTERNAL_SERVER',
            message='Lỗi khi lấy danh sách cổ tức.',
            domain='dividends',
            details={"error": str(e)},
            trace_id=getattr(g, 'trace_id', None)
        )), 500

@dividends_bp.route('/dividends', methods=['POST'])
def add_dividend():
    """
    POST /dividends
    Thêm mới một đợt chi cổ tức
    """
    try:
        data = request.json
        result = create_dividend(data)
        return jsonify(wrap_success(result, trace_id=getattr(g, 'trace_id', None))), 201
    except Exception as e:
        return jsonify(wrap_error(
            code='INTERNAL_SERVER',
            message='Lỗi khi tạo cổ tức.',
            domain='dividends',
            details={"error": str(e)},
            trace_id=getattr(g, 'trace_id', None)
        )), 500

@dividends_bp.route('/dividends/<int:dividend_id>', methods=['GET'])
def get_dividend(dividend_id):
    """
    GET /dividends/{id}
    Xem chi tiết đợt chi cổ tức
    """
    try:
        result = get_dividend_by_id(dividend_id)
        if not result:
            return jsonify(wrap_error(
                code='NOT_FOUND',
                message='Không tìm thấy bản ghi cổ tức.',
                domain='dividends',
                details={},
                trace_id=getattr(g, 'trace_id', None)
            )), 404
        return jsonify(wrap_success(result, trace_id=getattr(g, 'trace_id', None))), 200
    except Exception as e:
        return jsonify(wrap_error(
            code='INTERNAL_SERVER',
            message='Lỗi khi lấy chi tiết cổ tức.',
            domain='dividends',
            details={"error": str(e)},
            trace_id=getattr(g, 'trace_id', None)
        )), 500

@dividends_bp.route('/dividends/<int:dividend_id>', methods=['DELETE'])
def remove_dividend(dividend_id):
    """
    DELETE /dividends/{id}
    Xóa đợt chi cổ tức
    """
    try:
        result = delete_dividend(dividend_id)
        return jsonify(wrap_success(result, trace_id=getattr(g, 'trace_id', None))), 200
    except Exception as e:
        return jsonify(wrap_error(
            code='INTERNAL_SERVER',
            message='Lỗi khi xóa cổ tức.',
            domain='dividends',
            details={"error": str(e)},
            trace_id=getattr(g, 'trace_id', None)
        )), 500
@dividends_bp.route('/dividends/<int:dividend_id>', methods=['PUT'])
def update_dividend(dividend_id):
    """
    PUT /dividends/{id}
    Cập nhật thông tin một đợt chi cổ tức
    """
    try:
        data = request.json
        result = update_dividend_record(dividend_id, data)
        return jsonify(wrap_success(result, trace_id=getattr(g, 'trace_id', None))), 200
    except Exception as e:
        return jsonify(wrap_error(
            code='INTERNAL_SERVER',
            message='Lỗi khi cập nhật cổ tức.',
            domain='dividends',
            details={"error": str(e)},
            trace_id=getattr(g, 'trace_id', None)
        )), 500
