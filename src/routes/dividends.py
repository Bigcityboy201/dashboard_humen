from flask import Blueprint, request, jsonify, g
from services.dividend_service import (
    get_dividends, create_dividend, get_dividend_by_id, delete_dividend
)
from utils.response import wrap_success, wrap_error

dividends_bp = Blueprint('dividends', __name__)

@dividends_bp.route('/dividends', methods=['GET'])
def list_dividends():
    """
    GET /dividends
    Lấy danh sách các đợt chi cổ tức
    """
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