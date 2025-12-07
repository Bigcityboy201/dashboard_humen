// Load dữ liệu khi trang được tải
document.addEventListener('DOMContentLoaded', () => {
    loadPositions();
});

// Load danh sách chức vụ
async function loadPositions() {
    const loading = document.getElementById('loading');
    const tableBody = document.getElementById('positions-table-body');
    
    loading.style.display = 'block';
    tableBody.innerHTML = '';

    const result = await PositionsAPI.getAll();
    
    console.log('Positions API Response:', result); // Debug

    loading.style.display = 'none';

    if (result.success) {
        // Xử lý trường hợp response bị wrap thêm một lần
        let data = result.data;
        if (data && data.data && Array.isArray(data.data)) {
            data = data.data;
        } else if (data && !Array.isArray(data) && Array.isArray(data.data)) {
            data = data.data;
        }
        
        const positions = Array.isArray(data) ? data : [];

        if (positions.length === 0) {
            tableBody.innerHTML = `
                <tr>
                    <td colspan="3" class="empty-state">
                        <div class="empty-state-icon">📭</div>
                        <p>Không có dữ liệu chức vụ</p>
                    </td>
                </tr>
            `;
        } else {
            tableBody.innerHTML = positions.map(pos => `
                <tr>
                    <td>${pos.PositionID}</td>
                    <td>${pos.PositionName || '-'}</td>
                    <td>
                        <div class="action-buttons">
                            <button class="action-btn action-btn-view" onclick="viewPositionEmployees(${pos.PositionID})" title="Xem nhân viên">
                                👥
                            </button>
                            <button class="action-btn action-btn-edit" onclick="editPosition(${pos.PositionID})" title="Sửa">
                                ✏️
                            </button>
                            <button class="action-btn action-btn-delete" onclick="deletePosition(${pos.PositionID})" title="Xóa">
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
                <td colspan="3" class="empty-state">
                    <div class="empty-state-icon">⚠️</div>
                    <p>${result.error || 'Lỗi khi tải dữ liệu'}</p>
                </td>
            </tr>
        `;
        showAlert(result.error || 'Lỗi khi tải danh sách chức vụ', 'error');
    }
}

// Open position modal
function openPositionModal(positionId = null) {
    const modal = document.getElementById('positionModal');
    const form = document.getElementById('positionForm');
    const modalTitle = document.getElementById('modal-title');

    form.reset();
    document.getElementById('position-id').value = '';

    if (positionId) {
        modalTitle.textContent = 'Sửa thông tin chức vụ';
        loadPositionData(positionId);
    } else {
        modalTitle.textContent = 'Thêm chức vụ mới';
    }

    modal.classList.add('show');
}

// Close position modal
function closePositionModal() {
    const modal = document.getElementById('positionModal');
    modal.classList.remove('show');
    document.getElementById('positionForm').reset();
}

// Load position data for editing
async function loadPositionData(positionId) {
    const result = await PositionsAPI.getById(positionId);
    if (result.success) {
        const pos = result.data;
        document.getElementById('position-id').value = pos.PositionID;
        document.getElementById('position-name').value = pos.PositionName || '';
    } else {
        showAlert(result.error || 'Không thể tải thông tin chức vụ', 'error');
    }
}

// Edit position
function editPosition(positionId) {
    openPositionModal(positionId);
}

// Save position (create or update)
async function savePosition(event) {
    event.preventDefault();

    const positionId = document.getElementById('position-id').value;
    const isEdit = !!positionId;

    const data = {
        PositionName: document.getElementById('position-name').value
    };

    let result;
    if (isEdit) {
        result = await PositionsAPI.update(positionId, data);
    } else {
        result = await PositionsAPI.create(data);
    }

    if (result.success) {
        showAlert(isEdit ? 'Cập nhật chức vụ thành công!' : 'Thêm chức vụ thành công!', 'success');
        closePositionModal();
        loadPositions();
    } else {
        showAlert(result.error || 'Có lỗi xảy ra', 'error');
    }
}

// Delete position
async function deletePosition(positionId) {
    if (!confirm('Bạn có chắc chắn muốn xóa chức vụ này? Lưu ý: Tất cả nhân viên có chức vụ này sẽ bị ảnh hưởng.')) {
        return;
    }

    const result = await PositionsAPI.delete(positionId);
    if (result.success) {
        showAlert('Xóa chức vụ thành công!', 'success');
        loadPositions();
    } else {
        showAlert(result.error || 'Có lỗi xảy ra khi xóa', 'error');
    }
}

// Close modal when clicking outside
document.getElementById('positionModal').addEventListener('click', function(e) {
    if (e.target === this) {
        closePositionModal();
    }
});

// View employees by position
function viewPositionEmployees(positionId) {
    // Redirect to employees page with position filter
    window.location.href = `/employees?position_id=${positionId}`;
}

