from flask import Blueprint, request, jsonify, g
from services.report_service import (
    get_salary_report_by_year,
    get_attendance_report_by_year,
    get_financial_report
)
from utils.response import wrap_success, wrap_error

reports_bp = Blueprint('reports', __name__)

@reports_bp.route('/reports/salary', methods=['GET'])
def salary_report():
    """
    API Endpoint: GET /reports/salary?year={year}
    Báo cáo lương theo năm
    """
    try:
        year = request.args.get('year', type=str)
        if not year:
            return jsonify(wrap_error(
                code='BAD_REQUEST',
                message='Thiếu tham số year.',
                domain='reports',
                details={},
                trace_id=getattr(g, 'trace_id', None)
            )), 400
        
        result = get_salary_report_by_year(year)
        return jsonify(wrap_success(result, trace_id=getattr(g, 'trace_id', None))), 200
    except Exception as e:
        return jsonify(wrap_error(
            code='INTERNAL_SERVER',
            message='Lỗi khi tạo báo cáo lương.',
            domain='reports',
            details={"error": str(e)},
            trace_id=getattr(g, 'trace_id', None)
        )), 500

@reports_bp.route('/reports/attendance', methods=['GET'])
def attendance_report():
    """
    API Endpoint: GET /reports/attendance?year={year}
    Báo cáo chấm công theo năm
    """
    try:
        year = request.args.get('year', type=str)
        if not year:
            return jsonify(wrap_error(
                code='BAD_REQUEST',
                message='Thiếu tham số year.',
                domain='reports',
                details={},
                trace_id=getattr(g, 'trace_id', None)
            )), 400
        
        result = get_attendance_report_by_year(year)
        return jsonify(wrap_success(result, trace_id=getattr(g, 'trace_id', None))), 200
    except Exception as e:
        return jsonify(wrap_error(
            code='INTERNAL_SERVER',
            message='Lỗi khi tạo báo cáo chấm công.',
            domain='reports',
            details={"error": str(e)},
            trace_id=getattr(g, 'trace_id', None)
        )), 500

@reports_bp.route('/reports/financial', methods=['GET'])
def financial_report():
    """
    API Endpoint: GET /reports/financial?year={year}
    Báo cáo tài chính tổng hợp (lương + cổ tức) theo năm
    """
    try:
        year = request.args.get('year', type=str)
        if not year:
            return jsonify(wrap_error(
                code='BAD_REQUEST',
                message='Thiếu tham số year.',
                domain='reports',
                details={},
                trace_id=getattr(g, 'trace_id', None)
            )), 400
        
        result = get_financial_report(year)
        return jsonify(wrap_success(result, trace_id=getattr(g, 'trace_id', None))), 200
    except Exception as e:
        return jsonify(wrap_error(
            code='INTERNAL_SERVER',
            message='Lỗi khi tạo báo cáo tài chính.',
            domain='reports',
            details={"error": str(e)},
            trace_id=getattr(g, 'trace_id', None)
        )), 500








