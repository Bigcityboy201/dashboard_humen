# 📋 HƯỚNG DẪN TEST API TRÊN POSTMAN

## 🔧 Cấu hình cơ bản

### Base URL
```
http://localhost:8080
```

### Python API Base URL (qua proxy)
```
http://localhost:5000
```

---

## 🔐 1. AUTHENTICATION ENDPOINTS (Public - Không cần token)

### 1.1. Đăng nhập (Sign In)
**Endpoint:** `POST /auth/signIn`

**Headers:**
```
Content-Type: application/json
```

**Body (JSON):**
```json
{
  "userName": "quangtruongngo2012004",
  "password": "quangtruong1"
}
```

**Response thành công:**
```json
{
  "data": {
    "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "expiredDate": "2024-01-15T10:30:00.000+00:00",
    "user": {
      "id": 1,
      "userName": "quangtruongngo2012004",
      "email": "quangtruong2012004@gmail.com",
      "role": "ADMIN"
    }
  },
  "message": "Success",
  "code": "OK"
}
```

**Lưu ý:** Copy `token` từ response để dùng cho các request sau.

---

### 1.2. Đăng xuất (Logout)
**Endpoint:** `POST /auth/logout`

**Headers:**
```
Authorization: Bearer {token}
Content-Type: application/json
```

**Response:**
```json
{
  "data": "Logout successful",
  "message": "Success",
  "code": "OK"
}
```

---

## 🏥 2. HEALTH CHECK (Public)

**Endpoint:** `GET /api/v1/health`

**Headers:** Không cần

**Response:**
```json
{
  "status": "UP"
}
```

---

## 👤 3. USER MANAGEMENT ENDPOINTS (Chỉ ADMIN)

**Lưu ý:** Tất cả endpoint này cần:
- Header: `Authorization: Bearer {token}`
- Role: `ADMIN`

### 3.1. Lấy danh sách users (có phân trang)
**Endpoint:** `GET /users?page=0&size=10`

**Query Parameters:**
- `page` (optional, default: 0): Số trang
- `size` (optional, default: 10): Số lượng mỗi trang

### 3.2. Tạo user mới
**Endpoint:** `POST /users`

**Body (JSON):**
```json
{
  "userName": "newuser",
  "password": "password123",
  "email": "newuser@example.com",
  "role": "HR_MANAGER"
}
```

### 3.3. Cập nhật trạng thái user
**Endpoint:** `PUT /users/{id}/status`

**Body (JSON):**
```json
{
  "isActive": false
}
```

### 3.4. Xóa user
**Endpoint:** `DELETE /users/{id}`

---

## 📝 4. PROFILE ENDPOINTS (ADMIN hoặc HR_MANAGER)

**Lưu ý:** Tất cả endpoint này cần:
- Header: `Authorization: Bearer {token}`
- Role: `ADMIN` hoặc `HR_MANAGER`

### 4.1. Lấy thông tin profile hiện tại
**Endpoint:** `GET /profile`

### 4.2. Cập nhật profile hiện tại
**Endpoint:** `PUT /profile`

**Body (JSON):**
```json
{
  "email": "newemail@example.com",
  "password": "newpassword123"
}
```

---

## 🐍 5. PYTHON API PROXY ENDPOINTS

**⚠️ QUAN TRỌNG - Cách Proxy hoạt động:**

Java Spring Boot đóng vai trò là **Proxy Server** để forward request sang Python API:

1. **Bạn gọi:** `http://localhost:8080/api/python/employees`
2. **Java Proxy nhận request** tại `/api/python/**`
3. **Java bỏ prefix** `/api/python` → còn lại `/employees`
4. **Java forward** sang: `http://localhost:5000/employees`

**❌ SAI:** `http://localhost:5000/api/python/employees` 
- Python API không có route `/api/python/employees`
- Python API chỉ có route `/employees`, `/departments`, `/salaries`, v.v.

**✅ ĐÚNG:** `http://localhost:8080/api/python/employees`
- Java proxy sẽ tự động forward sang `http://localhost:5000/employees`

**Lưu ý:** Tất cả endpoint này cần:
- Header: `Authorization: Bearer {token}`
- Python API server phải đang chạy tại `http://localhost:5000`
- **LUÔN gọi qua Java proxy** tại `http://localhost:8080/api/python/**`

### 5.1. HR MANAGEMENT ENDPOINTS (HR_MANAGER hoặc ADMIN)

#### 5.1.1. Employees (Nhân viên)
- `GET /api/python/employees` - Lấy danh sách nhân viên
- `POST /api/python/employees` - Tạo nhân viên mới
- `GET /api/python/employees/{id}` - Lấy thông tin nhân viên theo ID
- `PUT /api/python/employees/{id}` - Cập nhật nhân viên
- `DELETE /api/python/employees/{id}` - Xóa nhân viên

**Ví dụ POST /api/python/employees:**
```json
{
  "name": "Nguyễn Văn A",
  "email": "nguyenvana@example.com",
  "department_id": 1,
  "position_id": 1,
  "salary": 10000000
}
```

#### 5.1.2. Attendance (Chấm công)
- `GET /api/python/attendance` - Lấy danh sách chấm công
- `POST /api/python/attendance` - Tạo bản ghi chấm công
- `GET /api/python/attendance/{id}` - Lấy thông tin chấm công theo ID
- `PUT /api/python/attendance/{id}` - Cập nhật chấm công
- `DELETE /api/python/attendance/{id}` - Xóa chấm công
- `GET /api/python/attendance/statistics` - Thống kê chấm công

**Ví dụ POST /api/python/attendance:**
```json
{
  "employee_id": 1,
  "date": "2024-01-15",
  "check_in": "08:00:00",
  "check_out": "17:00:00",
  "status": "present"
}
```

#### 5.1.3. Departments (Phòng ban)
- `GET /api/python/departments` - Lấy danh sách phòng ban
- `POST /api/python/departments` - Tạo phòng ban mới
- `GET /api/python/departments/{id}` - Lấy thông tin phòng ban theo ID
- `PUT /api/python/departments/{id}` - Cập nhật phòng ban
- `DELETE /api/python/departments/{id}` - Xóa phòng ban
- `GET /api/python/departments/{id}/employees` - Lấy danh sách nhân viên trong phòng ban

**Ví dụ POST /api/python/departments:**
```json
{
  "name": "Phòng Nhân Sự",
  "description": "Quản lý nhân sự công ty"
}
```

#### 5.1.4. Positions (Chức vụ)
- `GET /api/python/positions` - Lấy danh sách chức vụ
- `POST /api/python/positions` - Tạo chức vụ mới
- `GET /api/python/positions/{id}` - Lấy thông tin chức vụ theo ID
- `PUT /api/python/positions/{id}` - Cập nhật chức vụ
- `DELETE /api/python/positions/{id}` - Xóa chức vụ
- `GET /api/python/positions/{id}/employees` - Lấy danh sách nhân viên có chức vụ này

**Ví dụ POST /api/python/positions:**
```json
{
  "name": "Trưởng phòng",
  "description": "Chức vụ quản lý phòng ban",
  "base_salary": 15000000
}
```

---

### 5.2. PAYMENT ENDPOINTS (PAYROLL_MANAGER hoặc ADMIN)

#### 5.2.1. Salaries (Lương)
- `GET /api/python/salaries` - Lấy danh sách lương
- `POST /api/python/salaries` - Tạo bản ghi lương
- `GET /api/python/salaries/{id}` - Lấy thông tin lương theo ID
- `PUT /api/python/salaries/{id}` - Cập nhật lương
- `DELETE /api/python/salaries/{id}` - Xóa lương

**Ví dụ POST /api/python/salaries:**
```json
{
  "employee_id": 1,
  "month": 1,
  "year": 2024,
  "base_salary": 10000000,
  "bonus": 2000000,
  "deduction": 500000,
  "total": 11500000
}
```

#### 5.2.2. Dividends (Cổ tức)
- `GET /api/python/dividends` - Lấy danh sách cổ tức
- `POST /api/python/dividends` - Tạo bản ghi cổ tức
- `GET /api/python/dividends/{id}` - Lấy thông tin cổ tức theo ID
- `PUT /api/python/dividends/{id}` - Cập nhật cổ tức
- `DELETE /api/python/dividends/{id}` - Xóa cổ tức

**Ví dụ POST /api/python/dividends:**
```json
{
  "employee_id": 1,
  "year": 2024,
  "quarter": 1,
  "amount": 5000000,
  "payment_date": "2024-04-01"
}
```

---

### 5.3. CÁC ENDPOINT KHÁC (Chỉ ADMIN)

Tất cả endpoint khác trong `/api/python/**` (không thuộc các nhóm trên) chỉ dành cho ADMIN.

---

## ⚠️ 6. XỬ LÝ LỖI

### 6.1. Lỗi Connection Refused (Python API không chạy)
**Status Code:** `503 Service Unavailable`

**Response:**
```json
{
  "message": "Python API server không khả dụng. Vui lòng kiểm tra server đã chạy chưa.",
  "code": "INTERNAL_SERVER",
  "domain": "python-proxy",
  "details": {
    "error": "Connection refused: http://localhost:5000",
    "pythonApiUrl": "http://localhost:5000"
  },
  "traceId": "..."
}
```

### 6.2. Lỗi Unauthorized (Chưa đăng nhập)
**Status Code:** `401 Unauthorized`

**Response:**
```json
{
  "message": "Unauthorized",
  "code": "UNAUTHORIZED"
}
```

### 6.3. Lỗi Forbidden (Không đủ quyền)
**Status Code:** `403 Forbidden`

**Response:**
```json
{
  "message": "Access Denied",
  "code": "FORBIDDEN"
}
```

---

## 📝 7. CÁCH SỬ DỤNG TRONG POSTMAN

### Bước 1: Đăng nhập để lấy token
1. Tạo request mới: `POST http://localhost:8080/auth/signIn`
2. Chọn tab **Body** → **raw** → **JSON**
3. Nhập body:
```json
{
  "userName": "quangtruongngo2012004",
  "password": "quangtruong1"
}
```
4. Click **Send**
5. Copy `token` từ response

### Bước 2: Sử dụng token cho các request khác
1. Tạo request mới (ví dụ: `GET http://localhost:8080/api/python/employees`)
2. Chọn tab **Headers**
3. Thêm header:
   - Key: `Authorization`
   - Value: `Bearer {token}` (thay {token} bằng token đã copy)
4. Click **Send**

### Bước 3: Tạo Environment trong Postman (Tùy chọn)
Để dễ quản lý, bạn có thể tạo Environment:

1. Click vào **Environments** → **+**
2. Tạo biến:
   - `base_url`: `http://localhost:8080`
   - `token`: (để trống, sẽ set sau khi login)
3. Trong request, sử dụng: `{{base_url}}/auth/signIn`
4. Sau khi login, set `token` vào environment
5. Trong các request khác, dùng: `Authorization: Bearer {{token}}`

---

## 🎯 8. VÍ DỤ TEST THEO ROLE

### Test với ADMIN
1. Login với user có role ADMIN
2. Test tất cả endpoint (users, profile, tất cả Python API)

### Test với HR_MANAGER
1. Login với user có role HR_MANAGER
2. Test:
   - ✅ `/profile/**`
   - ✅ `/api/python/employees/**`
   - ✅ `/api/python/attendance/**`
   - ✅ `/api/python/departments/**`
   - ✅ `/api/python/positions/**`
   - ❌ `/users/**` (403 Forbidden)
   - ❌ `/api/python/salaries/**` (403 Forbidden)
   - ❌ `/api/python/dividends/**` (403 Forbidden)

### Test với PAYROLL_MANAGER
1. Login với user có role PAYROLL_MANAGER
2. Test:
   - ✅ `/api/python/salaries/**`
   - ✅ `/api/python/dividends/**`
   - ❌ `/users/**` (403 Forbidden)
   - ❌ `/profile/**` (403 Forbidden)
   - ❌ `/api/python/employees/**` (403 Forbidden)

---

## 📌 9. LƯU Ý QUAN TRỌNG

1. **Python API phải chạy:** Đảm bảo Python API server đang chạy tại `http://localhost:5000` trước khi test các endpoint `/api/python/**`

2. **Token hết hạn:** Token có thời hạn (mặc định 604800 giây = 7 ngày). Nếu token hết hạn, cần login lại.

3. **Role-based access:** Mỗi endpoint yêu cầu role cụ thể. Kiểm tra role của user trước khi test.

4. **Content-Type:** Tất cả POST/PUT request cần header `Content-Type: application/json`

5. **Bearer Token:** Luôn dùng format `Bearer {token}` trong header Authorization

---

## 🔗 10. TÓM TẮT ENDPOINTS

| Endpoint | Method | Role Required | Mô tả |
|----------|--------|---------------|-------|
| `/auth/signIn` | POST | Public | Đăng nhập |
| `/auth/logout` | POST | Authenticated | Đăng xuất |
| `/api/v1/health` | GET | Public | Health check |
| `/users/**` | ALL | ADMIN | Quản lý users |
| `/profile/**` | ALL | ADMIN, HR_MANAGER | Quản lý profile |
| `/api/python/employees/**` | ALL | ADMIN, HR_MANAGER | Quản lý nhân viên |
| `/api/python/attendance/**` | ALL | ADMIN, HR_MANAGER | Quản lý chấm công |
| `/api/python/departments/**` | ALL | ADMIN, HR_MANAGER | Quản lý phòng ban |
| `/api/python/positions/**` | ALL | ADMIN, HR_MANAGER | Quản lý chức vụ |
| `/api/python/salaries/**` | ALL | ADMIN, PAYROLL_MANAGER | Quản lý lương |
| `/api/python/dividends/**` | ALL | ADMIN, PAYROLL_MANAGER | Quản lý cổ tức |
| `/api/python/**` (khác) | ALL | ADMIN | Các endpoint khác |

---

**Chúc bạn test thành công! 🚀**

