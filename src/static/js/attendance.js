let employees = [];

// Load dữ liệu khi trang được tải
document.addEventListener('DOMContentLoaded', async () => {
    await loadEmployees();
    await loadAttendances();
});

// Load danh sách nhân viên
async function loadEmployees() {
    const result = await EmployeesAPI.getAll({ size: 1000 });
    if (result.success) {
        // Xử lý response
        let data = result.data;
        if (data && data.data) {
            data = data.data;
        }
        employees = data?.employees || data || [];
        const select = document.getElementById('filter-employee');
        const formSelect = document.getElementById('employee-id');
        
        // Clear options
        select.innerHTML = '<option value="">Tất cả</option>';
        formSelect.innerHTML = '<option value="">Chọn nhân viên</option>';
        
        // Add options
        employees.forEach(emp => {
            const option = document.createElement('option');
            option.value = emp.EmployeeID;
            option.textContent = `${emp.FullName} (ID: ${emp.EmployeeID})`;
            select.appendChild(option.cloneNode(true));
            formSelect.appendChild(option.cloneNode(true));
        });
    }
}

// Load danh sách chấm công
async function loadAttendances() {
    const loading = document.getElementById('loading');
    const tableBody = document.getElementById('attendances-table-body');
    
    loading.style.display = 'block';
    tableBody.innerHTML = '';

    const employeeId = document.getElementById('filter-employee').value;
    const year = document.getElementById('filter-year').value;

    const params = {};
    if (employeeId) params.employee_id = parseInt(employeeId);
    if (year) params.year = parseInt(year);

    const result = await AttendanceAPI.getAll(params);
    
    console.log('Attendance API Response:', result); // Debug

    loading.style.display = 'none';

    if (result.success) {
        // Xử lý trường hợp response bị wrap thêm một lần
        let data = result.data;
        if (data && data.data && Array.isArray(data.data)) {
            data = data.data;
        } else if (data && !Array.isArray(data) && Array.isArray(data.data)) {
            data = data.data;
        }
        
        const attendances = Array.isArray(data) ? data : [];

        if (attendances.length === 0) {
            tableBody.innerHTML = `
                <tr>
                    <td colspan="8" class="empty-state">
                        <div class="empty-state-icon">📭</div>
                        <p>Không có dữ liệu chấm công</p>
                    </td>
                </tr>
            `;
        } else {
            tableBody.innerHTML = attendances.map(att => `
                <tr>
                    <td>${att.AttendanceID || att.TimesheetID}</td>
                    <td>${att.EmployeeName || att.Employee?.FullName || '-'}</td>
                    <td>${formatDate(att.AttendanceMonth || att.Month) || '-'}</td>
                    <td>${att.WorkDays || att.WorkingDays || 0}</td>
                    <td>${att.LeaveDays || 0}</td>
                    <td>${att.AbsentDays || 0}</td>
                    <td>${att.Notes || '-'}</td>
                    <td>
                        <div class="action-buttons">
                            <button class="action-btn action-btn-view" onclick="viewAttendance(${att.AttendanceID || att.TimesheetID})" title="Xem chi tiết">
                                👁️
                            </button>
                            <button class="action-btn action-btn-edit" onclick="editAttendance(${att.AttendanceID || att.TimesheetID})" title="Sửa">
                                ✏️
                            </button>
                            <button class="action-btn action-btn-delete" onclick="deleteAttendance(${att.AttendanceID || att.TimesheetID})" title="Xóa">
                                🗑️
                            </button>
                        </div>
                    </td>
                </tr>
            `).join('');
        }
    } else {
        tableBody.innerHTML = `
            <tr>
                <td colspan="8" class="empty-state">
                    <div class="empty-state-icon">⚠️</div>
                    <p>${result.error || 'Lỗi khi tải dữ liệu'}</p>
                </td>
            </tr>
        `;
        showAlert(result.error || 'Lỗi khi tải danh sách chấm công', 'error');
    }
}

// Reset filters
function resetFilters() {
    document.getElementById('filter-employee').value = '';
    document.getElementById('filter-year').value = '';
    loadAttendances();
}

// Open attendance modal
function openAttendanceModal(attendanceId = null) {
    const modal = document.getElementById('attendanceModal');
    const form = document.getElementById('attendanceForm');
    const modalTitle = document.getElementById('modal-title');

    form.reset();
    document.getElementById('attendance-id').value = '';

    if (attendanceId) {
        modalTitle.textContent = 'Sửa thông tin chấm công';
        loadAttendanceData(attendanceId);
    } else {
        modalTitle.textContent = 'Thêm chấm công';
    }

    modal.classList.add('show');
}

// Close attendance modal
function closeAttendanceModal() {
    const modal = document.getElementById('attendanceModal');
    modal.classList.remove('show');
    document.getElementById('attendanceForm').reset();
}

// Load attendance data for editing
async function loadAttendanceData(attendanceId) {
    const result = await AttendanceAPI.getById(attendanceId);
    if (result.success) {
        const att = result.data;
        document.getElementById('attendance-id').value = att.AttendanceID || att.TimesheetID;
        document.getElementById('employee-id').value = att.EmployeeID || '';
        document.getElementById('attendance-month').value = att.AttendanceMonth || att.Month || '';
        document.getElementById('work-days').value = att.WorkDays || att.WorkingDays || 0;
        document.getElementById('leave-days').value = att.LeaveDays || 0;
        document.getElementById('absent-days').value = att.AbsentDays || 0;
        document.getElementById('notes').value = att.Notes || '';
    } else {
        showAlert(result.error || 'Không thể tải thông tin chấm công', 'error');
    }
}

// View attendance details
async function viewAttendance(attendanceId) {
    const modal = document.getElementById('attendanceDetailModal');
    const content = document.getElementById('attendance-detail-content');
    
    modal.classList.add('show');
    content.innerHTML = `
        <div class="loading">
            <div class="spinner"></div>
            <p>Đang tải thông tin...</p>
        </div>
    `;
    
    const result = await AttendanceAPI.getById(attendanceId);
    if (result.success) {
        const att = result.data;
        
        content.innerHTML = `
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1.5rem;">
                <div>
                    <h3 style="margin-bottom: 1rem; color: var(--primary-color); border-bottom: 2px solid var(--border-color); padding-bottom: 0.5rem;">Thông tin nhân viên</h3>
                    <div style="margin-bottom: 1rem;">
                        <strong>ID nhân viên:</strong>
                        <div style="color: var(--text-secondary);">${att.EmployeeID || '-'}</div>
                    </div>
                    <div style="margin-bottom: 1rem;">
                        <strong>Tên nhân viên:</strong>
                        <div style="color: var(--text-secondary); font-size: 1.1rem; font-weight: 500;">${att.EmployeeName || att.Employee?.FullName || '-'}</div>
                    </div>
                </div>
                
                <div>
                    <h3 style="margin-bottom: 1rem; color: var(--primary-color); border-bottom: 2px solid var(--border-color); padding-bottom: 0.5rem;">Thông tin chấm công</h3>
                    <div style="margin-bottom: 1rem;">
                        <strong>Tháng:</strong>
                        <div style="color: var(--text-secondary);">${formatDate(att.AttendanceMonth || att.Month) || '-'}</div>
                    </div>
                </div>
            </div>
            
            <div style="margin-top: 2rem; padding-top: 1.5rem; border-top: 2px solid var(--border-color);">
                <h3 style="margin-bottom: 1rem; color: var(--primary-color);">Chi tiết chấm công</h3>
                <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 1rem; background: var(--bg-color); padding: 1rem; border-radius: 0.5rem;">
                    <div>
                        <strong>Số ngày công:</strong>
                        <div style="color: var(--success-color); font-size: 1.2rem; font-weight: bold;">${att.WorkDays || att.WorkingDays || 0}</div>
                    </div>
                    <div>
                        <strong>Số ngày nghỉ phép:</strong>
                        <div style="color: var(--warning-color); font-size: 1.2rem; font-weight: bold;">${att.LeaveDays || 0}</div>
                    </div>
                    <div>
                        <strong>Số ngày vắng mặt:</strong>
                        <div style="color: var(--danger-color); font-size: 1.2rem; font-weight: bold;">${att.AbsentDays || 0}</div>
                    </div>
                </div>
                ${att.Notes ? `
                <div style="margin-top: 1rem; padding: 1rem; background: var(--bg-color); border-radius: 0.5rem;">
                    <strong>Ghi chú:</strong>
                    <div style="color: var(--text-secondary); margin-top: 0.5rem;">${att.Notes}</div>
                </div>
                ` : ''}
            </div>
        `;
    } else {
        content.innerHTML = `
            <div class="alert alert-error">
                <span>${result.error || 'Không thể tải thông tin chấm công'}</span>
            </div>
        `;
    }
}

// Close attendance detail modal
function closeAttendanceDetailModal() {
    const modal = document.getElementById('attendanceDetailModal');
    modal.classList.remove('show');
}

// Edit attendance
function editAttendance(attendanceId) {
    openAttendanceModal(attendanceId);
}

// Save attendance (create or update)
async function saveAttendance(event) {
    event.preventDefault();

    const attendanceId = document.getElementById('attendance-id').value;
    const isEdit = !!attendanceId;

    const data = {
        EmployeeID: parseInt(document.getElementById('employee-id').value),
        AttendanceMonth: document.getElementById('attendance-month').value,
        WorkDays: parseInt(document.getElementById('work-days').value) || 0,
        LeaveDays: parseInt(document.getElementById('leave-days').value) || 0,
        AbsentDays: parseInt(document.getElementById('absent-days').value) || 0,
        Notes: document.getElementById('notes').value || null
    };

    // Map to API expected format
    if (!isEdit) {
        data.Month = data.AttendanceMonth;
        data.WorkingDays = data.WorkDays;
    }

    let result;
    if (isEdit) {
        result = await AttendanceAPI.update(attendanceId, data);
    } else {
        result = await AttendanceAPI.create(data);
    }

    if (result.success) {
        showAlert(isEdit ? 'Cập nhật chấm công thành công!' : 'Thêm chấm công thành công!', 'success');
        closeAttendanceModal();
        loadAttendances();
    } else {
        showAlert(result.error || 'Có lỗi xảy ra', 'error');
    }
}

// Delete attendance
async function deleteAttendance(attendanceId) {
    if (!confirm('Bạn có chắc chắn muốn xóa bản ghi chấm công này?')) {
        return;
    }

    const result = await AttendanceAPI.delete(attendanceId);
    if (result.success) {
        showAlert('Xóa bản ghi chấm công thành công!', 'success');
        loadAttendances();
    } else {
        showAlert(result.error || 'Có lỗi xảy ra khi xóa', 'error');
    }
}

// Load statistics
async function loadStatistics() {
    const year = document.getElementById('stats-year').value;
    if (!year) {
        showAlert('Vui lòng chọn năm', 'error');
        return;
    }

    const content = document.getElementById('statistics-content');
    content.innerHTML = `
        <div class="loading">
            <div class="spinner"></div>
            <p>Đang tải thống kê...</p>
        </div>
    `;

    const result = await AttendanceAPI.getStatistics(null, year);
    console.log('Attendance statistics result:', result); // Debug
    
    if (result.success) {
        const stats = result.data;
        // Xử lý trường hợp data bị wrap
        const statsData = stats.data || stats;
        
        content.innerHTML = `
            <h3 style="margin-bottom: 1rem; color: var(--primary-color);">Thống kê chấm công năm ${year}</h3>
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem;">
                <div style="text-align: center; padding: 1rem; background: var(--bg-color); border-radius: 0.5rem;">
                    <div style="font-size: 2rem; font-weight: bold; color: var(--primary-color);">${statsData.total_records || 0}</div>
                    <div style="color: var(--text-secondary);">Tổng số bản ghi</div>
                </div>
                <div style="text-align: center; padding: 1rem; background: var(--bg-color); border-radius: 0.5rem;">
                    <div style="font-size: 2rem; font-weight: bold; color: var(--primary-color);">${statsData.total_work_days || 0}</div>
                    <div style="color: var(--text-secondary);">Tổng ngày công</div>
                </div>
                <div style="text-align: center; padding: 1rem; background: var(--bg-color); border-radius: 0.5rem;">
                    <div style="font-size: 2rem; font-weight: bold; color: var(--warning-color);">${statsData.total_leave_days || 0}</div>
                    <div style="color: var(--text-secondary);">Tổng ngày nghỉ phép</div>
                </div>
                <div style="text-align: center; padding: 1rem; background: var(--bg-color); border-radius: 0.5rem;">
                    <div style="font-size: 2rem; font-weight: bold; color: var(--danger-color);">${statsData.total_absent_days || 0}</div>
                    <div style="color: var(--text-secondary);">Tổng ngày vắng mặt</div>
                </div>
            </div>
        `;
    } else {
        content.innerHTML = `
            <div class="alert alert-error">
                <span>${result.error || 'Lỗi khi tải thống kê'}</span>
            </div>
        `;
    }
}

// Close modals when clicking outside
document.getElementById('attendanceModal')?.addEventListener('click', function(e) {
    if (e.target === this) closeAttendanceModal();
});
document.getElementById('attendanceDetailModal')?.addEventListener('click', function(e) {
    if (e.target === this) closeAttendanceDetailModal();
});

