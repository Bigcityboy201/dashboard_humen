let employees = [];

// Load dữ liệu khi trang được tải
document.addEventListener('DOMContentLoaded', async () => {
    await loadEmployees();
    await loadSalaries();
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
        const generateSelect = document.getElementById('generate-employee-id');
        
        // Clear options
        select.innerHTML = '<option value="">Tất cả</option>';
        generateSelect.innerHTML = '<option value="">Chọn nhân viên</option>';
        
        // Add options
        employees.forEach(emp => {
            const option = document.createElement('option');
            option.value = emp.EmployeeID;
            option.textContent = `${emp.FullName} (ID: ${emp.EmployeeID})`;
            select.appendChild(option.cloneNode(true));
            generateSelect.appendChild(option.cloneNode(true));
        });
    }
}

// Load danh sách lương
async function loadSalaries() {
    const loading = document.getElementById('loading');
    const tableBody = document.getElementById('salaries-table-body');
    
    loading.style.display = 'block';
    tableBody.innerHTML = '';

    const employeeId = document.getElementById('filter-employee').value;
    const year = document.getElementById('filter-year').value;

    const params = {};
    if (employeeId) params.employee_id = parseInt(employeeId);
    if (year) params.year = parseInt(year);

    const result = await SalariesAPI.getAll(params);
    
    console.log('Salaries API Response:', result); // Debug

    loading.style.display = 'none';

    if (result.success) {
        // Xử lý trường hợp response bị wrap thêm một lần
        let data = result.data;
        if (data && data.data && Array.isArray(data.data)) {
            data = data.data;
        } else if (data && !Array.isArray(data) && Array.isArray(data.data)) {
            data = data.data;
        }
        
        const salaries = Array.isArray(data) ? data : [];

        if (salaries.length === 0) {
            tableBody.innerHTML = `
                <tr>
                    <td colspan="8" class="empty-state">
                        <div class="empty-state-icon">📭</div>
                        <p>Không có dữ liệu lương</p>
                    </td>
                </tr>
            `;
        } else {
            tableBody.innerHTML = salaries.map(salary => `
                <tr>
                    <td>${salary.SalaryID}</td>
                    <td>${salary.EmployeeName || salary.Employee?.FullName || '-'}</td>
                    <td>${formatDate(salary.SalaryMonth || salary.SalaryDate) || '-'}</td>
                    <td>${formatCurrency(salary.BasicSalary)}</td>
                    <td>${formatCurrency(salary.Bonus)}</td>
                    <td>${formatCurrency(salary.Deduction)}</td>
                    <td><strong>${formatCurrency(salary.TotalSalary)}</strong></td>
                    <td>
                        <div class="action-buttons">
                            <button class="action-btn action-btn-view" onclick="viewSalary(${salary.SalaryID})" title="Xem chi tiết">
                                👁️
                            </button>
                            <button class="action-btn action-btn-edit" onclick="editSalary(${salary.SalaryID})" title="Sửa">
                                ✏️
                            </button>
                            <button class="action-btn action-btn-delete" onclick="deleteSalary(${salary.SalaryID})" title="Xóa">
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
        showAlert(result.error || 'Lỗi khi tải danh sách lương', 'error');
    }
}

// Reset filters
function resetFilters() {
    document.getElementById('filter-employee').value = '';
    document.getElementById('filter-year').value = '';
    loadSalaries();
}

// Open generate salary modal
function openGenerateSalaryModal() {
    const modal = document.getElementById('generateSalaryModal');
    document.getElementById('generateSalaryForm').reset();
    modal.classList.add('show');
}

// Close generate salary modal
function closeGenerateSalaryModal() {
    const modal = document.getElementById('generateSalaryModal');
    modal.classList.remove('show');
}

// Generate salary
async function generateSalary(event) {
    event.preventDefault();

    const employeeId = parseInt(document.getElementById('generate-employee-id').value);
    const month = document.getElementById('generate-month').value;

    const data = {
        EmployeeID: employeeId,
        SalaryMonth: month
    };

    const result = await SalariesAPI.generate(data);

    if (result.success) {
        showAlert('Tạo bảng lương thành công!', 'success');
        closeGenerateSalaryModal();
        loadSalaries();
    } else {
        showAlert(result.error || 'Có lỗi xảy ra', 'error');
    }
}

// View salary details
async function viewSalary(salaryId) {
    const modal = document.getElementById('salaryDetailModal');
    const content = document.getElementById('salary-detail-content');
    
    modal.classList.add('show');
    content.innerHTML = `
        <div class="loading">
            <div class="spinner"></div>
            <p>Đang tải thông tin...</p>
        </div>
    `;
    
    const result = await SalariesAPI.getById(salaryId);
    if (result.success) {
        const salary = result.data;
        
        content.innerHTML = `
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1.5rem;">
                <div>
                    <h3 style="margin-bottom: 1rem; color: var(--primary-color); border-bottom: 2px solid var(--border-color); padding-bottom: 0.5rem;">Thông tin nhân viên</h3>
                    <div style="margin-bottom: 1rem;">
                        <strong>ID nhân viên:</strong>
                        <div style="color: var(--text-secondary);">${salary.EmployeeID || '-'}</div>
                    </div>
                    <div style="margin-bottom: 1rem;">
                        <strong>Tên nhân viên:</strong>
                        <div style="color: var(--text-secondary); font-size: 1.1rem; font-weight: 500;">${salary.EmployeeName || salary.Employee?.FullName || '-'}</div>
                    </div>
                </div>
                
                <div>
                    <h3 style="margin-bottom: 1rem; color: var(--primary-color); border-bottom: 2px solid var(--border-color); padding-bottom: 0.5rem;">Thông tin lương</h3>
                    <div style="margin-bottom: 1rem;">
                        <strong>Tháng:</strong>
                        <div style="color: var(--text-secondary);">${formatDate(salary.SalaryMonth || salary.SalaryDate) || '-'}</div>
                    </div>
                </div>
            </div>
            
            <div style="margin-top: 2rem; padding-top: 1.5rem; border-top: 2px solid var(--border-color);">
                <h3 style="margin-bottom: 1rem; color: var(--primary-color);">Chi tiết lương</h3>
                <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 1rem; background: var(--bg-color); padding: 1rem; border-radius: 0.5rem;">
                    <div>
                        <strong>Lương cơ bản:</strong>
                        <div style="color: var(--text-secondary);">${formatCurrency(salary.BasicSalary)}</div>
                    </div>
                    <div>
                        <strong>Thưởng:</strong>
                        <div style="color: var(--success-color);">+ ${formatCurrency(salary.Bonus)}</div>
                    </div>
                    <div>
                        <strong>Khấu trừ:</strong>
                        <div style="color: var(--danger-color);">- ${formatCurrency(salary.Deduction)}</div>
                    </div>
                    <div>
                        <strong>Tổng lương:</strong>
                        <div style="color: var(--primary-color); font-size: 1.2rem; font-weight: bold;">${formatCurrency(salary.TotalSalary)}</div>
                    </div>
                </div>
            </div>
        `;
    } else {
        content.innerHTML = `
            <div class="alert alert-error">
                <span>${result.error || 'Không thể tải thông tin lương'}</span>
            </div>
        `;
    }
}

// Close salary detail modal
function closeSalaryDetailModal() {
    const modal = document.getElementById('salaryDetailModal');
    modal.classList.remove('show');
}

// Edit salary
async function editSalary(salaryId) {
    const result = await SalariesAPI.getById(salaryId);
    console.log('Get salary by ID result:', result); // Debug
    
    if (result.success) {
        const salary = result.data;
        // Xử lý trường hợp data bị wrap
        const salaryData = salary.data || salary;
        
        document.getElementById('salary-id').value = salaryData.SalaryID;
        document.getElementById('bonus').value = salaryData.Bonus || 0;
        // Map field names: Deduction -> Deductions
        document.getElementById('deduction').value = salaryData.Deduction || salaryData.Deductions || 0;
        
        const modal = document.getElementById('editSalaryModal');
        modal.classList.add('show');
    } else {
        showAlert(result.error || 'Không thể tải thông tin lương', 'error');
    }
}

// Close edit salary modal
function closeEditSalaryModal() {
    const modal = document.getElementById('editSalaryModal');
    modal.classList.remove('show');
}

// Save salary (update)
async function saveSalary(event) {
    event.preventDefault();

    const salaryId = document.getElementById('salary-id').value;

    // Map field names: Deduction -> Deductions (backend expects Deductions)
    const data = {
        Bonus: parseFloat(document.getElementById('bonus').value) || 0,
        Deductions: parseFloat(document.getElementById('deduction').value) || 0
    };

    console.log('Update salary data:', data); // Debug

    try {
        const result = await SalariesAPI.update(salaryId, data);
        
        console.log('Update salary result:', result); // Debug

        if (result.success) {
            showAlert('Cập nhật lương thành công!', 'success');
            closeEditSalaryModal();
            loadSalaries();
        } else {
            showAlert(result.error || 'Có lỗi xảy ra', 'error');
            console.error('Update salary error:', result); // Debug
        }
    } catch (error) {
        console.error('Update salary exception:', error); // Debug
        showAlert(error.message || 'Có lỗi xảy ra khi cập nhật lương', 'error');
    }
}

// Delete salary
async function deleteSalary(salaryId) {
    if (!confirm('Bạn có chắc chắn muốn xóa bản ghi lương này?')) {
        return;
    }

    const result = await SalariesAPI.delete(salaryId);
    if (result.success) {
        showAlert('Xóa bản ghi lương thành công!', 'success');
        loadSalaries();
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

    const result = await SalariesAPI.getStatistics(null, year);
    console.log('Statistics result:', result); // Debug
    
    if (result.success) {
        const stats = result.data;
        // Xử lý trường hợp data bị wrap
        const statsData = stats.data || stats;
        
        content.innerHTML = `
            <h3 style="margin-bottom: 1rem; color: var(--primary-color);">Thống kê lương năm ${year}</h3>
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem;">
                <div style="text-align: center; padding: 1rem; background: var(--bg-color); border-radius: 0.5rem;">
                    <div style="font-size: 2rem; font-weight: bold; color: var(--primary-color);">${statsData.total_records || 0}</div>
                    <div style="color: var(--text-secondary);">Tổng số bản ghi</div>
                </div>
                <div style="text-align: center; padding: 1rem; background: var(--bg-color); border-radius: 0.5rem;">
                    <div style="font-size: 2rem; font-weight: bold; color: var(--success-color);">${formatCurrency(statsData.total_amount || statsData.total_NetSalary || 0)}</div>
                    <div style="color: var(--text-secondary);">Tổng chi phí lương</div>
                </div>
                <div style="text-align: center; padding: 1rem; background: var(--bg-color); border-radius: 0.5rem;">
                    <div style="font-size: 1.5rem; font-weight: bold; color: var(--primary-color);">${formatCurrency(statsData.total_base_salary || statsData.total_BaseSalary || 0)}</div>
                    <div style="color: var(--text-secondary);">Tổng lương cơ bản</div>
                </div>
                <div style="text-align: center; padding: 1rem; background: var(--bg-color); border-radius: 0.5rem;">
                    <div style="font-size: 1.5rem; font-weight: bold; color: var(--warning-color);">${formatCurrency(statsData.total_bonus || 0)}</div>
                    <div style="color: var(--text-secondary);">Tổng thưởng</div>
                </div>
                <div style="text-align: center; padding: 1rem; background: var(--bg-color); border-radius: 0.5rem;">
                    <div style="font-size: 1.5rem; font-weight: bold; color: var(--danger-color);">${formatCurrency(statsData.total_deductions || statsData.total_Deductions || 0)}</div>
                    <div style="color: var(--text-secondary);">Tổng khấu trừ</div>
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
document.getElementById('generateSalaryModal')?.addEventListener('click', function(e) {
    if (e.target === this) closeGenerateSalaryModal();
});
document.getElementById('editSalaryModal')?.addEventListener('click', function(e) {
    if (e.target === this) closeEditSalaryModal();
});
document.getElementById('salaryDetailModal')?.addEventListener('click', function(e) {
    if (e.target === this) closeSalaryDetailModal();
});

