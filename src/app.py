# src/app.py
from flask import Flask, jsonify

# Import các Blueprint (định tuyến) từ thư mục src/routes/
from routes.employees import employees_bp 
# Bạn sẽ thêm các module khác sau: payroll_bp, attendance_bp, v.v.

def create_app():
    """Tạo và cấu hình ứng dụng Flask."""
    
    app = Flask(__name__)
    
    # 1. Cấu hình ứng dụng (ví dụ: biến cấu hình, khóa bí mật)
    # Nếu bạn có file config riêng, bạn sẽ tải chúng ở đây.
    app.config['SECRET_KEY'] = 'mot_chuoi_bi_mat_rat_dai_va_kho'
    
    # 2. Đăng ký các Blueprint (Định tuyến API)
    # Đây là nơi API /employees, /payroll, /dividends được thêm vào ứng dụng
    app.register_blueprint(employees_bp)
    # app.register_blueprint(payroll_bp, url_prefix='/payroll') # Ví dụ cho module khác

    # 3. Xử lý lỗi cơ bản (Tùy chọn)
    @app.errorhandler(404)
    def page_not_found(e):
        return jsonify({'message': 'Endpoint không tồn tại'}), 404

    return app

# Khởi tạo ứng dụng
app = create_app()

# Khối lệnh chạy ứng dụng (thường chỉ dùng khi chạy trực tiếp bằng python app.py)
# Khi dùng 'flask run' thì không cần khối này, nhưng có cũng không hại gì.
if __name__ == '__main__':
    app.run(debug=True)