let currentPage = 0;
const pageSize = 10;
let roles = [];
let allUsers = [];

// Load dữ liệu khi trang được tải
document.addEventListener("DOMContentLoaded", async () => {
  // Kiểm tra quyền ADMIN
  if (!AuthManager.hasRole("ADMIN")) {
    showAlert("Bạn không có quyền truy cập trang này", "error");
    setTimeout(() => {
      window.location.href = "/";
    }, 2000);
    return;
  }

  // Set max date cho date input (hôm nay - 1 ngày)
  const dateOfBirthInput = document.getElementById("date-of-birth");
  if (dateOfBirthInput) {
    const today = new Date();
    today.setDate(today.getDate() - 1); // Hôm qua (để đảm bảo là quá khứ)
    const maxDate = today.toISOString().split("T")[0];
    dateOfBirthInput.setAttribute("max", maxDate);
  }

  await loadRoles();
  await loadUsers();
});

// Load danh sách roles
async function loadRoles() {
  try {
    const result = await RolesAPI.getAll();
    console.log("Roles API Response:", result); // Debug

    if (result.success) {
      // Xử lý response - có thể là mảng trực tiếp hoặc bị wrap
      if (Array.isArray(result.data)) {
        roles = result.data;
      } else if (result.data && Array.isArray(result.data.data)) {
        roles = result.data.data;
      } else {
        console.error("Roles data format không hợp lệ:", result.data);
        roles = [];
      }

      console.log("Loaded roles:", roles.length); // Debug
      renderRolesCheckboxes();
    } else {
      console.error("Load roles error:", result);
      showAlert(
        "Không thể tải danh sách vai trò: " +
          (result.error || result.message || "Lỗi không xác định"),
        "error"
      );
      roles = [];
    }
  } catch (error) {
    console.error("Load roles exception:", error);
    showAlert("Lỗi khi tải danh sách vai trò: " + error.message, "error");
    roles = [];
  }
}

// Render roles checkboxes
function renderRolesCheckboxes(selectedRoleIds = []) {
  const container = document.getElementById("roles-checkbox-group");
  if (!container) {
    console.error("Roles checkbox container not found");
    return;
  }

  container.innerHTML = "";

  if (!roles || roles.length === 0) {
    container.innerHTML =
      '<p style="color: var(--text-secondary); padding: 1rem; text-align: center;">Không có vai trò nào</p>';
    return;
  }

  roles.forEach((role) => {
    const label = document.createElement("label");
    label.style.display = "flex";
    label.style.alignItems = "center";
    label.style.gap = "0.5rem";
    label.style.cursor = "pointer";

    const checkbox = document.createElement("input");
    checkbox.type = "checkbox";
    checkbox.value = role.id;
    checkbox.id = `role-${role.id}`;
    checkbox.checked = selectedRoleIds.includes(role.id);

    const span = document.createElement("span");
    span.textContent = `${role.name}${
      role.description ? " - " + role.description : ""
    }`;

    label.appendChild(checkbox);
    label.appendChild(span);
    container.appendChild(label);
  });
}

// Load danh sách users
async function loadUsers(page = 0) {
  currentPage = page;
  const loading = document.getElementById("loading");
  const tableBody = document.getElementById("users-table-body");

  loading.style.display = "block";
  tableBody.innerHTML = "";

  const keyword = document.getElementById("filter-keyword").value.trim();
  const statusFilter = document.getElementById("filter-status").value;

  const params = {
    page: currentPage,
    size: pageSize,
  };

  // Thêm timestamp để tránh cache (nếu cần)
  // params._t = Date.now();

  try {
    const result = await UsersAPI.getAll(params);

    console.log("Users API Response:", result); // Debug

    loading.style.display = "none";

    if (result.success) {
      // Xử lý response từ Java - có thể là PagedResult hoặc mảng trực tiếp
      let users = [];

      if (Array.isArray(result.data)) {
        // Nếu result.data là mảng trực tiếp
        users = result.data;
      } else if (result.data && Array.isArray(result.data.content)) {
        // Nếu là PagedResult từ Spring (có thuộc tính content)
        users = result.data.content;
      } else if (result.data && Array.isArray(result.data.data)) {
        // Nếu bị wrap thêm một lần
        users = result.data.data;
      } else {
        console.error("Users data format không hợp lệ:", result.data);
        users = [];
      }

      allUsers = users;
      console.log(
        "Loaded users:",
        users.length,
        "Total users in allUsers:",
        allUsers.length
      ); // Debug

      // Filter by keyword (client-side)
      if (keyword) {
        users = users.filter(
          (user) =>
            (user.fullName &&
              user.fullName.toLowerCase().includes(keyword.toLowerCase())) ||
            (user.email &&
              user.email.toLowerCase().includes(keyword.toLowerCase())) ||
            (user.userName &&
              user.userName.toLowerCase().includes(keyword.toLowerCase())) ||
            (user.phone && user.phone.includes(keyword))
        );
      }

      // Filter by status
      // Logic ngược: active = false (0) = đang hoạt động, active = true (1) = đã khóa
      if (statusFilter !== "") {
        const filterActive = statusFilter === "true"; // true = đã khóa, false = đang hoạt động
        users = users.filter((user) => user.active === filterActive);
      }

      if (users.length === 0) {
        tableBody.innerHTML = `
                    <tr>
                        <td colspan="9" class="empty-state">
                            <p>Không tìm thấy người dùng nào</p>
                        </td>
                    </tr>
                `;
      } else {
        // Clear table trước khi render
        tableBody.innerHTML = "";
        users.forEach((user) => {
          const row = createUserRow(user);
          tableBody.appendChild(row);
          console.log("Rendered user:", user.id, user.fullName); // Debug
        });
        console.log("Total users rendered:", users.length); // Debug
      }

      // Render pagination - lấy từ result hoặc result.data
      let totalPages = result.totalPages || 0;

      // Nếu không có totalPages ở result, thử lấy từ result.data (PagedResult)
      if (
        totalPages === 0 &&
        result.data &&
        result.data.totalPages !== undefined
      ) {
        totalPages = result.data.totalPages;
      }

      renderPagination(totalPages, currentPage);
    } else {
      tableBody.innerHTML = `
                <tr>
                    <td colspan="9" class="empty-state">
                        <p>Lỗi: ${result.message || "Không thể tải dữ liệu"}</p>
                    </td>
                </tr>
            `;
    }
  } catch (error) {
    loading.style.display = "none";
    console.error("Error loading users:", error);
    tableBody.innerHTML = `
            <tr>
                <td colspan="9" class="empty-state">
                    <p>Lỗi: ${error.message || "Không thể tải dữ liệu"}</p>
                </td>
            </tr>
        `;
  }
}

// Tạo row cho table
function createUserRow(user) {
  const tr = document.createElement("tr");

  const rolesText =
    user.roles && user.roles.length > 0
      ? user.roles.map((r) => r.name).join(", ")
      : "Chưa có vai trò";

  // Logic ngược: active = false (0) = đang hoạt động, active = true (1) = đã khóa
  const statusBadge = !user.active
    ? '<span class="badge badge-success">Đang hoạt động</span>'
    : '<span class="badge badge-danger">Đã khóa</span>';

  tr.innerHTML = `
        <td>${user.id}</td>
        <td>${user.fullName || "-"}</td>
        <td>${user.userName || "-"}</td>
        <td>${user.email || "-"}</td>
        <td>${user.phone || "-"}</td>
        <td>${rolesText}</td>
        <td>${statusBadge}</td>
        <td>${formatDate(user.createdAt)}</td>
        <td>
            <div class="action-buttons">
                <button class="btn btn-sm btn-primary" onclick="editUser(${
                  user.id
                })" title="Sửa">
                    ✏️
                </button>
                <button class="btn btn-sm btn-warning" onclick="toggleUserStatus(${
                  user.id
                }, ${user.active})" title="${user.active ? "Mở khóa" : "Khóa"}">
                    ${user.active ? "🔓" : "🔒"}
                </button>
                <button class="btn btn-sm btn-info" onclick="openResetPasswordModal(${
                  user.id
                })" title="Đặt lại mật khẩu">
                    🔑
                </button>
                <button class="btn btn-sm btn-danger" onclick="deleteUser(${
                  user.id
                })" title="Xóa">
                    🗑️
                </button>
            </div>
        </td>
    `;

  return tr;
}

// Render pagination
function renderPagination(totalPages, currentPage) {
  const pagination = document.getElementById("pagination");
  pagination.innerHTML = "";

  if (totalPages <= 1) return;

  // Previous button
  const prevBtn = document.createElement("button");
  prevBtn.className = "btn btn-secondary";
  prevBtn.textContent = "← Trước";
  prevBtn.disabled = currentPage === 0;
  prevBtn.onclick = () => loadUsers(currentPage - 1);
  pagination.appendChild(prevBtn);

  // Page numbers
  const maxPages = 5;
  let startPage = Math.max(0, currentPage - Math.floor(maxPages / 2));
  let endPage = Math.min(totalPages - 1, startPage + maxPages - 1);

  if (endPage - startPage < maxPages - 1) {
    startPage = Math.max(0, endPage - maxPages + 1);
  }

  if (startPage > 0) {
    const firstBtn = document.createElement("button");
    firstBtn.className = "btn btn-secondary";
    firstBtn.textContent = "1";
    firstBtn.onclick = () => loadUsers(0);
    pagination.appendChild(firstBtn);

    if (startPage > 1) {
      const ellipsis = document.createElement("span");
      ellipsis.textContent = "...";
      ellipsis.style.padding = "0 0.5rem";
      pagination.appendChild(ellipsis);
    }
  }

  for (let i = startPage; i <= endPage; i++) {
    const pageBtn = document.createElement("button");
    pageBtn.className = `btn ${
      i === currentPage ? "btn-primary" : "btn-secondary"
    }`;
    pageBtn.textContent = i + 1;
    pageBtn.onclick = () => loadUsers(i);
    pagination.appendChild(pageBtn);
  }

  if (endPage < totalPages - 1) {
    if (endPage < totalPages - 2) {
      const ellipsis = document.createElement("span");
      ellipsis.textContent = "...";
      ellipsis.style.padding = "0 0.5rem";
      pagination.appendChild(ellipsis);
    }

    const lastBtn = document.createElement("button");
    lastBtn.className = "btn btn-secondary";
    lastBtn.textContent = totalPages;
    lastBtn.onclick = () => loadUsers(totalPages - 1);
    pagination.appendChild(lastBtn);
  }

  // Next button
  const nextBtn = document.createElement("button");
  nextBtn.className = "btn btn-secondary";
  nextBtn.textContent = "Sau →";
  nextBtn.disabled = currentPage >= totalPages - 1;
  nextBtn.onclick = () => loadUsers(currentPage + 1);
  pagination.appendChild(nextBtn);
}

// Mở modal thêm user
function openUserModal() {
  const modal = document.getElementById("userModal");
  if (!modal) {
    console.error("User modal not found");
    showAlert("Không tìm thấy form thêm người dùng", "error");
    return;
  }

  document.getElementById("user-id").value = "";
  const form = document.getElementById("userForm");
  if (form) {
    form.reset();
  }

  const modalTitle = document.getElementById("modal-title");
  if (modalTitle) {
    modalTitle.textContent = "Thêm người dùng mới";
  }

  const passwordGroup = document.getElementById("password-group");
  if (passwordGroup) {
    passwordGroup.style.display = "block";
  }

  const passwordInput = document.getElementById("password");
  if (passwordInput) {
    passwordInput.required = true;
  }

  const activeGroup = document.getElementById("active-group");
  if (activeGroup) {
    activeGroup.style.display = "none";
  }

  const userNameInput = document.getElementById("user-name");
  if (userNameInput) {
    userNameInput.disabled = false;
  }

  renderRolesCheckboxes();
  modal.classList.add("show");
}

// Đóng modal
function closeUserModal() {
  const modal = document.getElementById("userModal");
  modal.classList.remove("show");
  document.getElementById("userForm").reset();
}

// Sửa user
async function editUser(id) {
  const user = allUsers.find((u) => u.id === id);
  if (!user) {
    showAlert("Không tìm thấy người dùng", "error");
    return;
  }

  document.getElementById("user-id").value = user.id;
  document.getElementById("full-name").value = user.fullName || "";
  document.getElementById("user-name").value = user.userName || "";
  document.getElementById("email").value = user.email || "";
  document.getElementById("phone").value = user.phone || "";
  document.getElementById("address").value = user.address || "";
  document.getElementById("date-of-birth").value = user.dateOfBirth
    ? formatDateForInput(user.dateOfBirth)
    : "";
  // Logic ngược: active = false (0) = đang hoạt động, active = true (1) = đã khóa
  document.getElementById("active").value = user.active ? "true" : "false";

  // Format date for input
  if (user.dateOfBirth) {
    const date = new Date(user.dateOfBirth);
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, "0");
    const day = String(date.getDate()).padStart(2, "0");
    document.getElementById("date-of-birth").value = `${year}-${month}-${day}`;
  }

  const selectedRoleIds = user.roles ? user.roles.map((r) => r.id) : [];
  renderRolesCheckboxes(selectedRoleIds);

  document.getElementById("modal-title").textContent =
    "Sửa thông tin người dùng";
  document.getElementById("password-group").style.display = "none";
  document.getElementById("password").required = false;
  document.getElementById("active-group").style.display = "block";
  document.getElementById("user-name").disabled = true; // Không cho sửa username

  const modal = document.getElementById("userModal");
  modal.classList.add("show");
}

// Lưu user
async function saveUser(event) {
  event.preventDefault();

  const userId = document.getElementById("user-id").value;
  const isEdit = !!userId;

  // Lấy danh sách role đã chọn
  const roleCheckboxes = document.querySelectorAll(
    '#roles-checkbox-group input[type="checkbox"]:checked'
  );
  const roleIds = Array.from(roleCheckboxes).map((cb) => parseInt(cb.value));

  if (roleIds.length === 0) {
    showAlert("Vui lòng chọn ít nhất một vai trò", "error");
    return;
  }

  // Lấy và validate form data
  const fullName = document.getElementById("full-name").value.trim();
  const email = document.getElementById("email").value.trim();
  const phone = document.getElementById("phone").value.trim();
  const address = document.getElementById("address").value.trim();
  const dateOfBirth = document.getElementById("date-of-birth").value;

  // Validation cho các field required
  if (!fullName) {
    showAlert("Họ và tên không được để trống", "error");
    return;
  }

  if (!email) {
    showAlert("Email không được để trống", "error");
    return;
  }

  // Validate email format
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  if (!emailRegex.test(email)) {
    showAlert("Email không hợp lệ", "error");
    return;
  }

  // Validate phone nếu có
  if (phone) {
    const phoneRegex = /^\+?\d{9,15}$/;
    if (!phoneRegex.test(phone)) {
      showAlert(
        "Số điện thoại không hợp lệ. Vui lòng nhập 9-15 chữ số, có thể bắt đầu bằng +",
        "error"
      );
      return;
    }
  }

  // Validate dateOfBirth nếu có - phải là quá khứ
  let dateOfBirthValue = null;
  if (dateOfBirth) {
    const selectedDate = new Date(dateOfBirth);
    const today = new Date();
    today.setHours(0, 0, 0, 0);
    selectedDate.setHours(0, 0, 0, 0);

    if (selectedDate >= today) {
      showAlert("Ngày sinh phải là ngày trong quá khứ", "error");
      return;
    }
    dateOfBirthValue = dateOfBirth;
  }

  // Tạo payload - chuyển empty string thành null
  const payload = {
    fullName: fullName,
    email: email,
    phone: phone || null, // Chuyển empty string thành null
    address: address || null, // Chuyển empty string thành null
    dateOfBirth: dateOfBirthValue, // null nếu không có hoặc empty
    roleIds: roleIds,
  };

  // Nếu thêm mới → cần password + userName
  if (!isEdit) {
    const userName = document.getElementById("user-name").value.trim();
    const password = document.getElementById("password").value;

    if (!userName) {
      showAlert("Username không được để trống", "error");
      return;
    }

    if (!password) {
      showAlert("Mật khẩu không được để trống", "error");
      return;
    }

    if (password.length < 6) {
      showAlert("Mật khẩu phải có ít nhất 6 ký tự", "error");
      return;
    }

    if (!/(?=.*[A-Z])(?=.*[0-9])/.test(password)) {
      showAlert("Mật khẩu phải chứa ít nhất 1 chữ hoa và 1 số", "error");
      return;
    }

    payload.userName = userName;
    payload.password = password;
  }

  // Nếu Sửa → xử lý active
  if (isEdit) {
    const activeValue = document.getElementById("active").value;
    payload.active = activeValue === "true"; // true = đã khóa, false = đang hoạt động
  }

  console.log("Payload to send:", JSON.stringify(payload, null, 2)); // Debug

  try {
    let result;
    if (isEdit) {
      // UPDATE USER
      console.log("Updating user ID:", userId); // Debug
      result = await UsersAPI.update(parseInt(userId), payload);
    } else {
      // CREATE USER
      console.log("Creating new user"); // Debug
      result = await UsersAPI.create(payload);
    }

    console.log("API Result:", result); // Debug

    if (result.success) {
      showAlert(
        isEdit
          ? "Cập nhật người dùng thành công"
          : "Thêm người dùng thành công",
        "success"
      );
      closeUserModal();
      await loadUsers(currentPage);
    } else {
      // Hiển thị lỗi chi tiết hơn
      let errorMsg = result.error || result.message || "Lỗi khi lưu người dùng";

      // Nếu là lỗi 500, thêm thông tin chi tiết
      if (result.status === 500) {
        errorMsg = `Lỗi server (500): ${errorMsg}`;
        if (result.traceId) {
          errorMsg += `\nTrace ID: ${result.traceId}`;
        }
        errorMsg += "\n\nVui lòng kiểm tra console để xem chi tiết lỗi.";
      }

      // Xử lý validation errors
      if (result.details) {
        if (Array.isArray(result.details)) {
          const validationErrors = result.details
            .map((d) => {
              if (typeof d === "string") return d;
              if (d.message) return d.message;
              if (d.field)
                return `${d.field}: ${d.message || "Lỗi validation"}`;
              return JSON.stringify(d);
            })
            .join("\n");
          errorMsg = validationErrors || errorMsg;
        } else if (typeof result.details === "object") {
          const detailStr = Object.entries(result.details)
            .map(([key, value]) => `${key}: ${value}`)
            .join(", ");
          errorMsg = `${errorMsg}\n${detailStr}`;
        }
      }

      showAlert(errorMsg, "error");
      console.error("Error details:", result); // Debug
      console.error("Payload sent:", payload); // Debug
    }
  } catch (err) {
    console.error("Exception:", err);
    showAlert("Lỗi khi kết nối đến máy chủ: " + err.message, "error");
  }
}

// Toggle user status
// Logic ngược: active = false (0) = đang hoạt động, active = true (1) = đã khóa
async function toggleUserStatus(id, currentActive) {
  // currentActive = true nghĩa là đang bị khóa, muốn mở khóa thì set active = false
  // currentActive = false nghĩa là đang hoạt động, muốn khóa thì set active = true
  const newActive = !currentActive; // Đảo ngược trạng thái
  const action = newActive ? "khóa" : "mở khóa";

  if (!confirm(`Bạn có chắc chắn muốn ${action} người dùng này?`)) {
    return;
  }

  try {
    const result = await UsersAPI.updateStatus(id, newActive);

    if (result.success) {
      showAlert(
        `${
          action.charAt(0).toUpperCase() + action.slice(1)
        } người dùng thành công`,
        "success"
      );
      await loadUsers(currentPage);
    } else {
      showAlert(result.message || "Cập nhật thất bại", "error");
    }
  } catch (error) {
    console.error("Error updating status:", error);
    showAlert(error.message || "Có lỗi xảy ra", "error");
  }
}

// Xóa user
async function deleteUser(id) {
  if (
    !confirm(
      "Bạn có chắc chắn muốn xóa người dùng này? Hành động này không thể hoàn tác."
    )
  ) {
    return;
  }

  try {
    const result = await UsersAPI.delete(id);

    if (result.success) {
      showAlert("Xóa người dùng thành công", "success");
      await loadUsers(currentPage);
    } else {
      showAlert(result.message || "Xóa thất bại", "error");
    }
  } catch (error) {
    console.error("Error deleting user:", error);
    showAlert(error.message || "Có lỗi xảy ra", "error");
  }
}

// Mở modal reset password
function openResetPasswordModal(id) {
  const modal = document.getElementById("resetPasswordModal");
  document.getElementById("reset-password-user-id").value = id;
  document.getElementById("resetPasswordForm").reset();
  modal.classList.add("show");
}

// Đóng modal reset password
function closeResetPasswordModal() {
  const modal = document.getElementById("resetPasswordModal");
  modal.classList.remove("show");
  document.getElementById("resetPasswordForm").reset();
}

// Reset password
async function resetPassword(event) {
  event.preventDefault();

  const userId = document.getElementById("reset-password-user-id").value;
  const newPassword = document.getElementById("reset-password").value;
  const confirmPassword = document.getElementById(
    "reset-password-confirm"
  ).value;

  if (newPassword !== confirmPassword) {
    showAlert("Mật khẩu xác nhận không khớp", "error");
    return;
  }

  // Validate password format
  if (newPassword.length < 6) {
    showAlert("Mật khẩu phải có ít nhất 6 ký tự", "error");
    return;
  }

  if (!/(?=.*[A-Z])(?=.*[0-9])/.test(newPassword)) {
    showAlert("Mật khẩu phải chứa ít nhất 1 chữ hoa và 1 số", "error");
    return;
  }

  try {
    const result = await UsersAPI.resetPassword(parseInt(userId), newPassword);

    if (result.success) {
      showAlert("Đặt lại mật khẩu thành công", "success");
      closeResetPasswordModal();
    } else {
      showAlert(result.message || "Đặt lại mật khẩu thất bại", "error");
    }
  } catch (error) {
    console.error("Error resetting password:", error);
    showAlert(error.message || "Có lỗi xảy ra", "error");
  }
}

// Handle keyword search
let searchTimeout;
function handleKeywordSearch(event) {
  if (event.key === "Enter") {
    loadUsers(0);
    return;
  }

  clearTimeout(searchTimeout);
  searchTimeout = setTimeout(() => {
    loadUsers(0);
  }, 500);
}

// Reset filters
function resetFilters() {
  document.getElementById("filter-keyword").value = "";
  document.getElementById("filter-status").value = "";
  loadUsers(0);
}

// Format date for display
function formatDate(dateString) {
  if (!dateString) return "-";
  const date = new Date(dateString);
  return date.toLocaleDateString("vi-VN");
}

// Format date for input
function formatDateForInput(dateString) {
  if (!dateString) return "";
  const date = new Date(dateString);
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, "0");
  const day = String(date.getDate()).padStart(2, "0");
  return `${year}-${month}-${day}`;
}

// Close modal when clicking outside
window.onclick = function (event) {
  const userModal = document.getElementById("userModal");
  const resetPasswordModal = document.getElementById("resetPasswordModal");

  if (event.target === userModal) {
    closeUserModal();
  }
  if (event.target === resetPasswordModal) {
    closeResetPasswordModal();
  }
};

// Close modal with Escape key
document.addEventListener("keydown", function (event) {
  if (event.key === "Escape") {
    closeUserModal();
    closeResetPasswordModal();
  }
});
