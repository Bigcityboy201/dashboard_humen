# src/routes/employees.py

from flask import Blueprint, jsonify, request, g
from services.employee_service import get_all_employees,create_employee_transaction,delete_employee_service,get_employee_by_id
# Import logic validation nếu cần (src/services/validation.py)
from utils.response import wrap_success, wrap_error

employees_bp = Blueprint('employees', __name__)

@employees_bp.route('/employees', methods=['GET'])
def list_employees():
    """
    API Endpoint: GET /employees
    Lấy danh sách nhân viên có lọc và phân trang.
    """
    # Kiểm tra nếu là browser request (có Accept: text/html) thì render HTML trực tiếp
    # Bất kể có query params hay không (query params sẽ được xử lý bởi JavaScript)
    accept_header = request.headers.get('Accept', '')
    
    if 'text/html' in accept_header and 'application/json' not in accept_header:
        from flask import render_template
        return render_template('employees.html'), 200
    
    try:
        # Lấy tham số query
        department_id = request.args.get('department_id', type=int)
        position_id = request.args.get('position_id', type=int)
        status = request.args.get('status', type=str)
        keyword = request.args.get('keyword', type=str)
        page = request.args.get('page', default=1, type=int)
        size = request.args.get('size', default=10, type=int)
        
        # Gọi Service để lấy dữ liệu
        result = get_all_employees(
            department_id=department_id,
            position_id=position_id,
            status=status,
            keyword=keyword,
            page=page, 
            size=size
        )
        
        # Trả về kết quả theo định dạng Success của Java
        return jsonify(wrap_success(result, trace_id=getattr(g, 'trace_id', None))), 200

    except Exception as e:
        # Trả về lỗi thống nhất theo định dạng Error của Java
        return jsonify(wrap_error(code='INTERNAL_SERVER', message='Lỗi khi truy vấn danh sách nhân viên.', domain='employees', details={"error": str(e)}, trace_id=getattr(g, 'trace_id', None))), 500
    
    
@employees_bp.route('/employees', methods=['POST'])
def create_new_employee():
    """
    API Endpoint: POST /employees
    Thêm mới nhân viên cùng lương khởi điểm.
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify(wrap_error(
                code='BAD_REQUEST',
                message='Thiếu dữ liệu gửi lên.',
                domain='employees',
                trace_id=getattr(g, 'trace_id', None)
            )), 400

        # Gọi service để xử lý thêm nhân viên
        new_employee = create_employee_transaction(data)

        return jsonify(wrap_success(new_employee, trace_id=getattr(g, 'trace_id', None))), 201

    except Exception as e:
        return jsonify(wrap_error(
            code='INTERNAL_SERVER',
            message='Lỗi khi thêm mới nhân viên.',
            domain='employees',
            details={"error": str(e)},
            trace_id=getattr(g, 'trace_id', None)
        )), 500
    
@employees_bp.route('/employees/<int:employee_id>', methods=['DELETE'])
def delete_employee(employee_id):
    """
    API Endpoint: DELETE /employees/{employee_id}
    Xóa nhân viên theo ID (AUTO CASCADE cả MySQL + SQL Server)
    """
    try:
        from services.employee_service import delete_employee_service

        result = delete_employee_service(employee_id)

        if result.get('success'):
            # Không truyền message nếu wrap_success không hỗ trợ
            return jsonify(wrap_success(
                data={"message": "Xóa nhân viên thành công."},  # gói vào data
                trace_id=getattr(g, 'trace_id', None)
            )), 200
        else:
            return jsonify(wrap_error(
                code='NOT_FOUND',
                message=result.get('message', 'Không tìm thấy nhân viên.'),
                domain='employees',
                trace_id=getattr(g, 'trace_id', None)
            )), 404

    except Exception as e:
        return jsonify(wrap_error(
            code='INTERNAL_SERVER',
            message='Lỗi khi xóa nhân viên.',
            domain='employees',
            details={"error": str(e)},
            trace_id=getattr(g, 'trace_id', None)
        )), 500

@employees_bp.route('/employees/<int:employee_id>', methods=['GET'])
def get_employee_detail(employee_id):
    """
    API Endpoint: GET /employees/{employee_id}
    Lấy thông tin chi tiết nhân viên theo ID.
    """
    try:
        # Import service function
        from services.employee_service import get_employee_by_id

        # Gọi service để lấy thông tin nhân viên
        result = get_employee_by_id(employee_id)

        if result.get('success'):
            return jsonify(wrap_success(
                data=result.get('employee'),
                trace_id=getattr(g, 'trace_id', None)
            )), 200
        else:
            return jsonify(wrap_error(
                code='NOT_FOUND',
                message=result.get('message', 'Không tìm thấy nhân viên.'),
                domain='employees',
                trace_id=getattr(g, 'trace_id', None)
            )), 404

    except Exception as e:
        return jsonify(wrap_error(
            code='INTERNAL_SERVER',
            message='Lỗi khi lấy thông tin nhân viên.',
            domain='employees',
            details={"error": str(e)},
            trace_id=getattr(g, 'trace_id', None)
        )), 500
    
@employees_bp.route('/employees/<int:employee_id>', methods=['PUT'])
def update_employee(employee_id):
    """
    API Endpoint: PUT /employees/{employee_id}
    Cập nhật thông tin nhân viên theo ID.
    """
    try:
        # Import service function
        from services.employee_service import update_employee_service

        # Lấy dữ liệu từ request body
        data = request.get_json()
        if not data:
            return jsonify(wrap_error(
                code='BAD_REQUEST',
                message='Thiếu dữ liệu gửi lên.',
                domain='employees',
                trace_id=getattr(g, 'trace_id', None)
            )), 400

        # Gọi service để cập nhật nhân viên
        result = update_employee_service(employee_id, data)

        if result.get('success'):
          return jsonify(wrap_success(
    data={
        "employee": result.get('employee'),
        "message": result.get('message')
    },
    trace_id=getattr(g, 'trace_id', None)
)), 200

        else:
            return jsonify(wrap_error(
                code='BAD_REQUEST',
                message=result.get('message', 'Cập nhật thất bại.'),
                domain='employees',
                trace_id=getattr(g, 'trace_id', None)
            )), 400

    except Exception as e:
        return jsonify(wrap_error(
            code='INTERNAL_SERVER',
            message='Lỗi khi cập nhật nhân viên.',
            domain='employees',
            details={"error": str(e)},
            trace_id=getattr(g, 'trace_id', None)
        )), 500
        
#thiếu xóa mềm