// Login Page Handler
document.addEventListener('DOMContentLoaded', function() {
    const loginForm = document.getElementById('loginForm');
    const userNameInput = document.getElementById('userName');
    const passwordInput = document.getElementById('password');
    const togglePasswordBtn = document.getElementById('togglePassword');
    const loginBtn = document.getElementById('loginBtn');
    const errorAlert = document.getElementById('errorAlert');
    const errorMessage = document.getElementById('errorMessage');

    // Toggle password visibility
    togglePasswordBtn.addEventListener('click', function() {
        const type = passwordInput.getAttribute('type') === 'password' ? 'text' : 'password';
        passwordInput.setAttribute('type', type);
        
        // Update icon (simple toggle)
        const svg = togglePasswordBtn.querySelector('svg');
        if (type === 'text') {
            svg.innerHTML = `
                <path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"></path>
                <line x1="1" y1="1" x2="23" y2="23"></line>
            `;
        } else {
            svg.innerHTML = `
                <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path>
                <circle cx="12" cy="12" r="3"></circle>
            `;
        }
    });

    // Handle form submission
    loginForm.addEventListener('submit', async function(e) {
        e.preventDefault();

        const userName = userNameInput.value.trim();
        const password = passwordInput.value;

        // Validation
        if (!userName || !password) {
            showError('Vui lòng nhập đầy đủ thông tin đăng nhập');
            return;
        }

        // Show loading state
        setLoadingState(true);

        try {
            const response = await fetch(`${AuthManager.JAVA_BASE_URL}/auth/signIn`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    userName: userName,
                    password: password
                })
            });

            const result = await response.json();

            if (response.ok && result.code === 'OK' && result.data) {
                const { token, expiredDate, user } = result.data;
                
                // Lưu thông tin đăng nhập
                AuthManager.saveAuth(token, user, expiredDate);

                // Redirect dựa trên role
                redirectByRole(user.roles);
            } else {
                // Hiển thị lỗi
                const errorMsg = result.message || 'Tên đăng nhập hoặc mật khẩu không đúng';
                showError(errorMsg);
            }
        } catch (error) {
            console.error('Login error:', error);
            showError('Không thể kết nối đến server. Vui lòng thử lại sau.');
        } finally {
            setLoadingState(false);
        }
    });

    function setLoadingState(loading) {
        const btnText = loginBtn.querySelector('.btn-text');
        const btnLoader = loginBtn.querySelector('.btn-loader');

        if (loading) {
            loginBtn.disabled = true;
            btnText.classList.add('hide');
            btnLoader.classList.add('show');
        } else {
            loginBtn.disabled = false;
            btnText.classList.remove('hide');
            btnLoader.classList.remove('show');
        }
    }

    function showError(message) {
        errorMessage.textContent = message;
        errorAlert.style.display = 'flex';
        
        // Auto hide after 5 seconds
        setTimeout(() => {
            errorAlert.style.display = 'none';
        }, 5000);
    }

    function redirectByRole(roles) {
        if (!roles || roles.length === 0) {
            window.location.href = '/';
            return;
        }

        // Lấy role đầu tiên (hoặc role chính)
        const roleNames = roles.map(r => r.name || r);
        
        // Redirect theo role
        if (roleNames.includes('ADMIN')) {
            window.location.href = '/';
        } else if (roleNames.includes('HR_MANAGER')) {
            window.location.href = '/employees';
        } else if (roleNames.includes('PAYROLL_MANAGER')) {
            window.location.href = '/salaries';
        } else {
            window.location.href = '/';
        }
    }

    // Focus vào input đầu tiên
    userNameInput.focus();
});

