// Load profile khi trang được tải
document.addEventListener('DOMContentLoaded', async () => {
    // Kiểm tra quyền (ADMIN hoặc HR_MANAGER)
    if (!AuthManager.hasAnyRole('ADMIN', 'HR_MANAGER')) {
        showAlert('Bạn không có quyền truy cập trang này', 'error');
        setTimeout(() => {
            window.location.href = '/';
        }, 2000);
        return;
    }

    await loadProfile();
});

// Load thông tin profile
async function loadProfile() {
    const loading = document.getElementById('loading');
    const content = document.getElementById('profile-content');
    
    loading.style.display = 'block';
    content.style.display = 'none';

    try {
        const result = await ProfileAPI.getProfile();
        
        loading.style.display = 'none';

        if (result.success) {
            const profile = result.data;
            
            // Điền thông tin vào form
            document.getElementById('full-name').value = profile.fullName || '';
            document.getElementById('email').value = profile.email || '';
            document.getElementById('phone').value = profile.phone || '';
            document.getElementById('address').value = profile.address || '';
            document.getElementById('user-name').value = profile.userName || '';
            
            // Format date for input
            if (profile.dateOfBirth) {
                const date = new Date(profile.dateOfBirth);
                const year = date.getFullYear();
                const month = String(date.getMonth() + 1).padStart(2, '0');
                const day = String(date.getDate()).padStart(2, '0');
                document.getElementById('date-of-birth').value = `${year}-${month}-${day}`;
            }

            // Hiển thị roles
            const rolesDisplay = document.getElementById('roles-display');
            if (profile.roles && profile.roles.length > 0) {
                rolesDisplay.innerHTML = profile.roles.map(role => 
                    `<span class="badge badge-primary">${role.name}</span>`
                ).join('');
            } else {
                rolesDisplay.innerHTML = '<span style="color: var(--text-secondary);">Chưa có vai trò</span>';
            }

            content.style.display = 'block';
        } else {
            showAlert(result.error || 'Không thể tải thông tin profile', 'error');
        }
    } catch (error) {
        loading.style.display = 'none';
        console.error('Error loading profile:', error);
        showAlert(error.message || 'Có lỗi xảy ra khi tải thông tin', 'error');
    }
}

// Cập nhật profile
async function updateProfile(event) {
    event.preventDefault();
    
    const updateData = {
        fullName: document.getElementById('full-name').value.trim(),
        email: document.getElementById('email').value.trim(),
        phone: document.getElementById('phone').value.trim(),
        address: document.getElementById('address').value.trim(),
        dateOfBirth: document.getElementById('date-of-birth').value
    };

    try {
        const result = await ProfileAPI.updateProfile(updateData);
        
        if (result.success) {
            showAlert('Cập nhật thông tin thành công', 'success');
            // Reload profile để cập nhật thông tin mới nhất
            await loadProfile();
        } else {
            showAlert(result.error || 'Cập nhật thất bại', 'error');
        }
    } catch (error) {
        console.error('Error updating profile:', error);
        showAlert(error.message || 'Có lỗi xảy ra', 'error');
    }
}

// Đổi mật khẩu
async function changePassword(event) {
    event.preventDefault();
    
    const oldPassword = document.getElementById('old-password').value;
    const newPassword = document.getElementById('new-password').value;
    const confirmPassword = document.getElementById('confirm-password').value;

    // Validation
    if (newPassword !== confirmPassword) {
        showAlert('Mật khẩu xác nhận không khớp', 'error');
        return;
    }

    if (newPassword.length < 6) {
        showAlert('Mật khẩu phải có ít nhất 6 ký tự', 'error');
        return;
    }

    // Kiểm tra mật khẩu có chứa chữ hoa và số không
    const hasUpperCase = /[A-Z]/.test(newPassword);
    const hasNumber = /\d/.test(newPassword);
    
    if (!hasUpperCase || !hasNumber) {
        showAlert('Mật khẩu phải chứa ít nhất 1 chữ hoa và 1 số', 'error');
        return;
    }

    try {
        const result = await ProfileAPI.changePassword({
            oldPassword: oldPassword,
            newPassword: newPassword
        });
        
        if (result.success) {
            showAlert('Đổi mật khẩu thành công', 'success');
            // Reset form
            document.getElementById('changePasswordForm').reset();
        } else {
            showAlert(result.error || 'Đổi mật khẩu thất bại', 'error');
        }
    } catch (error) {
        console.error('Error changing password:', error);
        showAlert(error.message || 'Có lỗi xảy ra', 'error');
    }
}















