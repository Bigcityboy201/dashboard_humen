// Load dữ liệu khi trang được tải
document.addEventListener('DOMContentLoaded', () => {
    loadDividends();
});

// Load danh sách cổ tức
async function loadDividends() {
    const loading = document.getElementById('loading');
    const tableBody = document.getElementById('dividends-table-body');
    
    loading.style.display = 'block';
    tableBody.innerHTML = '';

    const result = await DividendsAPI.getAll();
    
    console.log('Dividends API Response:', result); // Debug

    loading.style.display = 'none';

    if (result.success) {
        // Xử lý trường hợp response bị wrap thêm một lần
        let data = result.data;
        if (data && data.data && Array.isArray(data.data)) {
            data = data.data;
        } else if (data && !Array.isArray(data) && Array.isArray(data.data)) {
            data = data.data;
        }
        
        const dividends = Array.isArray(data) ? data : [];

        if (dividends.length === 0) {
            tableBody.innerHTML = `
                <tr>
                    <td colspan="5" class="empty-state">
                        <div class="empty-state-icon">📭</div>
                        <p>Không có dữ liệu cổ tức</p>
                    </td>
                </tr>
            `;
        } else {
            tableBody.innerHTML = dividends.map(div => {
                // Map field names: DividendAmount -> Amount, DividendDate -> Date
                const amount = div.Amount || div.DividendAmount || 0;
                const date = div.DividendDate || div.Date;
                const description = div.Description || '-';
                
                return `
                <tr>
                    <td>${div.DividendID}</td>
                    <td>${formatDate(date) || '-'}</td>
                    <td><strong>${formatCurrency(amount)}</strong></td>
                    <td>${description}</td>
                    <td>
                        <div class="action-buttons">
                            <button class="action-btn action-btn-view" onclick="viewDividend(${div.DividendID})" title="Xem chi tiết">
                                👁️
                            </button>
                            <button class="action-btn action-btn-edit" onclick="editDividend(${div.DividendID})" title="Sửa">
                                ✏️
                            </button>
                            <button class="action-btn action-btn-delete" onclick="deleteDividend(${div.DividendID})" title="Xóa">
                                🗑️
                            </button>
                        </div>
                    </td>
                </tr>
            `;
            }).join('');
        }
    } else {
        tableBody.innerHTML = `
            <tr>
                <td colspan="5" class="empty-state">
                    <div class="empty-state-icon">⚠️</div>
                    <p>${result.error || 'Lỗi khi tải dữ liệu'}</p>
                </td>
            </tr>
        `;
        showAlert(result.error || 'Lỗi khi tải danh sách cổ tức', 'error');
    }
}

// Open dividend modal
function openDividendModal(dividendId = null) {
    const modal = document.getElementById('dividendModal');
    const form = document.getElementById('dividendForm');
    const modalTitle = document.getElementById('modal-title');

    form.reset();
    document.getElementById('dividend-id').value = '';

    if (dividendId) {
        modalTitle.textContent = 'Sửa thông tin cổ tức';
        loadDividendData(dividendId);
    } else {
        modalTitle.textContent = 'Thêm cổ tức';
    }

    modal.classList.add('show');
}

// Close dividend modal
function closeDividendModal() {
    const modal = document.getElementById('dividendModal');
    modal.classList.remove('show');
    document.getElementById('dividendForm').reset();
}

// Load dividend data for editing
async function loadDividendData(dividendId) {
    const result = await DividendsAPI.getById(dividendId);
    if (result.success) {
        const div = result.data;
        // Map field names: DividendAmount -> Amount
        const amount = div.Amount || div.DividendAmount || 0;
        const date = div.DividendDate || div.Date || '';
        
        document.getElementById('dividend-id').value = div.DividendID;
        document.getElementById('dividend-date').value = date;
        document.getElementById('amount').value = amount;
        document.getElementById('description').value = div.Description || '';
    } else {
        showAlert(result.error || 'Không thể tải thông tin cổ tức', 'error');
    }
}

// View dividend details
async function viewDividend(dividendId) {
    const modal = document.getElementById('dividendDetailModal');
    const content = document.getElementById('dividend-detail-content');
    
    modal.classList.add('show');
    content.innerHTML = `
        <div class="loading">
            <div class="spinner"></div>
            <p>Đang tải thông tin...</p>
        </div>
    `;
    
    const result = await DividendsAPI.getById(dividendId);
    if (result.success) {
        const div = result.data;
        // Map field names: DividendAmount -> Amount
        const amount = div.Amount || div.DividendAmount || 0;
        const date = div.DividendDate || div.Date;
        const description = div.Description;
        
        content.innerHTML = `
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1.5rem;">
                <div>
                    <h3 style="margin-bottom: 1rem; color: var(--primary-color); border-bottom: 2px solid var(--border-color); padding-bottom: 0.5rem;">Thông tin cơ bản</h3>
                    <div style="margin-bottom: 1rem;">
                        <strong>ID cổ tức:</strong>
                        <div style="color: var(--text-secondary);">${div.DividendID}</div>
                    </div>
                    <div style="margin-bottom: 1rem;">
                        <strong>Ngày chi:</strong>
                        <div style="color: var(--text-secondary);">${formatDate(date) || '-'}</div>
                    </div>
                    ${div.EmployeeID ? `
                    <div style="margin-bottom: 1rem;">
                        <strong>ID Nhân viên:</strong>
                        <div style="color: var(--text-secondary);">${div.EmployeeID}</div>
                    </div>
                    ` : ''}
                </div>
                
                <div>
                    <h3 style="margin-bottom: 1rem; color: var(--primary-color); border-bottom: 2px solid var(--border-color); padding-bottom: 0.5rem;">Thông tin tài chính</h3>
                    <div style="margin-bottom: 1rem;">
                        <strong>Số tiền:</strong>
                        <div style="color: var(--primary-color); font-size: 1.5rem; font-weight: bold;">${formatCurrency(amount)}</div>
                    </div>
                </div>
            </div>
            
            ${description ? `
            <div style="margin-top: 2rem; padding-top: 1.5rem; border-top: 2px solid var(--border-color);">
                <h3 style="margin-bottom: 1rem; color: var(--primary-color);">Mô tả</h3>
                <div style="padding: 1rem; background: var(--bg-color); border-radius: 0.5rem; color: var(--text-secondary);">
                    ${description}
                </div>
            </div>
            ` : ''}
        `;
    } else {
        content.innerHTML = `
            <div class="alert alert-error">
                <span>${result.error || 'Không thể tải thông tin cổ tức'}</span>
            </div>
        `;
    }
}

// Close dividend detail modal
function closeDividendDetailModal() {
    const modal = document.getElementById('dividendDetailModal');
    modal.classList.remove('show');
}

// Edit dividend
function editDividend(dividendId) {
    openDividendModal(dividendId);
}

// Save dividend (create or update)
async function saveDividend(event) {
    event.preventDefault();

    const dividendId = document.getElementById('dividend-id').value;
    const isEdit = !!dividendId;

    const dividendDate = document.getElementById('dividend-date').value;
    const amount = parseFloat(document.getElementById('amount').value) || 0;
    const description = document.getElementById('description').value.trim() || null;

    // Map to API expected format (backend expects DividendAmount, DividendDate)
    const data = {
        DividendDate: dividendDate,
        DividendAmount: amount
    };
    
    // Thêm Description nếu có (nếu backend hỗ trợ)
    if (description) {
        data.Description = description;
    }

    console.log('Save dividend data:', data); // Debug

    try {
        let result;
        if (isEdit) {
            result = await DividendsAPI.update(dividendId, data);
        } else {
            result = await DividendsAPI.create(data);
        }

        console.log('Save dividend result:', result); // Debug

        if (result.success) {
            showAlert(isEdit ? 'Cập nhật cổ tức thành công!' : 'Thêm cổ tức thành công!', 'success');
            closeDividendModal();
            loadDividends();
        } else {
            showAlert(result.error || 'Có lỗi xảy ra', 'error');
            console.error('Save dividend error:', result); // Debug
        }
    } catch (error) {
        console.error('Save dividend exception:', error); // Debug
        showAlert(error.message || 'Có lỗi xảy ra khi lưu cổ tức', 'error');
    }
}

// Delete dividend
async function deleteDividend(dividendId) {
    if (!confirm('Bạn có chắc chắn muốn xóa cổ tức này?')) {
        return;
    }

    const result = await DividendsAPI.delete(dividendId);
    if (result.success) {
        showAlert('Xóa cổ tức thành công!', 'success');
        loadDividends();
    } else {
        showAlert(result.error || 'Có lỗi xảy ra khi xóa', 'error');
    }
}

// Close modals when clicking outside
document.getElementById('dividendModal')?.addEventListener('click', function(e) {
    if (e.target === this) closeDividendModal();
});
document.getElementById('dividendDetailModal')?.addEventListener('click', function(e) {
    if (e.target === this) closeDividendDetailModal();
});

