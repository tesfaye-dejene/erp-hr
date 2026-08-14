/**
 * PeopleOps — HR Employee Directory frontend
 * Talks to /api/v1/hr/ endpoints
 */

const API = "/api/v1/hr";

// ---------- State ----------
const state = {
  page: 1,
  pageSize: 20,
  totalPages: 0,
  search: "",
  departmentId: "",
  selected: new Set(),
  employees: [],
  editingId: null,
};

// ---------- DOM helpers ----------
const $ = (sel) => document.querySelector(sel);
const $$ = (sel) => [...document.querySelectorAll(sel)];

function toast(message, type = "info") {
  const el = document.createElement("div");
  el.className = `toast toast-${type}`;
  el.textContent = message;
  $("#toasts").appendChild(el);
  setTimeout(() => el.remove(), 3500);
}

function statusBadge(status) {
  const cls = `badge badge-${status}` || "badge";
  return `<span class="${cls}">${status.replace("_", " ")}</span>`;
}

function initials(first, last) {
  return `${(first || "?")[0]}${(last || "?")[0]}`.toUpperCase();
}

function formatDate(d) {
  if (!d) return "—";
  try {
    return new Date(d).toLocaleDateString(undefined, {
      year: "numeric",
      month: "short",
      day: "numeric",
    });
  } catch {
    return d;
  }
}




// ---------- API ----------
async function api(path, options = {}) {
  const res = await fetch(`${API}${path}`, {
    headers: {
      "Content-Type": "application/json",
      Accept: "application/json",
      ...(options.headers || {}),
    },
    ...options,
  });

  let data = null;
  const text = await res.text();
  try {
    data = text ? JSON.parse(text) : null;
  } catch {
    data = { success: false, error: { message: text || res.statusText } };
  }

  if (!res.ok) {
    const msg =
      data?.error?.message ||
      (typeof data?.error === "string" ? data.error : null) ||
      data?.message ||
      `Request failed (${res.status})`;
    throw new Error(typeof msg === "object" ? JSON.stringify(msg) : msg);
  }
  return data;
}

// ---------- Load employees ----------
async function loadEmployees() {
  const params = new URLSearchParams({
    page: state.page,
    page_size: state.pageSize,
  });
  if (state.search) params.set("search", state.search);
  if (state.departmentId) params.set("department_id", state.departmentId);

  const tbody = $("#employeeBody");
  tbody.innerHTML = `<tr class="empty-row"><td colspan="8">Loading…</td></tr>`;

  try {
    const res = await api(`/employees/?${params}`);
    const data = res.data || res;
    state.employees = data.items || [];
    state.totalPages = data.total_pages || 0;

    renderTable();
    renderPagination(data);
    updateDeptFilterOptions();
  } catch (err) {
    tbody.innerHTML = `<tr class="empty-row"><td colspan="8">Error: ${err.message}</td></tr>`;
    toast(err.message, "error");
  }
}

function renderTable() {
  const tbody = $("#employeeBody");
  if (!state.employees.length) {
    tbody.innerHTML = `<tr class="empty-row"><td colspan="8">No employees found. Click “+ Add Employee” to create one.</td></tr>`;
    return;
  }

  tbody.innerHTML = state.employees
    .map((e) => {
      const checked = state.selected.has(e.id) ? "checked" : "";
      const selectedCls = state.selected.has(e.id) ? "selected" : "";
      return `
      <tr class="${selectedCls}" data-id="${e.id}">
        <td class="col-check">
          <input type="checkbox" class="row-check" data-id="${e.id}" ${checked} />
        </td>
        <td>
          <div class="emp-name">
            <div class="avatar">${initials(e.first_name, e.last_name)}</div>
            <span>${escapeHtml(e.full_name || e.first_name + " " + e.last_name)}</span>
          </div>
        </td>
        <td><span class="emp-email">${escapeHtml(e.email)}</span></td>
        <td>${escapeHtml(e.department_name || "—")}</td>
        <td>${formatDate(e.hire_date)}</td>
        <td>${statusBadge(e.status)}</td>
        <td><span class="leave-dot ${e.is_on_leave ? "yes" : "no"}" title="${e.is_on_leave ? "On leave" : "Not on leave"}"></span></td>
        <td class="col-actions">
          <div class="action-btns">
            <button class="btn btn-sm btn-ghost btn-edit" data-id="${e.id}">Edit</button>
            <button class="btn btn-sm btn-danger btn-delete" data-id="${e.id}">Delete</button>
          </div>
        </td>
      </tr>`;
    })
    .join("");

  // Wire row checkboxes
  $$(".row-check").forEach((cb) => {
    cb.addEventListener("change", () => {
      if (cb.checked) state.selected.add(cb.dataset.id);
      else state.selected.delete(cb.dataset.id);
      updateBulkBar();
      renderTable(); // refresh selected class
    });
  });

  $$(".btn-edit").forEach((btn) =>
    btn.addEventListener("click", () => openEditModal(btn.dataset.id))
  );
  $$(".btn-delete").forEach((btn) =>
    btn.addEventListener("click", () => deleteEmployee(btn.dataset.id))
  );
}

function renderPagination(data) {
  $("#pageInfo").textContent = `Page ${data.page || 1} of ${data.total_pages || 1} · ${data.total || 0} total`;
  $("#btnPrev").disabled = (data.page || 1) <= 1;
  $("#btnNext").disabled = (data.page || 1) >= (data.total_pages || 1);
}

function updateBulkBar() {
  const bar = $("#bulkBar");
  const n = state.selected.size;
  if (n > 0) {
    bar.hidden = false;
    $("#selectedCount").textContent = `${n} selected`;
  } else {
    bar.hidden = true;
  }
  $("#selectAll").checked =
    state.employees.length > 0 &&
    state.employees.every((e) => state.selected.has(e.id));
}

function updateDeptFilterOptions() {
  const select = $("#deptFilter");
  const current = select.value;
  const depts = new Map();
  state.employees.forEach((e) => {
    if (e.department_id) depts.set(e.department_id, e.department_name || e.department_id);
  });
  // Keep existing options + new ones
  const existing = new Set([...select.options].map((o) => o.value).filter(Boolean));
  depts.forEach((name, id) => {
    if (!existing.has(id)) {
      const opt = document.createElement("option");
      opt.value = id;
      opt.textContent = name;
      select.appendChild(opt);
    }
  });
  select.value = current;
}

function escapeHtml(str) {
  if (str == null) return "";
  return String(str)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

// ---------- Leave summary ----------
async function loadLeaveCount() {
  try {
    const res = await api("/leave-summary/");
    const data = res.data || res;
    $("#leaveCount").textContent = data.total_on_leave ?? 0;
    $("#metricLeave").textContent = data.total_on_leave ?? 0;
  } catch {
    $("#leaveCount").textContent = "—";
  }
}

async function loadGlobalMetrics() {
  // Approximate from current list + leave summary
  try {
    const res = await api("/employees/?page=1&page_size=1");
    const data = res.data || res;
    $("#metricTotal").textContent = data.total ?? 0;
    const leave = parseInt($("#leaveCount").textContent, 10) || 0;
    $("#metricActive").textContent = Math.max(0, (data.total || 0) - leave);
  } catch {
    /* ignore */
  }
}

// ---------- CRUD ----------
function openAddModal() {
  state.editingId = null;
  $("#modalTitle").textContent = "Add Employee";
  $("#employeeForm").reset();
  $("#formId").value = "";
  $("#leaveField").hidden = true;
  $("#formError").hidden = true;
  $("#formHireDate").value = new Date().toISOString().slice(0, 10);
  $("#formStatus").value = "active";
  $("#employeeModal").hidden = false;
}

function openEditModal(id) {
  const emp = state.employees.find((e) => e.id === id);
  if (!emp) {
    toast("Employee not found in current page", "error");
    return;
  }
  state.editingId = id;
  $("#modalTitle").textContent = "Edit Employee";
  $("#formId").value = id;
  $("#formFirstName").value = emp.first_name;
  $("#formLastName").value = emp.last_name;
  $("#formEmail").value = emp.email;
  $("#formDeptId").value = emp.department_id;
  $("#formDeptName").value = emp.department_name;
  $("#formHireDate").value = emp.hire_date;
  $("#formStatus").value = emp.status;
  $("#formOnLeave").checked = !!emp.is_on_leave;
  $("#leaveField").hidden = false;
  $("#formError").hidden = true;
  $("#employeeModal").hidden = false;
}

function closeModal() {
  $("#employeeModal").hidden = true;
  state.editingId = null;
}

async function saveEmployee(e) {
  e.preventDefault();
  const errEl = $("#formError");
  errEl.hidden = true;

  const payload = {
    first_name: $("#formFirstName").value.trim(),
    last_name: $("#formLastName").value.trim(),
    email: $("#formEmail").value.trim(),
    department_id: $("#formDeptId").value.trim(),
    department_name: $("#formDeptName").value.trim(),
    hire_date: $("#formHireDate").value,
    status: $("#formStatus").value,
  };

  if (state.editingId) {
    payload.is_on_leave = $("#formOnLeave").checked;
  }

  const btn = $("#btnSaveEmployee");
  btn.disabled = true;
  btn.textContent = "Saving…";

  try {
    if (state.editingId) {
      await api(`/employees/${state.editingId}/`, {
        method: "PATCH",
        body: JSON.stringify(payload),
      });
      toast("Employee updated", "success");
    } else {
      await api("/employees/", {
        method: "POST",
        body: JSON.stringify(payload),
      });
      toast("Employee created", "success");
    }
    closeModal();
    await loadEmployees();
    await loadLeaveCount();
  } catch (err) {
    errEl.textContent = err.message;
    errEl.hidden = false;
  } finally {
    btn.disabled = false;
    btn.textContent = "Save";
  }
}

async function deleteEmployee(id) {
  const emp = state.employees.find((e) => e.id === id);
  const name = emp ? emp.full_name || emp.first_name : id;
  if (!confirm(`Soft-delete employee “${name}”?`)) return;

  try {
    await api(`/employees/${id}/`, { method: "DELETE" });
    state.selected.delete(id);
    toast("Employee deleted", "success");
    await loadEmployees();
    await loadLeaveCount();
    updateBulkBar();
  } catch (err) {
    toast(err.message, "error");
  }
}

// ---------- Bulk actions ----------
function openTransferModal() {
  if (!state.selected.size) return;
  $("#transferDeptId").value = "";
  $("#transferDeptName").value = "";
  $("#transferError").hidden = true;
  $("#transferModal").hidden = false;
}

function closeTransferModal() {
  $("#transferModal").hidden = true;
}

async function confirmTransfer() {
  const deptId = $("#transferDeptId").value.trim();
  const deptName = $("#transferDeptName").value.trim();
  const errEl = $("#transferError");

  if (!deptId || !deptName) {
    errEl.textContent = "Department ID and name are required";
    errEl.hidden = false;
    return;
  }

  try {
    await api("/employees/bulk-transfer/", {
      method: "POST",
      body: JSON.stringify({
        employee_ids: [...state.selected],
        new_department_id: deptId,
        new_department_name: deptName,
      }),
    });
    toast(`Transferred ${state.selected.size} employee(s)`, "success");
    state.selected.clear();
    closeTransferModal();
    updateBulkBar();
    await loadEmployees();
  } catch (err) {
    errEl.textContent = err.message;
    errEl.hidden = false;
  }
}

async function bulkDeactivate() {
  if (!state.selected.size) return;
  if (!confirm(`Deactivate ${state.selected.size} employee(s)?`)) return;

  try {
    await api("/employees/bulk-deactivate/", {
      method: "POST",
      body: JSON.stringify({ employee_ids: [...state.selected] }),
    });
    toast(`Deactivated ${state.selected.size} employee(s)`, "success");
    state.selected.clear();
    updateBulkBar();
    await loadEmployees();
  } catch (err) {
    toast(err.message, "error");
  }
}

// ---------- Metrics view ----------
async function loadDeptMetrics() {
  const deptId = $("#metricDeptId").value.trim();
  const deptName = $("#metricDeptName").value.trim();
  const box = $("#deptMetricsResult");

  if (!deptId) {
    toast("Enter a department UUID", "error");
    return;
  }

  const params = new URLSearchParams({ department_id: deptId });
  if (deptName) params.set("department_name", deptName);

  try {
    const res = await api(`/department-metrics/?${params}`);
    const d = res.data || res;
    box.hidden = false;
    box.innerHTML = `
      <div><strong>Department:</strong> ${escapeHtml(d.department_name || deptId)}</div>
      <div><strong>Total employees:</strong> ${d.total_employees}</div>
      <div><strong>On leave:</strong> ${d.employees_on_leave}</div>
      <div><strong>Active:</strong> ${d.active_employees}</div>
    `;
  } catch (err) {
    box.hidden = false;
    box.textContent = "Error: " + err.message;
  }
}

// ---------- Navigation ----------
function switchView(name) {
  $$(".view").forEach((v) => v.classList.remove("active"));
  $$(".nav-item").forEach((n) => n.classList.remove("active"));
  $(`#view-${name}`).classList.add("active");
  $$(`[data-view="${name}"]`).forEach((n) => n.classList.add("active"));

  if (name === "directory") {
    $("#pageTitle").textContent = "Employee Directory";
    $("#pageSubtitle").textContent = "Browse, search and manage your team";
  } else {
    $("#pageTitle").textContent = "HR Metrics";
    $("#pageSubtitle").textContent = "Leave counts and department insights";
    loadGlobalMetrics();
  }
}

// ---------- Events ----------
function bindEvents() {
  // Nav
  $$(".nav-item").forEach((btn) =>
    btn.addEventListener("click", () => switchView(btn.dataset.view))
  );

  // Toolbar
  let searchTimer;
  $("#searchInput").addEventListener("input", (e) => {
    clearTimeout(searchTimer);
    searchTimer = setTimeout(() => {
      state.search = e.target.value.trim();
      state.page = 1;
      loadEmployees();
    }, 300);
  });

  $("#deptFilter").addEventListener("change", (e) => {
    state.departmentId = e.target.value;
    state.page = 1;
    loadEmployees();
  });

  $("#btnRefresh").addEventListener("click", () => {
    loadEmployees();
    loadLeaveCount();
    toast("Refreshed", "info");
  });

  $("#btnAddEmployee").addEventListener("click", openAddModal);

  $("#btnPrev").addEventListener("click", () => {
    if (state.page > 1) {
      state.page--;
      loadEmployees();
    }
  });
  $("#btnNext").addEventListener("click", () => {
    if (state.page < state.totalPages) {
      state.page++;
      loadEmployees();
    }
  });

  $("#selectAll").addEventListener("change", (e) => {
    if (e.target.checked) {
      state.employees.forEach((emp) => state.selected.add(emp.id));
    } else {
      state.employees.forEach((emp) => state.selected.delete(emp.id));
    }
    updateBulkBar();
    renderTable();
  });

  $("#btnClearSelection").addEventListener("click", () => {
    state.selected.clear();
    updateBulkBar();
    renderTable();
  });

  $("#btnBulkTransfer").addEventListener("click", openTransferModal);
  $("#btnBulkDeactivate").addEventListener("click", bulkDeactivate);

  // Modal
  $("#btnCloseModal").addEventListener("click", closeModal);
  $("#btnCancelForm").addEventListener("click", closeModal);
  $("#employeeForm").addEventListener("submit", saveEmployee);
  $("#employeeModal").addEventListener("click", (e) => {
    if (e.target === $("#employeeModal")) closeModal();
  });

  $("#btnCloseTransfer").addEventListener("click", closeTransferModal);
  $("#btnCancelTransfer").addEventListener("click", closeTransferModal);
  $("#btnConfirmTransfer").addEventListener("click", confirmTransfer);
  $("#transferModal").addEventListener("click", (e) => {
    if (e.target === $("#transferModal")) closeTransferModal();
  });

  $("#btnLoadMetrics").addEventListener("click", loadDeptMetrics);
}

// ---------- Init ----------
document.addEventListener("DOMContentLoaded", () => {
  bindEvents();
  loadEmployees();
  loadLeaveCount();
});
