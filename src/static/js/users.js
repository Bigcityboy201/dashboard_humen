let currentPage = 0; // Java API uses 0-based pagination
const pageSize = 10;
let roles = [];

// Helper functions để xử lý active status
// Trong database/API: 0 = hoạt động, 1 = ngừng hoạt động (ngược với thông thường)
// Trong giao diện: true = hoạt động, false = không hoạt động
function isUserActive(activeValue) {
    // activeValue có thể là 0/1 (number) hoặc true/false (boolean)
    if (typeof activeValue === 'number') {
        return activeValue === 0; // 0 = hoạt động (true)
    }
    // Nếu là boolean, cần kiểm tra: false = 0 = hoạt động, true = 1 = không hoạt động
    // Nhưng thông thường boolean true = active, nên cần xử lý ngược
    // Giả sử: nếu API trả về 0 hoặc false => active (hoạt động)
    return activeValue === 0 || activeValue === false;
}

function getActiveValueForAPI(isActive) {
    // Chuyển từ boolean (true/false) sang boolean để gửi lên API
    // Nhưng logic ngược: true (hoạt động) => false (0), false (không hoạt động) => true (1)
    // Vì API: false (0) = hoạt động, true (1) = không hoạt động
    return !isActive;
}

// Load dữ liệu khi trang được tải
document.addEventListener('DOMContentLoaded', async () => {
    await loadRoles();
    await loadUsers();
});

// Load danh sách roles
async function loadRoles() {
    try {
        const result = await RolesAPI.getAll();
        console.log('Roles API Response:', result); // Debug: Kiểm tra response từ Java API
        
        if (result.success) {
            // Java API trả về SuccessResponse với data là array của RoleResponseDTO: [{ id, name, description }]
            roles = Array.isArray(result.data) ? result.data : [];
            console.log('Loaded roles:', roles); // Debug
            renderRolesCheckboxes();
        } else {
            console.error('Failed to load roles:', result.error);
            showAlert('Không thể tải danh sách quyền: ' + (result.error || 'Unknown error'), 'error');
        }
    } catch (error) {
        console.error('Error loading roles:', error);
        showAlert('Lỗi khi tải danh sách quyền: ' + error.message, 'error');
    }
}

// Render roles checkboxes
function renderRolesCheckboxes() {
    const container = document.getElementById('roles-checkboxes');
    if (!container) return;
    
    container.innerHTML = roles.map(role => `
        <label style="display: flex; align-items: center; gap: 0.5rem; cursor: pointer;">
            <input type="checkbox" name="roles" value="${role.id}" style="width: auto;">
            <span>${role.name}</span>
        </label>
    `).join('');
}

// Load danh sách users
async function loadUsers(page = 0) {
    currentPage = page;
    const loading = document.getElementById('loading');
    const tableBody = document.getElementById('users-table-body');
    
    loading.style.display = 'block';
    tableBody.innerHTML = '';

    const keyword = document.getElementById('filter-keyword').value.trim();

    const params = {
        page: currentPage,
        size: pageSize
    };

    try {
        const result = await UsersAPI.getAll(params);
        
        console.log('Users API Response:', result); // Debug: Kiểm tra response từ Java API
        
        loading.style.display = 'none';

        if (result.success) {
            // Java API trả về SuccessResponse với cấu trúc:
            // { data: List<UserResponseDTO>, totalElements, totalPages, page, pageSize }
            // data là array trực tiếp, không phải data.content
            const users = Array.isArray(result.data) ? result.data : [];
            // totalElements và totalPages được trả về từ apiCallWithAuth
            const totalElements = result.totalElements !== undefined ? result.totalElements : users.length;
            const totalPages = result.totalPages !== undefined ? result.totalPages : Math.ceil(totalElements / pageSize);
        
        console.log('Users Data:', users); // Debug
        console.log(`Loaded ${users.length} users, total: ${totalElements}, pages: ${totalPages}`); // Debug

        if (users.length === 0) {
            tableBody.innerHTML = `
                <tr>
                    <td colspan="8" class="empty-state">
                        <div class="empty-state-icon">📭</div>
                        <p>Không có dữ liệu người dùng</p>
                    </td>
                </tr>
            `;
        } else {
            // Filter by keyword if provided
            let filteredUsers = users;
            if (keyword) {
                filteredUsers = users.filter(user => {
                    const searchText = keyword.toLowerCase();
                    return (
                        (user.fullName || '').toLowerCase().includes(searchText) ||
                        (user.email || '').toLowerCase().includes(searchText) ||
                        (user.phone || '').includes(searchText) ||
                        (user.userName || '').toLowerCase().includes(searchText)
                    );
                });
            }

            tableBody.innerHTML = filteredUsers.map(user => {
                // Java API: roles là array của RoleResponseDTO với field 'name'
                const roleNames = (user.roles || []).map(r => r.name || r).join(', ') || 'Không có quyền';
                
                // Xử lý active status: 0 = hoạt động, 1 = ngừng hoạt động
                const isActive = isUserActive(user.active);
                const statusClass = isActive ? 'status-active' : 'status-inactive';
                const statusText = isActive ? 'Hoạt động' : 'Không hoạt động';
                const currentActiveValue = user.active; // Giữ nguyên giá trị gốc (0 hoặc 1)
                
                return `
                    <tr>
                        <td>${user.id}</td>
                        <td>${user.fullName || '-'}</td>
                        <td>${user.email || '-'}</td>
                        <td>${user.phone || '-'}</td>
                        <td>${user.userName || '-'}</td>
                        <td>${roleNames}</td>
                        <td>
                            <span class="status-badge ${statusClass}">
                                ${statusText}
                            </span>
                        </td>
                        <td>
                            <div class="action-buttons">
                                <button class="action-btn action-btn-edit" onclick="editUser(${user.id})" title="Sửa">
                                    ✏️
                                </button>
                                <button class="action-btn action-btn-view" onclick="toggleUserStatus(${user.id}, ${!isActive})" title="${isActive ? 'Vô hiệu hóa' : 'Kích hoạt'}">
                                    ${isActive ? '🔒' : '🔓'}
                                </button>
                                <button class="action-btn action-btn-view" onclick="openResetPasswordModal(${user.id})" title="Reset mật khẩu">
                                    🔑
                                </button>
                                <button class="action-btn action-btn-delete" onclick="deleteUser(${user.id})" title="Xóa">
                                    🗑️
                                </button>
                            </div>
                        </td>
                    </tr>
                `;
            }).join('');
        }

        // Render pagination
        renderPagination(totalPages, currentPage);
    } else {
        tableBody.innerHTML = `
            <tr>
                <td colspan="8" class="empty-state">
                    <div class="empty-state-icon">⚠️</div>
                    <p>${result.error || 'Lỗi khi tải dữ liệu'}</p>
                </td>
            </tr>
        `;
        showAlert(result.error || 'Lỗi khi tải danh sách người dùng', 'error');
    }
    } catch (error) {
        loading.style.display = 'none';
        console.error('Error loading users:', error);
        tableBody.innerHTML = `
            <tr>
                <td colspan="8" class="empty-state">
                    <div class="empty-state-icon">⚠️</div>
                    <p>Lỗi: ${error.message || 'Không thể tải dữ liệu'}</p>
                </td>
            </tr>
        `;
        showAlert('Lỗi khi tải danh sách người dùng: ' + error.message, 'error');
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
        <button ${currentPage === 0 ? 'disabled' : ''} onclick="loadUsers(${currentPage - 1})">‹ Trước</button>
        <span class="page-info">Trang ${currentPage + 1} / ${totalPages}</span>
        <button ${currentPage >= totalPages - 1 ? 'disabled' : ''} onclick="loadUsers(${currentPage + 1})">Sau ›</button>
    `;
    pagination.innerHTML = html;
}

// Reset filters
function resetFilters() {
    document.getElementById('filter-keyword').value = '';
    loadUsers(0);
}

// Handle keyword search with debounce
let keywordSearchTimeout;
function handleKeywordSearch(event) {
    clearTimeout(keywordSearchTimeout);
    
    keywordSearchTimeout = setTimeout(() => {
        loadUsers(0);
    }, 500);
    
    if (event.key === 'Enter') {
        clearTimeout(keywordSearchTimeout);
        loadUsers(0);
    }
}

// Open user modal
function openUserModal(userId = null) {
    const modal = document.getElementById('userModal');
    const form = document.getElementById('userForm');
    const modalTitle = document.getElementById('modal-title');
    const passwordGroup = document.getElementById('password-group');
    const activeGroup = document.getElementById('active-group');

    form.reset();
    document.getElementById('user-id').value = '';

    if (userId) {
        modalTitle.textContent = 'Sửa thông tin người dùng';
        passwordGroup.style.display = 'none';
        passwordGroup.querySelector('#password').removeAttribute('required');
        activeGroup.style.display = 'block';
        loadUserData(userId);
    } else {
        modalTitle.textContent = 'Thêm người dùng mới';
        passwordGroup.style.display = 'block';
        passwordGroup.querySelector('#password').setAttribute('required', 'required');
        activeGroup.style.display = 'none';
    }

    modal.classList.add('show');
}

// Close user modal
function closeUserModal() {
    const modal = document.getElementById('userModal');
    modal.classList.remove('show');
    document.getElementById('userForm').reset();
    document.getElementById('user-id').value = '';
}

// Load user data for editing
async function loadUserData(userId) {
    // Get user from list - Java API trả về SuccessResponse với data là array
    const result = await UsersAPI.getAll({ page: 0, size: 1000 });
    if (result.success) {
        // Java API: data là array trực tiếp
        const users = Array.isArray(result.data) ? result.data : [];
        const user = users.find(u => u.id === userId);
        
        if (user) {
            document.getElementById('user-id').value = user.id;
            document.getElementById('full-name').value = user.fullName || '';
            document.getElementById('email').value = user.email || '';
            document.getElementById('phone').value = user.phone || '';
            document.getElementById('user-name').value = user.userName || '';
            document.getElementById('address').value = user.address || '';
            document.getElementById('date-of-birth').value = user.dateOfBirth || '';
            // Xử lý active: 0 = hoạt động, 1 = ngừng hoạt động
            const isActive = isUserActive(user.active);
            document.getElementById('active').value = isActive ? 'true' : 'false';
            
            // Set roles - Java API: roles là array của RoleResponseDTO với field 'id'
            const checkboxes = document.querySelectorAll('input[name="roles"]');
            checkboxes.forEach(cb => {
                const roleId = parseInt(cb.value);
                cb.checked = (user.roles || []).some(r => {
                    const rId = r.id || r;
                    return rId === roleId;
                });
            });
        } else {
            showAlert('Không tìm thấy người dùng', 'error');
        }
    } else {
        showAlert(result.error || 'Không thể tải thông tin người dùng', 'error');
    }
}

// Edit user
function editUser(userId) {
    openUserModal(userId);
}

// Save user (create or update)
async function saveUser(event) {
    event.preventDefault();

    const userId = document.getElementById('user-id').value;
    const isEdit = !!userId;

    // Get selected roles
    const selectedRoles = Array.from(document.querySelectorAll('input[name="roles"]:checked'))
        .map(cb => parseInt(cb.value));

    if (selectedRoles.length === 0) {
        showAlert('Vui lòng chọn ít nhất một quyền', 'error');
        return;
    }

    // Java API: 
    // - UserRequestDTO (create) expects 'roles' (List<Integer>)
    // - AdminUpdateUserRequestDTO (update) expects 'roleIds' (List<Integer>)
    const data = {
        fullName: document.getElementById('full-name').value,
        email: document.getElementById('email').value,
        phone: document.getElementById('phone').value || null,
        userName: document.getElementById('user-name').value,
        address: document.getElementById('address').value || null,
        dateOfBirth: document.getElementById('date-of-birth').value || null
    };

    if (isEdit) {
        // Update: AdminUpdateUserRequestDTO expects 'roleIds'
        data.roleIds = selectedRoles;
        // Chuyển từ boolean sang boolean (ngược): true (hoạt động) => false (0), false (không hoạt động) => true (1)
        const isActive = document.getElementById('active').value === 'true';
        data.active = getActiveValueForAPI(isActive); // Trả về boolean ngược
    } else {
        // Create: UserRequestDTO expects 'roles'
        data.roles = selectedRoles;
        data.password = document.getElementById('password').value;
    }

    let result;
    if (isEdit) {
        result = await UsersAPI.update(userId, data);
    } else {
        result = await UsersAPI.create(data);
    }

    if (result.success) {
        showAlert(isEdit ? 'Cập nhật người dùng thành công!' : 'Thêm người dùng thành công!', 'success');
        closeUserModal();
        loadUsers(currentPage);
    } else {
        showAlert(result.error || 'Có lỗi xảy ra', 'error');
    }
}

// Toggle user status
async function toggleUserStatus(userId, isActive) {
    // isActive là boolean: true = hoạt động, false = không hoạt động
    // Cần chuyển sang boolean ngược: true => false (0 = hoạt động), false => true (1 = không hoạt động)
    const activeValue = getActiveValueForAPI(isActive);
    const action = isActive ? 'kích hoạt' : 'vô hiệu hóa';
    
    if (!confirm(`Bạn có chắc chắn muốn ${action} người dùng này?`)) {
        return;
    }

    // Gửi boolean (ngược) lên API: false = hoạt động, true = không hoạt động
    const result = await UsersAPI.updateStatus(userId, activeValue);
    if (result.success) {
        showAlert(`${isActive ? 'Kích hoạt' : 'Vô hiệu hóa'} người dùng thành công!`, 'success');
        loadUsers(currentPage);
    } else {
        showAlert(result.error || 'Có lỗi xảy ra', 'error');
    }
}

// Delete user
async function deleteUser(userId) {
    if (!confirm('Bạn có chắc chắn muốn xóa người dùng này?')) {
        return;
    }

    const result = await UsersAPI.delete(userId);
    if (result.success) {
        showAlert('Xóa người dùng thành công!', 'success');
        loadUsers(currentPage);
    } else {
        showAlert(result.error || 'Có lỗi xảy ra khi xóa', 'error');
    }
}

// Open reset password modal
function openResetPasswordModal(userId) {
    const modal = document.getElementById('resetPasswordModal');
    document.getElementById('reset-password-user-id').value = userId;
    document.getElementById('resetPasswordForm').reset();
    modal.classList.add('show');
}

// Close reset password modal
function closeResetPasswordModal() {
    const modal = document.getElementById('resetPasswordModal');
    modal.classList.remove('show');
    document.getElementById('resetPasswordForm').reset();
}

// Reset password
async function resetPassword(event) {
    event.preventDefault();

    const userId = document.getElementById('reset-password-user-id').value;
    const newPassword = document.getElementById('new-password').value;
    const confirmPassword = document.getElementById('confirm-password').value;

    if (newPassword !== confirmPassword) {
        showAlert('Mật khẩu xác nhận không khớp', 'error');
        return;
    }

    if (newPassword.length < 6) {
        showAlert('Mật khẩu phải có ít nhất 6 ký tự', 'error');
        return;
    }

    const result = await UsersAPI.resetPassword(userId, newPassword);
    if (result.success) {
        showAlert('Reset mật khẩu thành công!', 'success');
        closeResetPasswordModal();
    } else {
        showAlert(result.error || 'Có lỗi xảy ra', 'error');
    }
}

// Close modal when clicking outside
document.addEventListener('DOMContentLoaded', function() {
    const userModal = document.getElementById('userModal');
    const resetPasswordModal = document.getElementById('resetPasswordModal');
    
    if (userModal) {
        userModal.addEventListener('click', function(e) {
            if (e.target === this) {
                closeUserModal();
            }
        });
    }
    
    if (resetPasswordModal) {
        resetPasswordModal.addEventListener('click', function(e) {
            if (e.target === this) {
                closeResetPasswordModal();
            }
        });
    }
});
