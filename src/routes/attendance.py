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
    Chỉ xử lý khi có query params (API call), còn lại để route HTML xử lý
    """
    # Kiểm tra nếu là browser request (có Accept: text/html) và không có query params
    # thì render HTML trực tiếp
    accept_header = request.headers.get('Accept', '')
    has_query_params = request.args.get('employee_id') or request.args.get('year')
    
    if 'text/html' in accept_header and 'application/json' not in accept_header and not has_query_params:
        from flask import render_template
        return render_template('attendance.html'), 200
    
    try:
        employee_id = request.args.get('employee_id', type=int)
        year = request.args.get('year', type=int)
        
        result = get_attendances(employee_id, year=year)
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
        if not data:
            return jsonify(wrap_error(
                code='BAD_REQUEST',
                message='Thiếu dữ liệu gửi lên.',
                domain='attendance',
                details={},
                trace_id=getattr(g, 'trace_id', None)
            )), 400
        
        # Log để debug
        print(f"Creating attendance with data: {data}")
        
        result = create_attendance(data)
        return jsonify(wrap_success(result, trace_id=getattr(g, 'trace_id', None))), 201
    except Exception as e:
        # Log lỗi chi tiết
        import traceback
        error_trace = traceback.format_exc()
        print(f"Error creating attendance: {str(e)}")
        print(f"Traceback: {error_trace}")
        
        # Trả về error message rõ ràng hơn
        error_message = str(e)
        if "Lỗi DB" in error_message:
            error_message = f"Lỗi kết nối database: {error_message}"
        elif "Thiếu" in error_message:
            error_message = error_message
        elif "đã tồn tại" in error_message.lower() or "duplicate" in error_message.lower():
            error_message = error_message
        else:
            error_message = f"Lỗi khi tạo chấm công: {error_message}"
        
        return jsonify(wrap_error(
            code='INTERNAL_SERVER',
            message=error_message,
            domain='attendance',
            details={"error": str(e), "traceback": error_trace},
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
        year = request.args.get('year', type=int)
        if not year:
            return jsonify(wrap_error(
                code='BAD_REQUEST',
                message='Thiếu tham số year.',
                domain='attendance',
                details={},
                trace_id=getattr(g, 'trace_id', None)
            )), 400
        result = get_attendance_statistics(year=year)
        return jsonify(wrap_success(result, trace_id=getattr(g, 'trace_id', None))), 200
    except Exception as e:
        return jsonify(wrap_error(
            code='INTERNAL_SERVER',
            message='Lỗi khi thống kê chấm công.',
            domain='attendance',
            details={"error": str(e)},
            trace_id=getattr(g, 'trace_id', None)
        )), 500