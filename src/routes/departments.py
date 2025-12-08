from flask import Blueprint, request, jsonify, g
from services.department_service import get_departments, get_department_by_id, create_department, update_department, delete_department
from services.employee_service import get_employees_by_department
from utils.response import wrap_success, wrap_error

departments_bp = Blueprint('departments', __name__)

@departments_bp.route('/departments', methods=['GET'])
def list_departments():
    # Kiểm tra nếu là browser request (có Accept: text/html) thì render HTML trực tiếp
    accept_header = request.headers.get('Accept', '')
    if 'text/html' in accept_header and 'application/json' not in accept_header:
        from flask import render_template
        return render_template('departments.html'), 200
    
    try:
        result = get_departments()
        return jsonify(wrap_success(result, trace_id=getattr(g, 'trace_id', None))), 200
    except Exception as e:
        return jsonify(wrap_error(
            code='INTERNAL_SERVER',
            message='Lỗi khi lấy danh sách phòng ban.',
            domain='departments',
            details={"error": str(e)},
            trace_id=getattr(g, 'trace_id', None)
        )), 500


@departments_bp.route('/departments/<int:department_id>', methods=['GET'])
def get_department(department_id):
    try:
        result = get_department_by_id(department_id)
        if not result:
            return jsonify(wrap_error(code='NOT_FOUND', message='Không tìm thấy phòng ban.', domain='departments', details={}, trace_id=getattr(g, 'trace_id', None))), 404
        return jsonify(wrap_success(result, trace_id=getattr(g, 'trace_id', None))), 200
    except Exception as e:
        return jsonify(wrap_error(code='INTERNAL_SERVER', message='Lỗi khi lấy chi tiết phòng ban.', domain='departments', details={"error": str(e)}, trace_id=getattr(g, 'trace_id', None))), 500


@departments_bp.route('/departments', methods=['POST'])
def add_department():
    try:
        data = request.json
        name = data.get("DepartmentName")  # Chỉ lấy tên
        new_id = create_department(name)   # Thêm phòng ban

        # Lấy lại toàn bộ thông tin vừa thêm
        new_department = get_department_by_id(new_id)
        if not new_department:
            return jsonify(
                wrap_error(
                    code='INTERNAL_SERVER',
                    message='Không tìm thấy phòng ban vừa tạo',
                    domain='departments',
                    details={},
                    trace_id=getattr(g, 'trace_id', None)
                )
            ), 500

        return jsonify(
            wrap_success(new_department, trace_id=getattr(g, 'trace_id', None))
        ), 201

    except Exception as e:
        return jsonify(
            wrap_error(
                code='INTERNAL_SERVER',
                message='Lỗi khi tạo phòng ban.',
                domain='departments',
                details={"error": str(e)},
                trace_id=getattr(g, 'trace_id', None)
            )
        ), 500


@departments_bp.route('/departments/<int:department_id>', methods=['PUT'])
def edit_department(department_id):
    try:
        data = request.json
        name = data.get("DepartmentName")

        # Cập nhật
        update_department(department_id, name)

        # Lấy lại dữ liệu mới của department
        updated_department = get_department_by_id(department_id)
        if not updated_department:
            return jsonify(
                wrap_error(
                    code='NOT_FOUND',
                    message=f"Department with ID {department_id} not found after update",
                    domain='departments',
                    details={},
                    trace_id=getattr(g, 'trace_id', None)
                )
            ), 404

        return jsonify(
            wrap_success(updated_department, trace_id=getattr(g, 'trace_id', None))
        ), 200

    except Exception as e:
        return jsonify(
            wrap_error(
                code='INTERNAL_SERVER',
                message='Lỗi khi cập nhật phòng ban.',
                domain='departments',
                details={"error": str(e)},
                trace_id=getattr(g, 'trace_id', None)
            )
        ), 500

@departments_bp.route('/departments/<int:department_id>', methods=['DELETE'])
def remove_department(department_id):
    try:
        rowcount = delete_department(department_id)
        if rowcount == 0:
            return jsonify(
                wrap_error(
                    code='NOT_FOUND',
                    message=f"Department with ID {department_id} not found",
                    domain='departments',
                    details={},
                    trace_id=getattr(g, 'trace_id', None)
                )
            ), 404

        return jsonify(
            wrap_success(
                {"DepartmentID": department_id, "message": f"Department with ID {department_id} deleted successfully"},
                trace_id=getattr(g, 'trace_id', None)
            )
        ), 200
    except Exception as e:
        return jsonify(
            wrap_error(
                code='INTERNAL_SERVER',
                message='Lỗi khi xóa phòng ban.',
                domain='departments',
                details={"error": str(e)},
                trace_id=getattr(g, 'trace_id', None)
            )
        ), 500


@departments_bp.route('/departments/<int:department_id>/employees', methods=['GET'])
def get_department_employees(department_id):
    """
    API Endpoint: GET /departments/{department_id}/employees
    Lấy danh sách nhân viên thuộc phòng ban cụ thể.
    """
    try:
        # Lấy tham số query cho pagination
        page = request.args.get('page', default=1, type=int)
        size = request.args.get('size', default=10, type=int)
        
        # Gọi service để lấy danh sách nhân viên theo department
        result = get_employees_by_department(department_id, page=page, size=size)
        
        return jsonify(wrap_success(result, trace_id=getattr(g, 'trace_id', None))), 200
        
    except Exception as e:
        return jsonify(wrap_error(
            code='INTERNAL_SERVER',
            message='Lỗi khi lấy danh sách nhân viên theo phòng ban.',
            domain='departments',
            details={"error": str(e)},
            trace_id=getattr(g, 'trace_id', None)
        )), 500

@departments_bp.route('/departments/statistics', methods=['GET'])
def get_department_statistics():
    """
    API Endpoint: GET /departments/statistics
    Lấy thống kê nhân viên theo phòng ban (Báo cáo HR)
    """
    try:
        from services.department_service import get_department_statistics
        result = get_department_statistics()
        return jsonify(wrap_success(result, trace_id=getattr(g, 'trace_id', None))), 200
    except Exception as e:
        return jsonify(wrap_error(
            code='INTERNAL_SERVER',
            message='Lỗi khi lấy thống kê phòng ban.',
            domain='departments',
            details={"error": str(e)},
            trace_id=getattr(g, 'trace_id', None)
        )), 500
