from flask import Blueprint, request, jsonify, g
from services.position_service import (
    get_positions, get_position_by_id, create_position, update_position, delete_position
)
from utils.response import wrap_success, wrap_error

positions_bp = Blueprint('positions', __name__)

@positions_bp.route('/positions', methods=['GET'])
def list_positions():
    try:
        result = get_positions()
        return jsonify(wrap_success(result, trace_id=getattr(g, 'trace_id', None))), 200
    except Exception as e:
        return jsonify(wrap_error(code='INTERNAL_SERVER', message='Lỗi khi lấy danh sách chức vụ.', domain='positions', details={"error": str(e)}, trace_id=getattr(g, 'trace_id', None))), 500

@positions_bp.route('/positions/<int:position_id>', methods=['GET'])
def get_position(position_id):
    try:
        result = get_position_by_id(position_id)
        if not result:
            return jsonify(
                wrap_error(
                    code='NOT_FOUND',
                    message=f'Position with ID {position_id} not found',
                    domain='positions',
                    details={},
                    trace_id=getattr(g, 'trace_id', None)
                )
            ), 404
        return jsonify(wrap_success(result, trace_id=getattr(g, 'trace_id', None))), 200
    except Exception as e:
        return jsonify(
            wrap_error(
                code='INTERNAL_SERVER',
                message='Lỗi khi lấy chi tiết chức vụ.',
                domain='positions',
                details={"error": str(e)},
                trace_id=getattr(g, 'trace_id', None)
            )
        ), 500

# ---------------- CREATE ----------------
@positions_bp.route('/positions', methods=['POST'])
def add_position():
    try:
        data = request.json
        name = data.get("PositionName")
        new_id = create_position(name)

        # Lấy bản ghi vừa tạo để trả về đầy đủ thông tin
        new_position = get_position_by_id(new_id)

        return jsonify(
            wrap_success(
                new_position,
                trace_id=getattr(g, 'trace_id', None)
            )
        ), 201
    except Exception as e:
        return jsonify(
            wrap_error(
                code='INTERNAL_SERVER',
                message='Lỗi khi tạo chức vụ.',
                domain='positions',
                details={"error": str(e)},
                trace_id=getattr(g, 'trace_id', None)
            )
        ), 500
        
@positions_bp.route('/positions/<int:position_id>', methods=['PUT'])
def edit_position(position_id):
    try:
        data = request.json
        name = data.get("PositionName")
        update_position(position_id, name)

        # Lấy bản ghi sau khi cập nhật để trả về đầy đủ thông tin
        updated_position = get_position_by_id(position_id)

        if not updated_position:
            return jsonify(
                wrap_error(
                    code='NOT_FOUND',
                    message=f"Position with ID {position_id} not found",
                    domain='positions',
                    details={},
                    trace_id=getattr(g, 'trace_id', None)
                )
            ), 404

        return jsonify(
            wrap_success(
                updated_position,
                trace_id=getattr(g, 'trace_id', None)
            )
        ), 200
    except Exception as e:
        return jsonify(
            wrap_error(
                code='INTERNAL_SERVER',
                message='Lỗi khi cập nhật chức vụ.',
                domain='positions',
                details={"error": str(e)},
                trace_id=getattr(g, 'trace_id', None)
            )
        ), 500

@positions_bp.route('/positions/<int:position_id>', methods=['DELETE'])
def remove_position(position_id):
    try:
        rowcount = delete_position(position_id)
        if rowcount == 0:
            return jsonify(
                wrap_error(
                    code='NOT_FOUND',
                    message=f"Position with ID {position_id} not found",
                    domain='positions',
                    details={},
                    trace_id=getattr(g, 'trace_id', None)
                )
            ), 404

        return jsonify(
            wrap_success(
                {
                    "PositionID": position_id,
                    "message": f"Position with ID {position_id} deleted successfully"
                },
                trace_id=getattr(g, 'trace_id', None)
            )
        ), 200
    except Exception as e:
        return jsonify(
            wrap_error(
                code='INTERNAL_SERVER',
                message='Lỗi khi xóa chức vụ.',
                domain='positions',
                details={"error": str(e)},
                trace_id=getattr(g, 'trace_id', None)
            )
        ), 500