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
        if (!token) return false;

        const expiredDateStr = localStorage.getItem(this.EXPIRED_DATE_KEY);
        if (!expiredDateStr) return false;

        const expiredDate = new Date(expiredDateStr);
        const now = new Date();
        
        return now < expiredDate;
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
        return token ? { 'Authorization': `Bearer ${token}` } : {};
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

        // Nếu không phải 2xx, thử parse JSON để lấy error message
        if (!response.ok) {
            let errorResult;
            try {
                const responseText = await response.text();
                console.error(`API Error ${response.status}:`, responseText); // Debug
                
                if (responseText) {
                    try {
                        errorResult = JSON.parse(responseText);
                    } catch (e) {
                        // Nếu không parse được JSON, trả về text response
                        return { 
                            success: false, 
                            error: responseText || `Lỗi ${response.status}: ${response.statusText}`,
                            code: 'HTTP_ERROR',
                            status: response.status
                        };
                    }
                } else {
                    errorResult = {};
                }
            } catch (e) {
                // Nếu không đọc được response, trả về lỗi chung
                console.error('Error reading response:', e);
                return { 
                    success: false, 
                    error: `Lỗi ${response.status}: ${response.statusText}`,
                    code: 'HTTP_ERROR',
                    status: response.status
                };
            }
            
            // Xử lý lỗi validation từ Java
            if (errorResult.details && Array.isArray(errorResult.details)) {
                const validationErrors = errorResult.details.map(d => {
                    if (typeof d === 'string') return d;
                    if (d.message) return d.message;
                    if (d.field && d.message) return `${d.field}: ${d.message}`;
                    return JSON.stringify(d);
                }).join(', ');
                return {
                    success: false,
                    error: validationErrors || errorResult.message || 'Lỗi validation',
                    code: errorResult.code || 'VALIDATION_ERROR',
                    details: errorResult.details,
                    status: response.status
                };
            }
            
            // Xử lý lỗi từ Java ErrorResponse
            let errorMessage = errorResult.message || `Lỗi ${response.status}`;
            
            // Nếu có domain và details, thêm vào message
            if (errorResult.domain) {
                errorMessage = `[${errorResult.domain}] ${errorMessage}`;
            }
            
            if (errorResult.details && typeof errorResult.details === 'object' && !Array.isArray(errorResult.details)) {
                const detailStr = Object.entries(errorResult.details)
                    .map(([key, value]) => `${key}: ${value}`)
                    .join(', ');
                if (detailStr) {
                    errorMessage = `${errorMessage}\n${detailStr}`;
                }
            }
            
            return {
                success: false,
                error: errorMessage,
                code: errorResult.code || 'ERROR',
                details: errorResult.details,
                status: response.status,
                traceId: errorResult.traceId
            };
        }

        const result = await response.json();

        // Xử lý response từ Java backend
        if (result.code === 'OK' || result.operationType === 'Success') {
            // Nếu có pagination info, trả về kèm theo
            const response = {
                success: true,
                data: result.data,
                message: result.message,
                traceId: result.traceId
            };
            
            // Thêm thông tin pagination nếu có
            if (result.totalPages !== undefined) {
                response.totalPages = result.totalPages;
            }
            if (result.totalElements !== undefined) {
                response.totalElements = result.totalElements;
            }
            if (result.page !== undefined) {
                response.page = result.page;
            }
            if (result.pageSize !== undefined) {
                response.pageSize = result.pageSize;
            }
            
            return response;
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

