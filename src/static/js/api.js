// API Base URL
const API_BASE_URL = '';

// Helper function để gọi API
async function apiCall(endpoint, method = 'GET', data = null) {
    const options = {
        method: method,
        headers: {
            'Content-Type': 'application/json',
        }
    };

    if (data && (method === 'POST' || method === 'PUT')) {
        options.body = JSON.stringify(data);
    }

    try {
        const response = await fetch(`${API_BASE_URL}${endpoint}`, options);
        const result = await response.json();

        if (result.operationType === 'Success') {
            return {
                success: true,
                data: result.data,
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

// Employees API
const EmployeesAPI = {
    getAll: async (params = {}) => {
        const queryParams = new URLSearchParams();
        if (params.department_id) queryParams.append('department_id', params.department_id);
        if (params.status) queryParams.append('status', params.status);
        if (params.page) queryParams.append('page', params.page);
        if (params.size) queryParams.append('size', params.size);

        const queryString = queryParams.toString();
        return await apiCall(`/employees${queryString ? '?' + queryString : ''}`);
    },

    getById: async (id) => {
        return await apiCall(`/employees/${id}`);
    },

    create: async (data) => {
        return await apiCall('/employees', 'POST', data);
    },

    update: async (id, data) => {
        return await apiCall(`/employees/${id}`, 'PUT', data);
    },

    delete: async (id) => {
        return await apiCall(`/employees/${id}`, 'DELETE');
    }
};

// Departments API
const DepartmentsAPI = {
    getAll: async () => {
        return await apiCall('/departments');
    },

    getById: async (id) => {
        return await apiCall(`/departments/${id}`);
    },

    create: async (data) => {
        return await apiCall('/departments', 'POST', data);
    },

    update: async (id, data) => {
        return await apiCall(`/departments/${id}`, 'PUT', data);
    },

    delete: async (id) => {
        return await apiCall(`/departments/${id}`, 'DELETE');
    }
};

// Positions API
const PositionsAPI = {
    getAll: async () => {
        return await apiCall('/positions');
    },

    getById: async (id) => {
        return await apiCall(`/positions/${id}`);
    },

    create: async (data) => {
        return await apiCall('/positions', 'POST', data);
    },

    update: async (id, data) => {
        return await apiCall(`/positions/${id}`, 'PUT', data);
    },

    delete: async (id) => {
        return await apiCall(`/positions/${id}`, 'DELETE');
    }
};

// Utility functions
function showAlert(message, type = 'info') {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type}`;
    alertDiv.innerHTML = `
        <span>${message}</span>
        <button class="alert-close" onclick="this.parentElement.remove()">&times;</button>
    `;

    const container = document.querySelector('.container');
    container.insertBefore(alertDiv, container.firstChild);

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

