from flask import Blueprint, request, jsonify, g
from services.attendance_service import (
    get_attendances, create_attendance, get_attendance_by_id,
    update_attendance, delete_attendance, get_attendance_statistics
)
from utils.response import wrap_success, wrap_error

attendance_bp = Blueprint('attendance', __name__)

@attendance_bp.route('/attendance', methods=['GET'])
def list_attendances():
    """
    GET /attendance
    Lấy dữ liệu chấm công. (Hỗ trợ filter theo EmployeeID, AttendanceMonth)
    """
    try:
        employee_id = request.args.get('employee_id', type=int)
        attendance_month = request.args.get('month')
        
        result = get_attendances(employee_id, attendance_month)
        return jsonify(wrap_success(result, trace_id=getattr(g, 'trace_id', None))), 200
    except Exception as e:
        return jsonify(wrap_error(
            code='INTERNAL_SERVER',
            message='Lỗi khi lấy danh sách chấm công.',
            domain='attendance',
            details={"error": str(e)},
            trace_id=getattr(g, 'trace_id', None)
        )), 500

@attendance_bp.route('/attendance', methods=['POST'])
def create_attendance_record():
    """
    POST /attendance
    Tạo một bản ghi Timesheet (bảng chấm công) cho nhân viên/tháng.
    """
    try:
        data = request.json
        result = create_attendance(data)
        return jsonify(wrap_success(result, trace_id=getattr(g, 'trace_id', None))), 201
    except Exception as e:
        return jsonify(wrap_error(
            code='INTERNAL_SERVER',
            message='Lỗi khi tạo bản ghi chấm công.',
            domain='attendance',
            details={"error": str(e)},
            trace_id=getattr(g, 'trace_id', None)
        )), 500

@attendance_bp.route('/attendance/<int:attendance_id>', methods=['GET'])
def get_attendance(attendance_id):
    """
    GET /attendance/{id}
    Xem chi tiết bản ghi chấm công.
    """
    try:
        result = get_attendance_by_id(attendance_id)
        if not result:
            return jsonify(wrap_error(
                code='NOT_FOUND',
                message='Không tìm thấy bản ghi chấm công.',
                domain='attendance',
                details={},
                trace_id=getattr(g, 'trace_id', None)
            )), 404
        return jsonify(wrap_success(result, trace_id=getattr(g, 'trace_id', None))), 200
    except Exception as e:
        return jsonify(wrap_error(
            code='INTERNAL_SERVER',
            message='Lỗi khi lấy chi tiết chấm công.',
            domain='attendance',
            details={"error": str(e)},
            trace_id=getattr(g, 'trace_id', None)
        )), 500

@attendance_bp.route('/attendance/<int:attendance_id>', methods=['PUT'])
def edit_attendance(attendance_id):
    """
    PUT /attendance/{id}
    Cập nhật bản ghi chấm công (ví dụ: điều chỉnh ngày nghỉ phép, ngày vắng mặt).
    """
    try:
        data = request.json
        result = update_attendance(attendance_id, data)
        return jsonify(wrap_success(result, trace_id=getattr(g, 'trace_id', None))), 200
    except Exception as e:
        return jsonify(wrap_error(
            code='INTERNAL_SERVER',
            message='Lỗi khi cập nhật chấm công.',
            domain='attendance',
            details={"error": str(e)},
            trace_id=getattr(g, 'trace_id', None)
        )), 500

@attendance_bp.route('/attendance/<int:attendance_id>', methods=['DELETE'])
def remove_attendance(attendance_id):
    """
    DELETE /attendance/{id}
    Xóa bản ghi chấm công.
    """
    try:
        result = delete_attendance(attendance_id)
        return jsonify(wrap_success(result, trace_id=getattr(g, 'trace_id', None))), 200
    except Exception as e:
        return jsonify(wrap_error(
            code='INTERNAL_SERVER',
            message='Lỗi khi xóa chấm công.',
            domain='attendance',
            details={"error": str(e)},
            trace_id=getattr(g, 'trace_id', None)
        )), 500

@attendance_bp.route('/attendance/statistics', methods=['GET'])
def get_attendance_stats():
    """
    GET /attendance/statistics
    Thống kê tổng số ngày công, vắng mặt theo tháng/quý.
    """
    try:
        attendance_month = request.args.get('month')
        result = get_attendance_statistics(attendance_month)
        return jsonify(wrap_success(result, trace_id=getattr(g, 'trace_id', None))), 200
    except Exception as e:
        return jsonify(wrap_error(
            code='INTERNAL_SERVER',
            message='Lỗi khi thống kê chấm công.',
            domain='attendance',
            details={"error": str(e)},
            trace_id=getattr(g, 'trace_id', None)
        )), 500