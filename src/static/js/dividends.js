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

    loading.style.display = 'none';

    if (result.success) {
        const dividends = result.data || [];

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
            tableBody.innerHTML = dividends.map(div => `
                <tr>
                    <td>${div.DividendID}</td>
                    <td>${formatDate(div.DividendDate || div.Date) || '-'}</td>
                    <td><strong>${formatCurrency(div.Amount)}</strong></td>
                    <td>${div.Description || '-'}</td>
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
            `).join('');
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
        document.getElementById('dividend-id').value = div.DividendID;
        document.getElementById('dividend-date').value = div.DividendDate || div.Date || '';
        document.getElementById('amount').value = div.Amount || 0;
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
                        <div style="color: var(--text-secondary);">${formatDate(div.DividendDate || div.Date) || '-'}</div>
                    </div>
                </div>
                
                <div>
                    <h3 style="margin-bottom: 1rem; color: var(--primary-color); border-bottom: 2px solid var(--border-color); padding-bottom: 0.5rem;">Thông tin tài chính</h3>
                    <div style="margin-bottom: 1rem;">
                        <strong>Số tiền:</strong>
                        <div style="color: var(--primary-color); font-size: 1.5rem; font-weight: bold;">${formatCurrency(div.Amount)}</div>
                    </div>
                </div>
            </div>
            
            ${div.Description ? `
            <div style="margin-top: 2rem; padding-top: 1.5rem; border-top: 2px solid var(--border-color);">
                <h3 style="margin-bottom: 1rem; color: var(--primary-color);">Mô tả</h3>
                <div style="padding: 1rem; background: var(--bg-color); border-radius: 0.5rem; color: var(--text-secondary);">
                    ${div.Description}
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

    const data = {
        DividendDate: document.getElementById('dividend-date').value,
        Amount: parseFloat(document.getElementById('amount').value) || 0,
        Description: document.getElementById('description').value || null
    };

    // Map to API expected format
    if (!isEdit || !data.DividendDate) {
        data.Date = data.DividendDate;
    }

    let result;
    if (isEdit) {
        result = await DividendsAPI.update(dividendId, data);
    } else {
        result = await DividendsAPI.create(data);
    }

    if (result.success) {
        showAlert(isEdit ? 'Cập nhật cổ tức thành công!' : 'Thêm cổ tức thành công!', 'success');
        closeDividendModal();
        loadDividends();
    } else {
        showAlert(result.error || 'Có lỗi xảy ra', 'error');
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

