# Phân tích các API còn thiếu trong hệ thống

## Tổng quan
Hệ thống hiện có các module chính:
- **Employees** (Nhân viên)
- **Departments** (Phòng ban)
- **Positions** (Chức vụ)
- **Salaries** (Lương)
- **Attendance** (Chấm công)
- **Dividends** (Cổ tức)

---

## 1. EMPLOYEES API - Còn thiếu

### ✅ Đã có:
- `GET /employees` - List với filter, pagination
- `POST /employees` - Tạo mới
- `GET /employees/{id}` - Chi tiết
- `PUT /employees/{id}` - Cập nhật
- `DELETE /employees/{id}` - Xóa hard delete

### ❌ Còn thiếu:
1. **Soft Delete** - `PUT /employees/{id}/deactivate` hoặc `DELETE /employees/{id}` với soft delete
   - Comment trong code: `#thiếu xóa mềm` (dòng 196 employees.py)
   - Cần thêm field `IsDeleted` hoặc `DeletedAt` trong DB

2. **Bulk Operations**:
   - `POST /employees/bulk` - Tạo nhiều nhân viên cùng lúc
   - `PUT /employees/bulk` - Cập nhật nhiều nhân viên
   - `DELETE /employees/bulk` - Xóa nhiều nhân viên

3. **Search/Filter nâng cao**:
   - `GET /employees/search?q={keyword}` - Tìm kiếm theo tên, email, phone
   - `GET /employees?position_id={id}` - Filter theo chức vụ (hiện chỉ có department_id, status)

4. **Statistics/Reports**:
   - `GET /employees/statistics` - Thống kê: tổng số, theo phòng ban, theo chức vụ, theo status
   - `GET /employees/{id}/history` - Lịch sử thay đổi thông tin nhân viên

5. **Export/Import**:
   - `GET /employees/export?format=csv|excel` - Xuất danh sách nhân viên
   - `POST /employees/import` - Import nhân viên từ file

---

## 2. DEPARTMENTS API - Còn thiếu

### ✅ Đã có:
- `GET /departments` - List
- `GET /departments/{id}` - Chi tiết
- `POST /departments` - Tạo mới
- `PUT /departments/{id}` - Cập nhật
- `DELETE /departments/{id}` - Xóa

### ❌ Còn thiếu:
1. **Statistics**:
   - `GET /departments/{id}/employees` - Danh sách nhân viên trong phòng ban
   - `GET /departments/{id}/statistics` - Thống kê: số nhân viên, tổng lương, v.v.
   - `GET /departments/statistics` - Thống kê tổng hợp tất cả phòng ban

2. **Hierarchy** (nếu có cấu trúc cây):
   - `GET /departments/{id}/children` - Phòng ban con
   - `GET /departments/{id}/parent` - Phòng ban cha

---

## 3. POSITIONS API - Còn thiếu

### ✅ Đã có:
- `GET /positions` - List
- `GET /positions/{id}` - Chi tiết
- `POST /positions` - Tạo mới
- `PUT /positions/{id}` - Cập nhật
- `DELETE /positions/{id}` - Xóa

### ❌ Còn thiếu:
1. **Statistics**:
   - `GET /positions/{id}/employees` - Danh sách nhân viên có chức vụ này
   - `GET /positions/{id}/statistics` - Thống kê: số nhân viên, mức lương trung bình
   - `GET /positions/statistics` - Thống kê tổng hợp

---

## 4. SALARIES API - Còn thiếu

### ✅ Đã có:
- `GET /salaries` - List với filter
- `POST /salaries/generate` - Tạo/tính lương
- `GET /salaries/{id}` - Chi tiết
- `PUT /salaries/{id}` - Cập nhật
- `DELETE /salaries/{id}` - Xóa
- `GET /salaries/my` - Lịch sử lương của tôi
- `GET /salaries/statistics` - Thống kê theo tháng

### ❌ Còn thiếu:
1. **Bulk Generate**:
   - `POST /salaries/generate/bulk` - Tính lương cho nhiều nhân viên/tháng cùng lúc

2. **Reports nâng cao**:
   - `GET /salaries/report?year={year}` - Báo cáo lương theo năm
   - `GET /salaries/report/department?month={month}&department_id={id}` - Báo cáo lương theo phòng ban
   - `GET /salaries/report/position?month={month}&position_id={id}` - Báo cáo lương theo chức vụ

3. **Export**:
   - `GET /salaries/export?month={month}&format=csv|excel` - Xuất bảng lương

4. **Salary Slip**:
   - `GET /salaries/{id}/slip` - Phiếu lương chi tiết (PDF/HTML)

5. **Comparison**:
   - `GET /salaries/compare?employee_id={id}&month1={m1}&month2={m2}` - So sánh lương giữa các tháng

---

## 5. ATTENDANCE API - Còn thiếu

### ✅ Đã có:
- `GET /attendance` - List với filter
- `POST /attendance` - Tạo mới
- `GET /attendance/{id}` - Chi tiết
- `PUT /attendance/{id}` - Cập nhật
- `DELETE /attendance/{id}` - Xóa
- `GET /attendance/statistics` - Thống kê

### ❌ Còn thiếu:
1. **Bulk Operations**:
   - `POST /attendance/bulk` - Tạo nhiều bản ghi chấm công cùng lúc

2. **Reports nâng cao**:
   - `GET /attendance/report?year={year}` - Báo cáo chấm công theo năm
   - `GET /attendance/report/department?month={month}&department_id={id}` - Báo cáo theo phòng ban
   - `GET /attendance/report/employee?employee_id={id}&year={year}` - Báo cáo theo nhân viên

3. **Export**:
   - `GET /attendance/export?month={month}&format=csv|excel` - Xuất bảng chấm công

4. **Daily Attendance** (nếu cần chi tiết theo ngày):
   - `GET /attendance/daily?date={date}` - Chấm công theo ngày
   - `POST /attendance/daily` - Tạo chấm công theo ngày

---

## 6. DIVIDENDS API - Còn thiếu

### ✅ Đã có:
- `GET /dividends` - List
- `POST /dividends` - Tạo mới
- `GET /dividends/{id}` - Chi tiết
- `PUT /dividends/{id}` - Cập nhật
- `DELETE /dividends/{id}` - Xóa

### ❌ Còn thiếu:
1. **Filter/Search**:
   - `GET /dividends?employee_id={id}` - Filter theo nhân viên
   - `GET /dividends?year={year}` - Filter theo năm
   - `GET /dividends?date_from={date}&date_to={date}` - Filter theo khoảng thời gian

2. **Statistics**:
   - `GET /dividends/statistics?year={year}` - Thống kê cổ tức theo năm
   - `GET /dividends/statistics/employee?employee_id={id}` - Tổng cổ tức của nhân viên

3. **Reports**:
   - `GET /dividends/report?year={year}` - Báo cáo cổ tức theo năm
   - `GET /dividends/export?year={year}&format=csv|excel` - Xuất báo cáo

---

## 7. CÁC API TỔNG HỢP/DASHBOARD - Hoàn toàn thiếu

### ❌ Cần thêm:
1. **Dashboard/Overview**:
   - `GET /dashboard/overview` - Tổng quan hệ thống
   - `GET /dashboard/statistics` - Thống kê tổng hợp: tổng nhân viên, tổng lương tháng, v.v.

2. **Reports tổng hợp**:
   - `GET /reports/payroll?month={month}` - Báo cáo tổng hợp lương
   - `GET /reports/attendance?month={month}` - Báo cáo tổng hợp chấm công
   - `GET /reports/financial?year={year}` - Báo cáo tài chính (lương + cổ tức)

3. **Analytics**:
   - `GET /analytics/employee-growth?year={year}` - Phân tích tăng trưởng nhân viên
   - `GET /analytics/salary-trend?year={year}` - Xu hướng lương
   - `GET /analytics/attendance-trend?year={year}` - Xu hướng chấm công

---

## 8. CÁC API TIỆN ÍCH - Hoàn toàn thiếu

### ❌ Cần thêm:
1. **File Upload/Download**:
   - `POST /upload` - Upload file (ảnh nhân viên, tài liệu)
   - `GET /files/{file_id}` - Download file

2. **Notifications** (nếu cần):
   - `GET /notifications` - Danh sách thông báo
   - `POST /notifications/{id}/read` - Đánh dấu đã đọc

3. **Audit Log** (nếu cần tracking):
   - `GET /audit-logs?entity={entity}&entity_id={id}` - Lịch sử thay đổi

---

## 9. CÁC API XÁC THỰC/PHÂN QUYỀN - Hoàn toàn thiếu (chưa tính security)

### ❌ Cần thêm (khi implement security):
1. **Authentication**:
   - `POST /auth/login` - Đăng nhập
   - `POST /auth/logout` - Đăng xuất
   - `POST /auth/refresh` - Refresh token

2. **User Management** (nếu có bảng users):
   - `GET /users` - Danh sách user
   - `POST /users` - Tạo user
   - `PUT /users/{id}` - Cập nhật user
   - `DELETE /users/{id}` - Xóa user

3. **Roles & Permissions** (nếu có):
   - `GET /roles` - Danh sách vai trò
   - `GET /permissions` - Danh sách quyền

---

## Tóm tắt ưu tiên

### 🔴 Ưu tiên cao (cần thiết cho hệ thống cơ bản):
1. Soft delete cho Employees
2. Statistics cho các module chính
3. Filter/Search nâng cao cho Dividends
4. Dashboard/Overview API

### 🟡 Ưu tiên trung bình (cải thiện UX):
1. Bulk operations
2. Export/Import
3. Reports nâng cao
4. Salary slip

### 🟢 Ưu tiên thấp (nice to have):
1. Analytics
2. File upload/download
3. Notifications
4. Audit logs

---

## Lưu ý
- Tất cả các API trên chưa tính tới security (authentication, authorization)
- Cần kiểm tra database schema để xác nhận các bảng/field có sẵn
- Một số API có thể cần thêm bảng mới trong database

