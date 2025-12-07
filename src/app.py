# src/app.py
from flask import Flask, jsonify, g, request, render_template, url_for, send_from_directory
import uuid
import os
from dotenv import load_dotenv
from typing import Tuple


# Load biến môi trường từ file .env
load_dotenv()

# Import các Blueprint (định tuyến)
from routes.employees import employees_bp
# Bạn sẽ thêm các module khác sau: payroll_bp, attendance_bp, v.v.
from routes.departments import departments_bp
from routes.positions import positions_bp
from routes.salaries import salaries_bp
from routes.dividends import dividends_bp
from routes.attendance import attendance_bp
from routes.dashboard import dashboard_bp
from routes.search import search_bp
from routes.reports import reports_bp

from utils.response import wrap_success, wrap_error
from clients.java_client import JavaClient


def create_app():
    """Tạo và cấu hình ứng dụng Flask."""
    # Lấy đường dẫn tuyệt đối của thư mục chứa app.py
    base_dir = os.path.dirname(os.path.abspath(__file__))
    app = Flask(__name__, 
                template_folder=os.path.join(base_dir, 'templates'), 
                static_folder=os.path.join(base_dir, 'static'),
                static_url_path='/static')

    # 1. Cấu hình ứng dụng (biến cấu hình, bí mật)
    app.config['SECRET_KEY'] = 'mot_chuoi_bi_mat_rat_dai_va_kho'
    app.config['JAVA_BASE_URL'] = os.getenv('JAVA_BASE_URL', 'http://localhost:8080')
    app.config['SQL_SERVER_CONN_STRING'] = os.getenv("SQL_SERVER_CONN_STRING")  # nếu dùng SQL Server

    # 2. Đăng ký Blueprint (API routes) trước
    app.register_blueprint(employees_bp) 
    app.register_blueprint(departments_bp)
    app.register_blueprint(positions_bp)
    app.register_blueprint(salaries_bp)
    app.register_blueprint(dividends_bp)
    app.register_blueprint(attendance_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(search_bp)
    app.register_blueprint(reports_bp)

    # 3. Đăng ký route HTML sau (để ưu tiên render HTML khi truy cập từ browser)
    # Trong Flask, route được match theo thứ tự LIFO (Last In First Out)
    @app.route('/login')
    def login_page():
        return render_template('login.html')

    @app.route('/')
    def index():
        return render_template('index.html')

    @app.route('/employees')
    def employees_page():
        return render_template('employees.html')

    @app.route('/departments')
    def departments_page():
        return render_template('departments.html')

    @app.route('/positions')
    def positions_page():
        return render_template('positions.html')

    @app.route('/salaries')
    def salaries_page():
        return render_template('salaries.html')

    @app.route('/attendance')
    def attendance_page():
        return render_template('attendance.html')

    @app.route('/dividends')
    def dividends_page():
        return render_template('dividends.html')

    @app.route('/users')
    def users_page():
        return render_template('users.html')

    @app.route('/profile')
    def profile_page():
        return render_template('profile.html')

    # 3. Xử lý lỗi 404
    @app.errorhandler(404)
    def page_not_found(e):
        trace_id = getattr(g, 'trace_id', None)
        
        # Xử lý đặc biệt cho browser request (có Accept: text/html)
        accept_header = request.headers.get('Accept', '')
        if 'text/html' in accept_header and 'application/json' not in accept_header:
            # Render HTML tương ứng cho các route
            if request.path == '/':
                return render_template('index.html'), 200
            elif request.path == '/employees':
                return render_template('employees.html'), 200
            elif request.path == '/departments':
                return render_template('departments.html'), 200
            elif request.path == '/positions':
                return render_template('positions.html'), 200
            elif request.path == '/salaries':
                return render_template('salaries.html'), 200
            elif request.path == '/attendance':
                return render_template('attendance.html'), 200
            elif request.path == '/dividends':
                return render_template('dividends.html'), 200
            elif request.path == '/users':
                return render_template('users.html'), 200
            elif request.path == '/profile':
                return render_template('profile.html'), 200
        
        # Trả về JSON cho tất cả các trường hợp khác
        return jsonify(
            wrap_error(
                code='NOT_FOUND',
                message='Endpoint không tồn tại',
                domain='routing',
                details=None,
                trace_id=trace_id
            )
        ), 404

    # Context processor để debug static files và cache busting
    @app.context_processor
    def inject_static_path():
        import time
        return dict(
            static_path=app.static_url_path,
            cache_bust=int(time.time())  # Cache busting
        )
    
    # Tạo trace_id cho mỗi request
    @app.before_request
    def ensure_request_id():
        incoming = request.headers.get('X-Request-Id')
        g.trace_id = incoming if incoming else str(uuid.uuid4())

    # Endpoint test gọi sang Java
    @app.get('/java/health')
    def java_health():
        client = JavaClient(base_url=app.config['JAVA_BASE_URL'], trace_id=g.trace_id)
        ok, status_code, payload = client.get('/api/v1/health')

        if ok is True and isinstance(payload, dict) and payload.get('operationType') == 'Success':
            payload['traceId'] = payload.get('traceId') or g.trace_id
            return jsonify(payload), status_code

        if ok is False and isinstance(payload, dict) and payload.get('operationType') == 'Failure':
            payload['traceId'] = payload.get('traceId') or g.trace_id
            return jsonify(payload), status_code

        if ok:
            return jsonify(wrap_success(payload, trace_id=g.trace_id)), status_code

        return jsonify(
            wrap_error(
                code='INTERNAL_SERVER',
                message='Java call failed',
                domain='java',
                details=payload,
                trace_id=g.trace_id,
            )
        ), status_code or 500

   
    return app


# Khởi tạo ứng dụng
app = create_app()

if __name__ == '__main__':
    app.run(debug=True, port=5000)

