// Navbar Management với Role-based Menu
document.addEventListener('DOMContentLoaded', function() {
    const navbar = document.querySelector('.navbar-nav');
    if (!navbar) return;

    const user = AuthManager.getUser();
    const roles = AuthManager.getUserRoles();

    // Kiểm tra authentication
    if (!AuthManager.isAuthenticated()) {
        window.location.href = '/login';
        return;
    }

    // Thêm menu items theo role
    const menuItems = [];

    // Menu cho tất cả user đã đăng nhập
    menuItems.push({ href: '/', text: 'Trang chủ', roles: ['ADMIN', 'HR_MANAGER', 'PAYROLL_MANAGER'] });

    // Menu cho HR_MANAGER và ADMIN
    if (AuthManager.hasAnyRole('ADMIN', 'HR_MANAGER')) {
        menuItems.push(
            { href: '/employees', text: 'Nhân viên', roles: ['ADMIN', 'HR_MANAGER'] },
            { href: '/departments', text: 'Phòng ban', roles: ['ADMIN', 'HR_MANAGER'] },
            { href: '/positions', text: 'Chức vụ', roles: ['ADMIN', 'HR_MANAGER'] },
            { href: '/attendance', text: 'Chấm công', roles: ['ADMIN', 'HR_MANAGER'] }
        );
    }

    // Menu cho PAYROLL_MANAGER và ADMIN
    if (AuthManager.hasAnyRole('ADMIN', 'PAYROLL_MANAGER')) {
        menuItems.push(
            { href: '/salaries', text: 'Lương', roles: ['ADMIN', 'PAYROLL_MANAGER'] },
            { href: '/dividends', text: 'Cổ tức', roles: ['ADMIN', 'PAYROLL_MANAGER'] }
        );
    }

    // Menu cho ADMIN
    if (AuthManager.hasRole('ADMIN')) {
        menuItems.push(
            { href: '/users', text: 'Người dùng', roles: ['ADMIN'] }
        );
    }

    // Render menu items
    menuItems.forEach(item => {
        if (item.roles.some(role => roles.includes(role))) {
            const li = document.createElement('li');
            const a = document.createElement('a');
            a.href = item.href;
            a.textContent = item.text;
            
            // Highlight active menu
            if (window.location.pathname === item.href || 
                (item.href === '/' && window.location.pathname === '/')) {
                a.classList.add('active');
            }
            
            li.appendChild(a);
            navbar.appendChild(li);
        }
    });

    // Thêm user info và logout button
    const userInfo = document.createElement('li');
    userInfo.className = 'navbar-user';
    userInfo.innerHTML = `
        <div class="user-dropdown">
            <button class="user-button">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path>
                    <circle cx="12" cy="7" r="4"></circle>
                </svg>
                <span class="user-name">${user?.userName || 'User'}</span>
                <span class="user-role">${roles[0] || ''}</span>
            </button>
            <div class="user-dropdown-menu">
                <div class="user-info">
                    <div class="user-info-name">${user?.fullName || user?.userName || 'User'}</div>
                    <div class="user-info-email">${user?.email || ''}</div>
                    <div class="user-info-roles">
                        ${roles.map(r => `<span class="role-badge">${r}</span>`).join('')}
                    </div>
                </div>
                ${AuthManager.hasAnyRole('ADMIN', 'HR_MANAGER') ? `
                <button class="profile-btn" onclick="window.location.href='/profile'" style="width: 100%; padding: 0.75rem; margin-bottom: 0.5rem; background: var(--primary-color); color: white; border: none; border-radius: 0.25rem; cursor: pointer; display: flex; align-items: center; gap: 0.5rem; justify-content: center;">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path>
                        <circle cx="12" cy="7" r="4"></circle>
                    </svg>
                    Hồ sơ của tôi
                </button>
                ` : ''}
                <button class="logout-btn" onclick="AuthManager.logout()">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"></path>
                        <polyline points="16 17 21 12 16 7"></polyline>
                        <line x1="21" y1="12" x2="9" y2="12"></line>
                    </svg>
                    Đăng xuất
                </button>
            </div>
        </div>
    `;
    navbar.appendChild(userInfo);

    // Toggle dropdown
    const userButton = userInfo.querySelector('.user-button');
    const dropdownMenu = userInfo.querySelector('.user-dropdown-menu');
    
    userButton.addEventListener('click', function(e) {
        e.stopPropagation();
        dropdownMenu.classList.toggle('show');
    });

    // Close dropdown when clicking outside
    document.addEventListener('click', function(e) {
        if (!userInfo.contains(e.target)) {
            dropdownMenu.classList.remove('show');
        }
    });
});

