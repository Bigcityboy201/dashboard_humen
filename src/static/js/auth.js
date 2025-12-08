// Authentication Management
const AuthManager = {
    JAVA_BASE_URL: 'http://localhost:8080',
    TOKEN_KEY: 'auth_token',
    USER_KEY: 'user_data',
    EXPIRED_DATE_KEY: 'token_expired_date',

    // Lưu thông tin đăng nhập
    saveAuth(token, user, expiredDate) {
        localStorage.setItem(this.TOKEN_KEY, token);
        localStorage.setItem(this.USER_KEY, JSON.stringify(user));
        localStorage.setItem(this.EXPIRED_DATE_KEY, expiredDate);
    },

    // Lấy token
    getToken() {
        return localStorage.getItem(this.TOKEN_KEY);
    },

    // Lấy thông tin user
    getUser() {
        const userStr = localStorage.getItem(this.USER_KEY);
        return userStr ? JSON.parse(userStr) : null;
    },

    // Kiểm tra token còn hợp lệ không
    isTokenValid() {
        const token = this.getToken();
        if (!token) {
            console.warn('No token found in localStorage');
            return false;
        }

        const expiredDateStr = localStorage.getItem(this.EXPIRED_DATE_KEY);
        if (!expiredDateStr) {
            console.warn('No expired date found in localStorage');
            return false;
        }

        const expiredDate = new Date(expiredDateStr);
        const now = new Date();
        
        const isValid = now < expiredDate;
        if (!isValid) {
            console.warn('Token has expired. Expired date:', expiredDateStr, 'Current date:', now);
        }
        
        return isValid;
    },

    // Kiểm tra đã đăng nhập chưa
    isAuthenticated() {
        return this.isTokenValid();
    },

    // Lấy roles của user
    getUserRoles() {
        const user = this.getUser();
        if (!user || !user.roles) return [];
        return user.roles.map(role => role.name || role);
    },

    // Kiểm tra user có role cụ thể không
    hasRole(roleName) {
        const roles = this.getUserRoles();
        return roles.includes(roleName);
    },

    // Kiểm tra user có một trong các roles không
    hasAnyRole(...roleNames) {
        const roles = this.getUserRoles();
        return roleNames.some(role => roles.includes(role));
    },

    // Xóa thông tin đăng nhập
    clearAuth() {
        localStorage.removeItem(this.TOKEN_KEY);
        localStorage.removeItem(this.USER_KEY);
        localStorage.removeItem(this.EXPIRED_DATE_KEY);
    },

    // Đăng xuất
    async logout() {
        const token = this.getToken();
        
        if (token) {
            try {
                await fetch(`${this.JAVA_BASE_URL}/auth/logout`, {
                    method: 'POST',
                    headers: {
                        'Authorization': `Bearer ${token}`,
                        'Content-Type': 'application/json'
                    }
                });
            } catch (error) {
                console.error('Logout error:', error);
            }
        }

        this.clearAuth();
        window.location.href = '/login';
    },

    // Lấy header Authorization cho API calls
    getAuthHeader() {
        const token = this.getToken();
        if (!token) {
            console.warn('No token available for API call');
            return {};
        }
        if (!this.isTokenValid()) {
            console.warn('Token is expired or invalid');
            // Vẫn gửi token để server xác định, nhưng có thể sẽ bị reject
        }
        return { 'Authorization': `Bearer ${token}` };
    }
};

// API Helper với authentication
async function apiCallWithAuth(endpoint, method = 'GET', data = null) {
    const options = {
        method: method,
        headers: {
            'Content-Type': 'application/json',
            ...AuthManager.getAuthHeader()
        }
    };

    if (data && (method === 'POST' || method === 'PUT')) {
        options.body = JSON.stringify(data);
    }

    try {
        const response = await fetch(`${AuthManager.JAVA_BASE_URL}${endpoint}`, options);
        
        // Nếu 401 Unauthorized, đăng xuất
        if (response.status === 401) {
            AuthManager.clearAuth();
            window.location.href = '/login';
            return { success: false, error: 'Phiên đăng nhập đã hết hạn' };
        }

        // Nếu 403 Forbidden
        if (response.status === 403) {
            return { success: false, error: 'Bạn không có quyền truy cập tài nguyên này', code: 'FORBIDDEN' };
        }

        const result = await response.json();

        // Xử lý response từ Java backend
        if (result.code === 'OK' || result.operationType === 'Success') {
            // Java API trả về SuccessResponse với các field: data, totalElements, totalPages, page, pageSize
            return {
                success: true,
                data: result.data,
                totalElements: result.totalElements,
                totalPages: result.totalPages,
                page: result.page,
                pageSize: result.pageSize,
                message: result.message,
                traceId: result.traceId
            };
        } else {
            return {
                success: false,
                error: result.message || 'Có lỗi xảy ra',
                code: result.code,
                details: result.details,
                traceId: result.traceId
            };
        }
    } catch (error) {
        return {
            success: false,
            error: error.message || 'Lỗi kết nối đến server'
        };
    }
}

// Kiểm tra authentication khi load trang
function checkAuth() {
    if (!AuthManager.isAuthenticated()) {
        // Nếu không phải trang login, redirect về login
        if (window.location.pathname !== '/login') {
            window.location.href = '/login';
        }
    } else {
        // Nếu đã đăng nhập mà đang ở trang login, redirect về trang chủ
        if (window.location.pathname === '/login') {
            window.location.href = '/';
        }
    }
}

// Chạy check khi load trang
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', checkAuth);
} else {
    checkAuth();
}

