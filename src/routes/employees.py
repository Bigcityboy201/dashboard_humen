# src/routes/employees.py

from flask import Blueprint, jsonify, request, g
from services.employee_service import get_all_employees
# Import logic validation nếu cần (src/services/validation.py)
from utils.response import wrap_success, wrap_error

employees_bp = Blueprint('employees', __name__)

@employees_bp.route('/employees', methods=['GET'])
def list_employees():
    """
    API Endpoint: GET /employees
    Lấy danh sách nhân viên có lọc và phân trang.
    """
    try:
        # Lấy tham số query
        department_id = request.args.get('department_id', type=int)
        status = request.args.get('status', type=str)
        page = request.args.get('page', default=1, type=int)
        size = request.args.get('size', default=10, type=int)
        
        # Gọi Service để lấy dữ liệu
        result = get_all_employees(
            department_id=department_id, 
            status=status, 
            page=page, 
            size=size
        )
        
        # Trả về kết quả theo định dạng Success của Java
        return jsonify(wrap_success(result, trace_id=getattr(g, 'trace_id', None))), 200

    except Exception as e:
        # Trả về lỗi thống nhất theo định dạng Error của Java
        return jsonify(wrap_error(code='INTERNAL_SERVER', message='Lỗi khi truy vấn danh sách nhân viên.', domain='employees', details={"error": str(e)}, trace_id=getattr(g, 'trace_id', None))), 500