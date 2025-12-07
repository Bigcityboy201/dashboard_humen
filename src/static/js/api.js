// API Base URL - Sử dụng Java backend
const JAVA_BASE_URL = 'http://localhost:8080';

// Helper function để gọi API Python qua Java proxy (sử dụng apiCallWithAuth từ auth.js)
async function apiCallPython(endpoint, method = 'GET', data = null) {
    // Tất cả API Python đều đi qua Java proxy với prefix /api/python
    const proxyEndpoint = `/api/python${endpoint}`;
    return await apiCallWithAuth(proxyEndpoint, method, data);
}

// Helper function để gọi API Java trực tiếp (sử dụng apiCallWithAuth từ auth.js)
async function apiCallJava(endpoint, method = 'GET', data = null) {
    return await apiCallWithAuth(endpoint, method, data);
}

// ========== JAVA API - User Management (ADMIN only) ==========
const UsersAPI = {
    // Lấy danh sách users với pagination
    getAll: async (params = {}) => {
        const queryParams = new URLSearchParams();
        if (params.page !== undefined) queryParams.append('page', params.page);
        if (params.size !== undefined) queryParams.append('size', params.size);
        
        const queryString = queryParams.toString();
        const endpoint = `/users${queryString ? '?' + queryString : ''}`;
        return await apiCallJava(endpoint, 'GET');
    },

    // Tạo user mới
    create: async (data) => {
        // data: { fullName, email, phone, userName, password, address, dateOfBirth, roles: [roleIds] }
        return await apiCallJava('/users', 'POST', data);
    },

    // Cập nhật user (Admin update)
    update: async (id, data) => {
        // data: { fullName?, email?, phone?, address?, dateOfBirth?, active?, roleIds? }
        return await apiCallJava(`/users/${id}`, 'PUT', data);
    },

    // Cập nhật trạng thái active/inactive
    updateStatus: async (id, isActive) => {
        return await apiCallJava(`/users/${id}/status`, 'PUT', { active: isActive });
    },

    // Xóa user
    delete: async (id) => {
        return await apiCallJava(`/users/${id}`, 'DELETE');
    },

    // Reset password
    resetPassword: async (id, newPassword) => {
        return await apiCallJava(`/users/${id}/reset-password`, 'PUT', { password: newPassword });
    }
};

// ========== JAVA API - Profile Management (ADMIN, HR_MANAGER) ==========
const ProfileAPI = {
    // Lấy profile hiện tại
    getProfile: async () => {
        return await apiCallJava('/profile', 'GET');
    },

    // Cập nhật profile hiện tại
    updateProfile: async (data) => {
        // data: { fullName?, email?, phone?, address?, dateOfBirth? }
        return await apiCallJava('/profile', 'PUT', data);
    },

    // Đổi mật khẩu
    changePassword: async (data) => {
        // data: { oldPassword, newPassword }
        return await apiCallJava('/profile/change-password', 'PUT', data);
    }
};

// ========== JAVA API - Role Management ==========
const RolesAPI = {
    // Lấy danh sách tất cả roles
    getAll: async () => {
        return await apiCallJava('/api/roles', 'GET');
    },

    // Tạo role mới
    create: async (data) => {
        // data: { name, description? }
        return await apiCallJava('/api/roles', 'POST', data);
    }
};

// ========== PYTHON API - Employees (HR_MANAGER hoặc ADMIN) ==========
const EmployeesAPI = {
    getAll: async (params = {}) => {
        const queryParams = new URLSearchParams();
        if (params.department_id) queryParams.append('department_id', params.department_id);
        if (params.position_id) queryParams.append('position_id', params.position_id);
        if (params.status) queryParams.append('status', params.status);
        if (params.keyword) queryParams.append('keyword', params.keyword);
        if (params.page) queryParams.append('page', params.page);
        if (params.size) queryParams.append('size', params.size);

        const queryString = queryParams.toString();
        return await apiCallPython(`/employees${queryString ? '?' + queryString : ''}`);
    },

    getByDepartment: async (departmentId, params = {}) => {
        const queryParams = new URLSearchParams();
        if (params.page) queryParams.append('page', params.page);
        if (params.size) queryParams.append('size', params.size);
        const queryString = queryParams.toString();
        return await apiCallPython(`/departments/${departmentId}/employees${queryString ? '?' + queryString : ''}`);
    },

    getByPosition: async (positionId, params = {}) => {
        const queryParams = new URLSearchParams();
        if (params.page) queryParams.append('page', params.page);
        if (params.size) queryParams.append('size', params.size);
        const queryString = queryParams.toString();
        return await apiCallPython(`/positions/${positionId}/employees${queryString ? '?' + queryString : ''}`);
    },

    getById: async (id) => {
        return await apiCallPython(`/employees/${id}`);
    },

    create: async (data) => {
        return await apiCallPython('/employees', 'POST', data);
    },

    update: async (id, data) => {
        return await apiCallPython(`/employees/${id}`, 'PUT', data);
    },

    delete: async (id) => {
        return await apiCallPython(`/employees/${id}`, 'DELETE');
    }
};

// ========== PYTHON API - Departments (HR_MANAGER hoặc ADMIN) ==========
const DepartmentsAPI = {
    getAll: async () => {
        return await apiCallPython('/departments');
    },

    getById: async (id) => {
        return await apiCallPython(`/departments/${id}`);
    },

    create: async (data) => {
        return await apiCallPython('/departments', 'POST', data);
    },

    update: async (id, data) => {
        return await apiCallPython(`/departments/${id}`, 'PUT', data);
    },

    delete: async (id) => {
        return await apiCallPython(`/departments/${id}`, 'DELETE');
    },

    // Lấy danh sách nhân viên trong phòng ban
    getEmployees: async (id, params = {}) => {
        const queryParams = new URLSearchParams();
        if (params.page) queryParams.append('page', params.page);
        if (params.size) queryParams.append('size', params.size);
        const queryString = queryParams.toString();
        return await apiCallPython(`/departments/${id}/employees${queryString ? '?' + queryString : ''}`);
    }
};

// ========== PYTHON API - Positions (HR_MANAGER hoặc ADMIN) ==========
const PositionsAPI = {
    getAll: async () => {
        return await apiCallPython('/positions');
    },

    getById: async (id) => {
        return await apiCallPython(`/positions/${id}`);
    },

    create: async (data) => {
        return await apiCallPython('/positions', 'POST', data);
    },

    update: async (id, data) => {
        return await apiCallPython(`/positions/${id}`, 'PUT', data);
    },

    delete: async (id) => {
        return await apiCallPython(`/positions/${id}`, 'DELETE');
    },

    // Lấy danh sách nhân viên có chức vụ này
    getEmployees: async (id, params = {}) => {
        const queryParams = new URLSearchParams();
        if (params.page) queryParams.append('page', params.page);
        if (params.size) queryParams.append('size', params.size);
        const queryString = queryParams.toString();
        return await apiCallPython(`/positions/${id}/employees${queryString ? '?' + queryString : ''}`);
    }
};

// ========== PYTHON API - Salaries (PAYROLL_MANAGER hoặc ADMIN) ==========
const SalariesAPI = {
    getAll: async (params = {}) => {
        const queryParams = new URLSearchParams();
        if (params.employee_id) queryParams.append('employee_id', params.employee_id);
        if (params.year) queryParams.append('year', params.year);
        const queryString = queryParams.toString();
        return await apiCallPython(`/salaries${queryString ? '?' + queryString : ''}`);
    },

    getById: async (id) => {
        return await apiCallPython(`/salaries/${id}`);
    },

    generate: async (data) => {
        return await apiCallPython('/salaries/generate', 'POST', data);
    },

    update: async (id, data) => {
        return await apiCallPython(`/salaries/${id}`, 'PUT', data);
    },

    delete: async (id) => {
        return await apiCallPython(`/salaries/${id}`, 'DELETE');
    },

    getMySalaries: async (employeeId) => {
        return await apiCallPython(`/salaries/my?employee_id=${employeeId}`);
    },

    getStatistics: async (month, year) => {
        const queryParams = new URLSearchParams();
        if (month) queryParams.append('month', month);
        if (year) queryParams.append('year', year);
        const queryString = queryParams.toString();
        return await apiCallPython(`/salaries/statistics${queryString ? '?' + queryString : ''}`);
    }
};

// ========== PYTHON API - Attendance (HR_MANAGER hoặc ADMIN) ==========
const AttendanceAPI = {
    getAll: async (params = {}) => {
        const queryParams = new URLSearchParams();
        if (params.employee_id) queryParams.append('employee_id', params.employee_id);
        if (params.year) queryParams.append('year', params.year);
        const queryString = queryParams.toString();
        return await apiCallPython(`/attendance${queryString ? '?' + queryString : ''}`);
    },

    getById: async (id) => {
        return await apiCallPython(`/attendance/${id}`);
    },

    create: async (data) => {
        return await apiCallPython('/attendance', 'POST', data);
    },

    update: async (id, data) => {
        return await apiCallPython(`/attendance/${id}`, 'PUT', data);
    },

    delete: async (id) => {
        return await apiCallPython(`/attendance/${id}`, 'DELETE');
    },

    getStatistics: async (month, year) => {
        const queryParams = new URLSearchParams();
        if (month) queryParams.append('month', month);
        if (year) queryParams.append('year', year);
        const queryString = queryParams.toString();
        return await apiCallPython(`/attendance/statistics${queryString ? '?' + queryString : ''}`);
    }
};

// ========== PYTHON API - Dividends (PAYROLL_MANAGER hoặc ADMIN) ==========
const DividendsAPI = {
    getAll: async () => {
        return await apiCallPython('/dividends');
    },

    getById: async (id) => {
        return await apiCallPython(`/dividends/${id}`);
    },

    create: async (data) => {
        return await apiCallPython('/dividends', 'POST', data);
    },

    update: async (id, data) => {
        return await apiCallPython(`/dividends/${id}`, 'PUT', data);
    },

    delete: async (id) => {
        return await apiCallPython(`/dividends/${id}`, 'DELETE');
    }
};

// ========== PYTHON API - Dashboard ==========
const DashboardAPI = {
    // Lấy thống kê tổng hợp cho trang chủ
    getOverview: async () => {
        return await apiCallPython('/dashboard/overview');
    }
};

// ========== PYTHON API - Search ==========
const SearchAPI = {
    // Tìm kiếm toàn hệ thống
    searchAll: async (keyword) => {
        return await apiCallPython(`/search?keyword=${encodeURIComponent(keyword)}`);
    }
};

// ========== PYTHON API - Reports ==========
const ReportsAPI = {
    // Báo cáo lương theo năm
    getSalaryReport: async (year) => {
        return await apiCallPython(`/reports/salary?year=${year}`);
    },

    // Báo cáo chấm công theo năm
    getAttendanceReport: async (year) => {
        return await apiCallPython(`/reports/attendance?year=${year}`);
    },

    // Báo cáo tài chính tổng hợp (lương + cổ tức) theo năm
    getFinancialReport: async (year) => {
        return await apiCallPython(`/reports/financial?year=${year}`);
    }
};

// ========== Utility functions ==========
function showAlert(message, type = 'info') {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type}`;
    alertDiv.innerHTML = `
        <span>${message}</span>
        <button class="alert-close" onclick="this.parentElement.remove()">&times;</button>
    `;

    const container = document.querySelector('.container');
    if (container) {
        container.insertBefore(alertDiv, container.firstChild);
    } else {
        document.body.insertBefore(alertDiv, document.body.firstChild);
    }

    // Tự động xóa sau 5 giây
    setTimeout(() => {
        alertDiv.remove();
    }, 5000);
}

function formatDate(dateString) {
    if (!dateString) return '-';
    const date = new Date(dateString);
    return date.toLocaleDateString('vi-VN');
}

function formatCurrency(amount) {
    if (!amount) return '-';
    return new Intl.NumberFormat('vi-VN', {
        style: 'currency',
        currency: 'VND'
    }).format(amount);
}
