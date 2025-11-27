// Load dữ liệu khi trang được tải
document.addEventListener('DOMContentLoaded', () => {
    loadDepartments();
});

// Load danh sách phòng ban
async function loadDepartments() {
    const loading = document.getElementById('loading');
    const tableBody = document.getElementById('departments-table-body');
    
    loading.style.display = 'block';
    tableBody.innerHTML = '';

    const result = await DepartmentsAPI.getAll();

    loading.style.display = 'none';

    if (result.success) {
        const departments = result.data || [];

        if (departments.length === 0) {
            tableBody.innerHTML = `
                <tr>
                    <td colspan="3" class="empty-state">
                        <div class="empty-state-icon">📭</div>
                        <p>Không có dữ liệu phòng ban</p>
                    </td>
                </tr>
            `;
        } else {
            tableBody.innerHTML = departments.map(dept => `
                <tr>
                    <td>${dept.DepartmentID}</td>
                    <td>${dept.DepartmentName || '-'}</td>
                    <td>
                        <div class="action-buttons">
                            <button class="action-btn action-btn-view" onclick="viewDepartmentEmployees(${dept.DepartmentID})" title="Xem nhân viên">
                                👥
                            </button>
                            <button class="action-btn action-btn-edit" onclick="editDepartment(${dept.DepartmentID})" title="Sửa">
                                ✏️
                            </button>
                            <button class="action-btn action-btn-delete" onclick="deleteDepartment(${dept.DepartmentID})" title="Xóa">
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
                <td colspan="3" class="empty-state">
                    <div class="empty-state-icon">⚠️</div>
                    <p>${result.error || 'Lỗi khi tải dữ liệu'}</p>
                </td>
            </tr>
        `;
        showAlert(result.error || 'Lỗi khi tải danh sách phòng ban', 'error');
    }
}

// Open department modal
function openDepartmentModal(departmentId = null) {
    const modal = document.getElementById('departmentModal');
    const form = document.getElementById('departmentForm');
    const modalTitle = document.getElementById('modal-title');

    form.reset();
    document.getElementById('department-id').value = '';

    if (departmentId) {
        modalTitle.textContent = 'Sửa thông tin phòng ban';
        loadDepartmentData(departmentId);
    } else {
        modalTitle.textContent = 'Thêm phòng ban mới';
    }

    modal.classList.add('show');
}

// Close department modal
function closeDepartmentModal() {
    const modal = document.getElementById('departmentModal');
    modal.classList.remove('show');
    document.getElementById('departmentForm').reset();
}

// Load department data for editing
async function loadDepartmentData(departmentId) {
    const result = await DepartmentsAPI.getById(departmentId);
    if (result.success) {
        const dept = result.data;
        document.getElementById('department-id').value = dept.DepartmentID;
        document.getElementById('department-name').value = dept.DepartmentName || '';
    } else {
        showAlert(result.error || 'Không thể tải thông tin phòng ban', 'error');
    }
}

// Edit department
function editDepartment(departmentId) {
    openDepartmentModal(departmentId);
}

// Save department (create or update)
async function saveDepartment(event) {
    event.preventDefault();

    const departmentId = document.getElementById('department-id').value;
    const isEdit = !!departmentId;

    const data = {
        DepartmentName: document.getElementById('department-name').value
    };

    let result;
    if (isEdit) {
        result = await DepartmentsAPI.update(departmentId, data);
    } else {
        result = await DepartmentsAPI.create(data);
    }

    if (result.success) {
        showAlert(isEdit ? 'Cập nhật phòng ban thành công!' : 'Thêm phòng ban thành công!', 'success');
        closeDepartmentModal();
        loadDepartments();
    } else {
        showAlert(result.error || 'Có lỗi xảy ra', 'error');
    }
}

// Delete department
async function deleteDepartment(departmentId) {
    if (!confirm('Bạn có chắc chắn muốn xóa phòng ban này? Lưu ý: Tất cả nhân viên trong phòng ban này sẽ bị ảnh hưởng.')) {
        return;
    }

    const result = await DepartmentsAPI.delete(departmentId);
    if (result.success) {
        showAlert('Xóa phòng ban thành công!', 'success');
        loadDepartments();
    } else {
        showAlert(result.error || 'Có lỗi xảy ra khi xóa', 'error');
    }
}

// Close modal when clicking outside
document.getElementById('departmentModal').addEventListener('click', function(e) {
    if (e.target === this) {
        closeDepartmentModal();
    }
});

// View employees by department
function viewDepartmentEmployees(departmentId) {
    // Redirect to employees page with department filter
    window.location.href = `/employees?department_id=${departmentId}`;
}

