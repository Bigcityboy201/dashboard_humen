let currentPage = 1;
const pageSize = 10;
let departments = [];
let positions = [];

// Load dữ liệu khi trang được tải
document.addEventListener('DOMContentLoaded', async () => {
    await loadDepartments();
    await loadPositions();
    await loadEmployees();
});

// Load danh sách phòng ban
async function loadDepartments() {
    const result = await DepartmentsAPI.getAll();
    if (result.success) {
        departments = result.data;
        const select = document.getElementById('department-id');
        const filterSelect = document.getElementById('filter-department');
        
        // Clear options
        select.innerHTML = '<option value="">Chọn phòng ban</option>';
        filterSelect.innerHTML = '<option value="">Tất cả</option>';
        
        // Add options
        departments.forEach(dept => {
            const option = document.createElement('option');
            option.value = dept.DepartmentID;
            option.textContent = dept.DepartmentName;
            select.appendChild(option.cloneNode(true));
            filterSelect.appendChild(option);
        });
    }
}

// Load danh sách chức vụ
async function loadPositions() {
    const result = await PositionsAPI.getAll();
    if (result.success) {
        positions = result.data;
        const select = document.getElementById('position-id');
        
        // Clear options
        select.innerHTML = '<option value="">Chọn chức vụ</option>';
        
        // Add options
        positions.forEach(pos => {
            const option = document.createElement('option');
            option.value = pos.PositionID;
            option.textContent = pos.PositionName;
            select.appendChild(option);
        });
    }
}

// Load danh sách nhân viên
async function loadEmployees(page = 1) {
    currentPage = page;
    const loading = document.getElementById('loading');
    const tableBody = document.getElementById('employees-table-body');
    
    loading.style.display = 'block';
    tableBody.innerHTML = '';

    const departmentId = document.getElementById('filter-department').value;
    const status = document.getElementById('filter-status').value;

    const params = {
        page: currentPage,
        size: pageSize
    };
    if (departmentId) params.department_id = parseInt(departmentId);
    if (status) params.status = status;

    const result = await EmployeesAPI.getAll(params);

    loading.style.display = 'none';

    if (result.success) {
        const employees = result.data.employees || [];
        const totalRecords = result.data.total_records || 0;
        const totalPages = Math.ceil(totalRecords / pageSize);

        if (employees.length === 0) {
            tableBody.innerHTML = `
                <tr>
                    <td colspan="10" class="empty-state">
                        <div class="empty-state-icon">📭</div>
                        <p>Không có dữ liệu nhân viên</p>
                    </td>
                </tr>
            `;
        } else {
            tableBody.innerHTML = employees.map(emp => `
                <tr>
                    <td>${emp.EmployeeID}</td>
                    <td>${emp.FullName || '-'}</td>
                    <td>${emp.Email || '-'}</td>
                    <td>${emp.PhoneNumber || '-'}</td>
                    <td>${emp.DepartmentName || '-'}</td>
                    <td>${emp.PositionName || '-'}</td>
                    <td>
                        <span class="status-badge ${getStatusClass(emp.Status)}">
                            ${emp.Status || '-'}
                        </span>
                    </td>
                    <td>${formatDate(emp.HireDate)}</td>
                    <td>${emp.Salary ? formatCurrency(emp.Salary.TotalSalary) : '-'}</td>
                    <td>
                        <div class="action-buttons">
                            <button class="action-btn action-btn-view" onclick="viewEmployee(${emp.EmployeeID})" title="Xem chi tiết">
                                👁️
                            </button>
                            <button class="action-btn action-btn-edit" onclick="editEmployee(${emp.EmployeeID})" title="Sửa">
                                ✏️
                            </button>
                            <button class="action-btn action-btn-delete" onclick="deleteEmployee(${emp.EmployeeID})" title="Xóa">
                                🗑️
                            </button>
                        </div>
                    </td>
                </tr>
            `).join('');
        }

        // Render pagination
        renderPagination(totalPages, currentPage);
    } else {
        tableBody.innerHTML = `
            <tr>
                <td colspan="10" class="empty-state">
                    <div class="empty-state-icon">⚠️</div>
                    <p>${result.error || 'Lỗi khi tải dữ liệu'}</p>
                </td>
            </tr>
        `;
        showAlert(result.error || 'Lỗi khi tải danh sách nhân viên', 'error');
    }
}

// Render pagination
function renderPagination(totalPages, currentPage) {
    const pagination = document.getElementById('pagination');
    if (totalPages <= 1) {
        pagination.innerHTML = '';
        return;
    }

    let html = `
        <button ${currentPage === 1 ? 'disabled' : ''} onclick="loadEmployees(${currentPage - 1})">‹ Trước</button>
        <span class="page-info">Trang ${currentPage} / ${totalPages}</span>
        <button ${currentPage === totalPages ? 'disabled' : ''} onclick="loadEmployees(${currentPage + 1})">Sau ›</button>
    `;
    pagination.innerHTML = html;
}

// Reset filters
function resetFilters() {
    document.getElementById('filter-department').value = '';
    document.getElementById('filter-status').value = '';
    loadEmployees(1);
}

// Get status color (for backward compatibility)
function getStatusColor(status) {
    switch(status) {
        case 'Đang làm việc': return '#10b981';
        case 'Nghỉ việc': return '#ef4444';
        case 'Thực tập': return '#f59e0b';
        default: return '#64748b';
    }
}

// Get status CSS class
function getStatusClass(status) {
    switch(status) {
        case 'Đang làm việc': return 'status-active';
        case 'Nghỉ việc': return 'status-inactive';
        case 'Nghỉ phép': return 'status-inactive';
        case 'Thực tập': return 'status-intern';
        case 'Thử việc': return 'status-intern';
        default: return 'status-active';
    }
}

// Open employee modal
function openEmployeeModal(employeeId = null) {
    const modal = document.getElementById('employeeModal');
    const form = document.getElementById('employeeForm');
    const modalTitle = document.getElementById('modal-title');
    const salaryGroup = document.getElementById('salary-group');

    form.reset();
    document.getElementById('employee-id').value = '';

    if (employeeId) {
        modalTitle.textContent = 'Sửa thông tin nhân viên';
        salaryGroup.style.display = 'none';
        loadEmployeeData(employeeId);
    } else {
        modalTitle.textContent = 'Thêm nhân viên mới';
        salaryGroup.style.display = 'block';
    }

    modal.classList.add('show');
}

// Close employee modal
function closeEmployeeModal() {
    const modal = document.getElementById('employeeModal');
    modal.classList.remove('show');
    document.getElementById('employeeForm').reset();
}

// Load employee data for editing
async function loadEmployeeData(employeeId) {
    const result = await EmployeesAPI.getById(employeeId);
    if (result.success) {
        const emp = result.data;
        document.getElementById('employee-id').value = emp.EmployeeID;
        document.getElementById('full-name').value = emp.FullName || '';
        document.getElementById('email').value = emp.Email || '';
        document.getElementById('phone-number').value = emp.PhoneNumber || '';
        document.getElementById('date-of-birth').value = emp.DateOfBirth || '';
        document.getElementById('gender').value = emp.Gender || '';
        document.getElementById('department-id').value = emp.Department?.DepartmentID || '';
        document.getElementById('position-id').value = emp.Position?.PositionID || '';
        document.getElementById('status').value = emp.Status || 'Thực tập';
    } else {
        showAlert(result.error || 'Không thể tải thông tin nhân viên', 'error');
    }
}

// View employee details
async function viewEmployee(employeeId) {
    const modal = document.getElementById('employeeDetailModal');
    const content = document.getElementById('employee-detail-content');
    
    // Show modal with loading
    modal.classList.add('show');
    content.innerHTML = `
        <div class="loading">
            <div class="spinner"></div>
            <p>Đang tải thông tin...</p>
        </div>
    `;
    
    const result = await EmployeesAPI.getById(employeeId);
    if (result.success) {
        const emp = result.data;
        const statusClass = getStatusClass(emp.Status);
        
        content.innerHTML = `
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1.5rem;">
                <div>
                    <h3 style="margin-bottom: 1rem; color: var(--primary-color); border-bottom: 2px solid var(--border-color); padding-bottom: 0.5rem;">Thông tin cá nhân</h3>
                    <div style="margin-bottom: 1rem;">
                        <strong>ID nhân viên:</strong>
                        <div style="color: var(--text-secondary);">${emp.EmployeeID}</div>
                    </div>
                    <div style="margin-bottom: 1rem;">
                        <strong>Họ và tên:</strong>
                        <div style="color: var(--text-secondary); font-size: 1.1rem; font-weight: 500;">${emp.FullName || '-'}</div>
                    </div>
                    <div style="margin-bottom: 1rem;">
                        <strong>Email:</strong>
                        <div style="color: var(--text-secondary);">${emp.Email || '-'}</div>
                    </div>
                    <div style="margin-bottom: 1rem;">
                        <strong>Số điện thoại:</strong>
                        <div style="color: var(--text-secondary);">${emp.PhoneNumber || '-'}</div>
                    </div>
                    <div style="margin-bottom: 1rem;">
                        <strong>Ngày sinh:</strong>
                        <div style="color: var(--text-secondary);">${formatDate(emp.DateOfBirth) || '-'}</div>
                    </div>
                    <div style="margin-bottom: 1rem;">
                        <strong>Giới tính:</strong>
                        <div style="color: var(--text-secondary);">${emp.Gender || '-'}</div>
                    </div>
                </div>
                
                <div>
                    <h3 style="margin-bottom: 1rem; color: var(--primary-color); border-bottom: 2px solid var(--border-color); padding-bottom: 0.5rem;">Thông tin công việc</h3>
                    <div style="margin-bottom: 1rem;">
                        <strong>Phòng ban:</strong>
                        <div style="color: var(--text-secondary);">${emp.Department?.DepartmentName || '-'}</div>
                    </div>
                    <div style="margin-bottom: 1rem;">
                        <strong>Chức vụ:</strong>
                        <div style="color: var(--text-secondary);">${emp.Position?.PositionName || '-'}</div>
                    </div>
                    <div style="margin-bottom: 1rem;">
                        <strong>Trạng thái:</strong>
                        <div>
                            <span class="status-badge ${statusClass}">
                                ${emp.Status || '-'}
                            </span>
                        </div>
                    </div>
                    <div style="margin-bottom: 1rem;">
                        <strong>Ngày vào làm:</strong>
                        <div style="color: var(--text-secondary);">${formatDate(emp.HireDate) || '-'}</div>
                    </div>
                </div>
            </div>
            
            ${emp.Salary ? `
            <div style="margin-top: 2rem; padding-top: 1.5rem; border-top: 2px solid var(--border-color);">
                <h3 style="margin-bottom: 1rem; color: var(--primary-color);">Thông tin lương</h3>
                <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 1rem; background: var(--bg-color); padding: 1rem; border-radius: 0.5rem;">
                    <div>
                        <strong>Lương cơ bản:</strong>
                        <div style="color: var(--text-secondary);">${formatCurrency(emp.Salary.BasicSalary)}</div>
                    </div>
                    <div>
                        <strong>Thưởng:</strong>
                        <div style="color: var(--success-color);">+ ${formatCurrency(emp.Salary.Bonus)}</div>
                    </div>
                    <div>
                        <strong>Khấu trừ:</strong>
                        <div style="color: var(--danger-color);">- ${formatCurrency(emp.Salary.Deduction)}</div>
                    </div>
                    <div>
                        <strong>Tổng lương:</strong>
                        <div style="color: var(--primary-color); font-size: 1.2rem; font-weight: bold;">${formatCurrency(emp.Salary.TotalSalary)}</div>
                    </div>
                    <div style="grid-column: 1 / -1;">
                        <strong>Tháng lương:</strong>
                        <div style="color: var(--text-secondary);">${formatDate(emp.Salary.SalaryDate) || '-'}</div>
                    </div>
                </div>
            </div>
            ` : `
            <div style="margin-top: 2rem; padding: 1rem; background: var(--bg-color); border-radius: 0.5rem; text-align: center; color: var(--text-secondary);">
                Chưa có thông tin lương
            </div>
            `}
        `;
    } else {
        content.innerHTML = `
            <div class="alert alert-error">
                <span>${result.error || 'Không thể tải thông tin nhân viên'}</span>
            </div>
        `;
    }
}

// Close employee detail modal
function closeEmployeeDetailModal() {
    const modal = document.getElementById('employeeDetailModal');
    modal.classList.remove('show');
}

// Close modal when clicking outside (sau khi DOM load)
document.addEventListener('DOMContentLoaded', function() {
    const detailModal = document.getElementById('employeeDetailModal');
    if (detailModal) {
        detailModal.addEventListener('click', function(e) {
            if (e.target === this) {
                closeEmployeeDetailModal();
            }
        });
    }
});

// Edit employee
function editEmployee(employeeId) {
    openEmployeeModal(employeeId);
}

// Save employee (create or update)
async function saveEmployee(event) {
    event.preventDefault();

    const employeeId = document.getElementById('employee-id').value;
    const isEdit = !!employeeId;

    const data = {
        FullName: document.getElementById('full-name').value,
        Email: document.getElementById('email').value,
        PhoneNumber: document.getElementById('phone-number').value || null,
        DateOfBirth: document.getElementById('date-of-birth').value || null,
        Gender: document.getElementById('gender').value || null,
        DepartmentID: parseInt(document.getElementById('department-id').value),
        PositionID: parseInt(document.getElementById('position-id').value),
        Status: document.getElementById('status').value
    };

    // Chỉ thêm Salary khi tạo mới
    if (!isEdit) {
        const salary = document.getElementById('salary').value;
        if (salary) {
            data.Salary = parseFloat(salary);
        }
    }

    let result;
    if (isEdit) {
        result = await EmployeesAPI.update(employeeId, data);
    } else {
        result = await EmployeesAPI.create(data);
    }

    if (result.success) {
        showAlert(isEdit ? 'Cập nhật nhân viên thành công!' : 'Thêm nhân viên thành công!', 'success');
        closeEmployeeModal();
        loadEmployees(currentPage);
    } else {
        showAlert(result.error || 'Có lỗi xảy ra', 'error');
    }
}

// Delete employee
async function deleteEmployee(employeeId) {
    if (!confirm('Bạn có chắc chắn muốn xóa nhân viên này?')) {
        return;
    }

    const result = await EmployeesAPI.delete(employeeId);
    if (result.success) {
        showAlert('Xóa nhân viên thành công!', 'success');
        loadEmployees(currentPage);
    } else {
        showAlert(result.error || 'Có lỗi xảy ra khi xóa', 'error');
    }
}

// Close modal when clicking outside
document.getElementById('employeeModal').addEventListener('click', function(e) {
    if (e.target === this) {
        closeEmployeeModal();
    }
});


