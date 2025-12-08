// Dashboard JavaScript
let salaryTrendChart = null;
let salaryHistoryChart = null;
let attendanceChart = null;

// Initialize dashboard
document.addEventListener('DOMContentLoaded', async () => {
    await initializeDashboard();
});

async function initializeDashboard() {
    try {
        // Load current year into filter
        const currentYear = new Date().getFullYear();
        const yearFilter = document.getElementById('year-filter');
        for (let year = currentYear; year >= currentYear - 5; year--) {
            const option = document.createElement('option');
            option.value = year;
            option.textContent = year;
            if (year === currentYear) option.selected = true;
            yearFilter.appendChild(option);
        }

        // Load dashboard data
        await loadDashboardData(currentYear);

        // Add event listener for year filter
        yearFilter.addEventListener('change', async (e) => {
            const selectedYear = e.target.value || currentYear;
            await loadDashboardData(selectedYear);
        });
    } catch (error) {
        console.error('Error initializing dashboard:', error);
        showAlert('Lỗi khi khởi tạo dashboard', 'error');
    }
}

async function loadDashboardData(year) {
    try {
        // Load all data in parallel
        const [overviewRes, salaryStatsRes, attendanceStatsRes, deptStatsRes, employeesRes, salariesRes, attendanceRes, dividendsRes, financialReportRes] = await Promise.all([
            DashboardAPI.getOverview(),
            StatisticsAPI.getSalaryStatistics(year),
            StatisticsAPI.getAttendanceStatistics(year),
            StatisticsAPI.getDepartmentStatistics().catch(() => ({ success: false })),
            EmployeesAPI.getAll({ size: 5, page: 1 }).catch(() => ({ success: false })),
            SalariesAPI.getAll({ year: year }).catch(() => ({ success: false })),
            AttendanceAPI.getAll({ year: year }).catch(() => ({ success: false })),
            DividendsAPI.getAll().catch(() => ({ success: false })),
            ReportsAPI.getFinancialReport(year).catch(() => ({ success: false }))
        ]);

        // Update KPIs
        if (overviewRes.success) {
            updateKPIs(overviewRes.data, salaryStatsRes);
        }

        // Update charts
        if (salaryStatsRes.success) {
            updateSalaryCharts(salaryStatsRes.data);
        }

        // Update attendance chart
        if (attendanceStatsRes.success) {
            updateAttendanceChart(attendanceStatsRes.data);
        }

        // Update department stats table
        if (deptStatsRes.success) {
            updateDepartmentStatsTable(deptStatsRes.data);
        } else {
            // Fallback: get departments and count employees
            await updateDepartmentStatsFallback();
        }

        // Update recent employees
        if (employeesRes.success && employeesRes.data.employees) {
            updateRecentEmployees(employeesRes.data.employees);
        }

        // Update salary summary table
        if (salaryStatsRes.success) {
            updateSalarySummaryTable(salaryStatsRes.data);
        }

        // Update financial reports
        updateFinancialReports(overviewRes, dividendsRes, financialReportRes, salaryStatsRes, year);
    } catch (error) {
        console.error('Error loading dashboard data:', error);
        showAlert('Lỗi khi tải dữ liệu dashboard', 'error');
    }
}

function updateKPIs(overviewData, salaryStats) {
    // Total Employees
    const totalEmployees = overviewData?.total_employees || 0;
    const kpiTotalEmployees = document.getElementById('kpi-total-employees');
    if (kpiTotalEmployees) {
        kpiTotalEmployees.textContent = totalEmployees.toLocaleString('vi-VN');
    }

    // Average Net Salary
    let avgNetSalary = 0;
    if (salaryStats && salaryStats.success && salaryStats.data) {
        const monthlyData = salaryStats.data.monthly_data || [];
        if (monthlyData.length > 0) {
            const totalNet = monthlyData.reduce((sum, month) => sum + (month.total_net_salary || 0), 0);
            const totalEmployees = monthlyData.reduce((sum, month) => sum + (month.employee_count || 0), 0);
            avgNetSalary = totalEmployees > 0 ? totalNet / totalEmployees : 0;
        }
    }
    const kpiAvgNetSalary = document.getElementById('kpi-avg-net-salary');
    if (kpiAvgNetSalary) {
        kpiAvgNetSalary.textContent = formatCurrency(avgNetSalary);
    }

    // Total Gross Salary
    let totalGrossSalary = 0;
    if (salaryStats && salaryStats.success && salaryStats.data) {
        const monthlyData = salaryStats.data.monthly_data || [];
        if (monthlyData.length > 0) {
            totalGrossSalary = monthlyData.reduce((sum, month) => sum + (month.total_gross_salary || 0), 0);
        } else if (salaryStats.data.total_gross_salary !== undefined) {
            // Fallback: sử dụng total_gross_salary từ response nếu có
            totalGrossSalary = salaryStats.data.total_gross_salary || 0;
        }
    }
    const kpiTotalGrossSalary = document.getElementById('kpi-total-gross-salary');
    if (kpiTotalGrossSalary) {
        kpiTotalGrossSalary.textContent = formatCurrency(totalGrossSalary);
    }

    // Total Monthly Bills (Total salary + other costs)
    const totalMonthlyBills = totalGrossSalary;
    const kpiTotalMonthlyBills = document.getElementById('kpi-total-monthly-bills');
    if (kpiTotalMonthlyBills) {
        kpiTotalMonthlyBills.textContent = formatCurrency(totalMonthlyBills);
    }
}

function updateSalaryCharts(salaryData) {
    const monthlyData = salaryData.monthly_data || [];
    
    // Prepare data for charts
    const labels = monthlyData.map(m => {
        const [year, month] = m.month ? m.month.split('-') : ['', ''];
        return month ? `${month}/${year}` : '';
    });
    const grossSalaryData = monthlyData.map(m => m.total_gross_salary || 0);
    const netSalaryData = monthlyData.map(m => m.total_net_salary || 0);

    // Update Salary Trend Chart (Line Chart)
    updateLineChart('salary-trend-chart', labels, grossSalaryData, netSalaryData);

    // Update Salary History Chart (Bar Chart)
    updateBarChart('salary-history-chart', labels, grossSalaryData, netSalaryData);
}

function updateLineChart(canvasId, labels, grossData, netData) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return;

    if (salaryTrendChart) {
        salaryTrendChart.destroy();
    }

    salaryTrendChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [
                {
                    label: 'Gross Salary',
                    data: grossData,
                    borderColor: 'rgb(37, 99, 235)',
                    backgroundColor: 'rgba(37, 99, 235, 0.1)',
                    tension: 0.4,
                    fill: true
                },
                {
                    label: 'Net Salary',
                    data: netData,
                    borderColor: 'rgb(16, 185, 129)',
                    backgroundColor: 'rgba(16, 185, 129, 0.1)',
                    tension: 0.4,
                    fill: true
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: true,
                    position: 'top'
                },
                tooltip: {
                    mode: 'index',
                    intersect: false,
                    callbacks: {
                        label: function(context) {
                            return context.dataset.label + ': ' + formatCurrency(context.parsed.y);
                        }
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        callback: function(value) {
                            return formatCurrency(value);
                        }
                    }
                }
            }
        }
    });
}

function updateBarChart(canvasId, labels, grossData, netData) {
    const ctx = document.getElementById(canvasId);
    if (!ctx) return;

    if (salaryHistoryChart) {
        salaryHistoryChart.destroy();
    }

    salaryHistoryChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [
                {
                    label: 'Gross Salary',
                    data: grossData,
                    backgroundColor: 'rgba(37, 99, 235, 0.8)',
                    borderColor: 'rgb(37, 99, 235)',
                    borderWidth: 1
                },
                {
                    label: 'Net Salary',
                    data: netData,
                    backgroundColor: 'rgba(16, 185, 129, 0.8)',
                    borderColor: 'rgb(16, 185, 129)',
                    borderWidth: 1
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: true,
                    position: 'top'
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return context.dataset.label + ': ' + formatCurrency(context.parsed.y);
                        }
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        callback: function(value) {
                            return formatCurrency(value);
                        }
                    }
                }
            }
        }
    });
}

async function updateDepartmentStatsFallback() {
    try {
        const [departmentsRes, employeesRes] = await Promise.all([
            DepartmentsAPI.getAll(),
            EmployeesAPI.getAll({ size: 1000 })
        ]);

        if (departmentsRes.success && employeesRes.success) {
            const departments = departmentsRes.data || [];
            const employees = employeesRes.data.employees || [];
            
            // Count employees by department
            const deptCounts = {};
            employees.forEach(emp => {
                const deptId = emp.department_id;
                if (deptId) {
                    deptCounts[deptId] = (deptCounts[deptId] || 0) + 1;
                }
            });

            // Build table data
            const tableData = departments.map(dept => ({
                name: dept.DepartmentName || dept.department_name || 'N/A',
                count: deptCounts[dept.DepartmentID || dept.department_id] || 0,
                date: new Date().toLocaleDateString('vi-VN')
            }));

            updateDepartmentStatsTable(tableData);
        }
    } catch (error) {
        console.error('Error updating department stats fallback:', error);
    }
}

function updateDepartmentStatsTable(data) {
    const tbody = document.getElementById('department-stats-table');
    if (!tbody) return;

    if (!data || data.length === 0) {
        tbody.innerHTML = '<tr><td colspan="3" class="empty-state">Không có dữ liệu</td></tr>';
        return;
    }

    tbody.innerHTML = data.map(dept => `
        <tr>
            <td>${dept.DepartmentName || dept.department_name || dept.name || 'N/A'}</td>
            <td><strong>${dept.EmployeeCount || dept.employee_count || dept.count || 0}</strong></td>
            <td>${dept.Date || dept.date || new Date().toLocaleDateString('vi-VN')}</td>
        </tr>
    `).join('');
}

function updateRecentEmployees(employees) {
    const container = document.getElementById('recent-employees');
    if (!container) return;

    if (!employees || employees.length === 0) {
        container.innerHTML = '<div class="empty-state">Không có nhân viên gần đây</div>';
        return;
    }

    container.innerHTML = employees.slice(0, 5).map(emp => `
        <div class="recent-employee-item">
            <div class="employee-avatar">${(emp.FullName || emp.full_name || 'N/A').charAt(0).toUpperCase()}</div>
            <div class="employee-info">
                <div class="employee-name">${emp.FullName || emp.full_name || 'N/A'}</div>
                <div class="employee-department">${emp.DepartmentName || emp.department_name || 'N/A'}</div>
            </div>
        </div>
    `).join('');
}

function updateAttendanceChart(attendanceData) {
    const ctx = document.getElementById('attendance-chart');
    if (!ctx) return;

    // Destroy existing chart if any
    if (attendanceChart) {
        attendanceChart.destroy();
        attendanceChart = null;
    }

    const monthlyData = attendanceData?.monthly_data || [];
    
    if (monthlyData.length === 0) {
        // Show empty state message
        const chartContainer = ctx.parentElement;
        if (chartContainer) {
            chartContainer.innerHTML = `
                <div style="padding: 2rem; text-align: center; color: var(--text-secondary);">
                    <p>Không có dữ liệu chấm công cho năm được chọn</p>
                </div>
            `;
        }
        return;
    }

    const labels = monthlyData.map(m => {
        const [year, month] = m.month ? m.month.split('-') : ['', ''];
        return month ? `${month}/${year}` : '';
    });
    const workDaysData = monthlyData.map(m => m.total_work_days || 0);
    const absentDaysData = monthlyData.map(m => m.total_absent_days || 0);

    attendanceChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [
                {
                    label: 'Work Days',
                    data: workDaysData,
                    backgroundColor: 'rgba(16, 185, 129, 0.8)',
                    borderColor: 'rgb(16, 185, 129)',
                    borderWidth: 1
                },
                {
                    label: 'Absent Days',
                    data: absentDaysData,
                    backgroundColor: 'rgba(239, 68, 68, 0.8)',
                    borderColor: 'rgb(239, 68, 68)',
                    borderWidth: 1
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: true,
                    position: 'top'
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return context.dataset.label + ': ' + context.parsed.y + ' days';
                        }
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        stepSize: 1
                    }
                }
            }
        }
    });
}

function updateSalarySummaryTable(salaryData) {
    const tbody = document.getElementById('salary-summary-table');
    if (!tbody) return;

    const monthlyData = salaryData.monthly_data || [];
    
    if (monthlyData.length === 0) {
        tbody.innerHTML = '<tr><td colspan="4" class="empty-state">Không có dữ liệu</td></tr>';
        return;
    }

    tbody.innerHTML = monthlyData.map(month => {
        const [year, monthNum] = month.month ? month.month.split('-') : ['', ''];
        const monthLabel = monthNum ? `${monthNum}/${year}` : month.month || 'N/A';
        return `
            <tr>
                <td><strong>${monthLabel}</strong></td>
                <td>${month.employee_count || 0}</td>
                <td>${formatCurrency(month.total_gross_salary || 0)}</td>
                <td>${formatCurrency(month.total_net_salary || 0)}</td>
            </tr>
        `;
    }).join('');
}

function updateFinancialReports(overviewRes, dividendsRes, financialReportRes, salaryStatsRes, year) {
    // Total Dividends - ưu tiên sử dụng từ financialReportRes
    let totalDividends = 0;
    const selectedYear = year || new Date().getFullYear();
    
    if (financialReportRes && financialReportRes.success && financialReportRes.data) {
        // Sử dụng total_dividends từ financial report (đã được tính theo năm)
        totalDividends = financialReportRes.data.total_dividends || 0;
    } else if (dividendsRes && dividendsRes.success && dividendsRes.data) {
        // Fallback: tính từ danh sách dividends
        let dividends = dividendsRes.data;
        // Xử lý trường hợp response bị wrap thêm một lần
        if (dividends && dividends.data && Array.isArray(dividends.data)) {
            dividends = dividends.data;
        } else if (dividends && !Array.isArray(dividends) && Array.isArray(dividends.data)) {
            dividends = dividends.data;
        }
        
        const dividendsArray = Array.isArray(dividends) ? dividends : [];
        totalDividends = dividendsArray
            .filter(div => {
                const divDate = new Date(div.DividendDate || div.dividend_date || '');
                return divDate.getFullYear() === selectedYear;
            })
            .reduce((sum, div) => {
                // Sử dụng DividendAmount (tên đúng từ database)
                const amount = div.DividendAmount || div.dividend_amount || div.Amount || div.amount || 0;
                return sum + (parseFloat(amount) || 0);
            }, 0);
    }
    
    const totalDividendsElement = document.getElementById('total-dividends');
    if (totalDividendsElement) {
        totalDividendsElement.textContent = formatCurrency(totalDividends);
    }

    // Total Salary Cost
    let totalSalaryCost = 0;
    if (salaryStatsRes && salaryStatsRes.success && salaryStatsRes.data) {
        const monthlyData = salaryStatsRes.data.monthly_data || [];
        if (monthlyData.length > 0) {
            totalSalaryCost = monthlyData.reduce((sum, month) => sum + (month.total_gross_salary || 0), 0);
        } else if (salaryStatsRes.data.total_gross_salary !== undefined) {
            // Fallback: sử dụng total_gross_salary từ response nếu có
            totalSalaryCost = salaryStatsRes.data.total_gross_salary || 0;
        }
    }
    const totalSalaryCostElement = document.getElementById('total-salary-cost');
    if (totalSalaryCostElement) {
        totalSalaryCostElement.textContent = formatCurrency(totalSalaryCost);
    }

    // Total Financial (Salary + Dividends)
    const totalFinancial = totalSalaryCost + totalDividends;
    const totalFinancialElement = document.getElementById('total-financial');
    if (totalFinancialElement) {
        totalFinancialElement.textContent = formatCurrency(totalFinancial);
    }
}
