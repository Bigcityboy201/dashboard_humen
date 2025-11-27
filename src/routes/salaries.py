from flask import Blueprint, request, jsonify, g
from services.salarie_service import (
    get_salaries, generate_salary, get_salary_by_id, 
    update_salary, delete_salary, get_my_salaries, get_salary_statistics
)
from utils.response import wrap_success, wrap_error

salaries_bp = Blueprint('salaries', __name__)

@salaries_bp.route('/salaries', methods=['GET'])
def list_salaries():
    """
    GET /salaries
    Lấy danh sách các bản ghi lương (Hỗ trợ filter theo EmployeeID, SalaryMonth)
    Chỉ xử lý khi có query params (API call), còn lại để route HTML xử lý
    """
    # Kiểm tra nếu là browser request (có Accept: text/html) và không có query params
    # thì render HTML trực tiếp
    accept_header = request.headers.get('Accept', '')
    has_query_params = request.args.get('employee_id') or request.args.get('month')
    
    if 'text/html' in accept_header and 'application/json' not in accept_header and not has_query_params:
        from flask import render_template
        return render_template('salaries.html'), 200
    
    try:
        employee_id = request.args.get('employee_id', type=int)
        salary_month = request.args.get('month')
        
        result = get_salaries(employee_id, salary_month)
        return jsonify(wrap_success(result, trace_id=getattr(g, 'trace_id', None))), 200
    except Exception as e:
        return jsonify(wrap_error(
            code='INTERNAL_SERVER',
            message='Lỗi khi lấy danh sách lương.',
            domain='salaries',
            details={"error": str(e)},
            trace_id=getattr(g, 'trace_id', None)
        )), 500

@salaries_bp.route('/salaries/generate', methods=['POST'])
def generate_salary_record():
    """
    POST /salaries/generate
    Tạo/Tính lương cho một tháng từ dữ liệu attendance và employees
    """
    try:
        data = request.json
        result = generate_salary(data)
        return jsonify(wrap_success(result, trace_id=getattr(g, 'trace_id', None))), 201
    except Exception as e:
        return jsonify(wrap_error(
            code='INTERNAL_SERVER',
            message='Lỗi khi tạo bản ghi lương.',
            domain='salaries',
            details={"error": str(e)},
            trace_id=getattr(g, 'trace_id', None)
        )), 500

@salaries_bp.route('/salaries/<int:salary_id>', methods=['GET'])
def get_salary(salary_id):
    """
    GET /salaries/{id}
    Xem chi tiết bản ghi lương
    """
    try:
        result = get_salary_by_id(salary_id)
        if not result:
            return jsonify(wrap_error(
                code='NOT_FOUND',
                message='Không tìm thấy bản ghi lương.',
                domain='salaries',
                details={},
                trace_id=getattr(g, 'trace_id', None)
            )), 404
        return jsonify(wrap_success(result, trace_id=getattr(g, 'trace_id', None))), 200
    except Exception as e:
        return jsonify(wrap_error(
            code='INTERNAL_SERVER',
            message='Lỗi khi lấy chi tiết lương.',
            domain='salaries',
            details={"error": str(e)},
            trace_id=getattr(g, 'trace_id', None)
        )), 500

@salaries_bp.route('/salaries/<int:salary_id>', methods=['PUT'])
def edit_salary(salary_id):
    """
    PUT /salaries/{id}
    Cập nhật bản ghi lương (điều chỉnh Bonus/Deductions)
    """
    try:
        data = request.json
        result = update_salary(salary_id, data)
        return jsonify(wrap_success(result, trace_id=getattr(g, 'trace_id', None))), 200
    except Exception as e:
        return jsonify(wrap_error(
            code='INTERNAL_SERVER',
            message='Lỗi khi cập nhật lương.',
            domain='salaries',
            details={"error": str(e)},
            trace_id=getattr(g, 'trace_id', None)
        )), 500

@salaries_bp.route('/salaries/<int:salary_id>', methods=['DELETE'])
def remove_salary(salary_id):
    """
    DELETE /salaries/{id}
    Xóa bản ghi lương
    """
    try:
        result = delete_salary(salary_id)
        return jsonify(wrap_success(result, trace_id=getattr(g, 'trace_id', None))), 200
    except Exception as e:
        return jsonify(wrap_error(
            code='INTERNAL_SERVER',
            message='Lỗi khi xóa lương.',
            domain='salaries',
            details={"error": str(e)},
            trace_id=getattr(g, 'trace_id', None)
        )), 500

@salaries_bp.route('/salaries/my', methods=['GET'])
def get_my_salary_history():
    """
    GET /salaries/my
    Lấy lịch sử lương của người dùng đang đăng nhập
    """
    try:
        # TODO: Lấy EmployeeID từ JWT token hoặc session
        # Hiện tại dùng employee_id từ query param
        employee_id = request.args.get('employee_id', type=int)
        if not employee_id:
            return jsonify(wrap_error(
                code='BAD_REQUEST',
                message='Thiếu employee_id.',
                domain='salaries',
                details={},
                trace_id=getattr(g, 'trace_id', None)
            )), 400
            
        result = get_my_salaries(employee_id)
        return jsonify(wrap_success(result, trace_id=getattr(g, 'trace_id', None))), 200
    except Exception as e:
        return jsonify(wrap_error(
            code='INTERNAL_SERVER',
            message='Lỗi khi lấy lịch sử lương.',
            domain='salaries',
            details={"error": str(e)},
            trace_id=getattr(g, 'trace_id', None)
        )), 500

@salaries_bp.route('/salaries/statistics', methods=['GET'])
def get_salary_stats():
    """
    GET /salaries/statistics
    Thống kê tổng chi phí lương theo tháng
    """
    try:
        salary_month = request.args.get('month')
        if not salary_month:
            return jsonify(wrap_error(
                code='BAD_REQUEST',
                message='Thiếu tham số month.',
                domain='salaries',
                details={},
                trace_id=getattr(g, 'trace_id', None)
            )), 400
            
        result = get_salary_statistics(salary_month)
        return jsonify(wrap_success(result, trace_id=getattr(g, 'trace_id', None))), 200
    except Exception as e:
        return jsonify(wrap_error(
            code='INTERNAL_SERVER',
            message='Lỗi khi thống kê lương.',
            domain='salaries',
            details={"error": str(e)},
            trace_id=getattr(g, 'trace_id', None)
        )), 500