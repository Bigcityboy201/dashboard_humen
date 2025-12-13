// Dashboard JavaScript
let salaryTrendChart = null;
let salaryHistoryChart = null;
let attendanceChart = null;

// Check if user is HR_MANAGER (not ADMIN)
function isHRManager() {
    return AuthManager.hasRole('HR_MANAGER') && !AuthManager.hasRole('ADMIN');
}

// Check if user is PAYROLL_MANAGER (not ADMIN)
function isPayrollManager() {
    return AuthManager.hasRole('PAYROLL_MANAGER') && !AuthManager.hasRole('ADMIN');
}

// Initialize dashboard
document.addEventListener('DOMContentLoaded', async () => {
    await initializeDashboard();
});

async function initializeDashboard() {
    try {
        // Check authentication
        if (!AuthManager.isAuthenticated()) {
            window.location.href = '/login';
            return;
        }

        // Hide/show sections based on role
        setupRoleBasedVisibility();

        // Load current year into filter
        const currentYear = new Date().getFullYear();
        const yearFilter = document.getElementById('year-filter');
        if (yearFilter) {
            for (let year = currentYear; year >= currentYear - 5; year--) {
                const option = document.createElement('option');
                option.value = year;
                option.textContent = year;
                if (year === currentYear) option.selected = true;
                yearFilter.appendChild(option);
            }

            // Add event listener for year filter
            yearFilter.addEventListener('change', async (e) => {
                const selectedYear = e.target.value || currentYear;
                await loadDashboardData(selectedYear);
            });
        }

        // Load dashboard data
        await loadDashboardData(currentYear);
    } catch (error) {
        console.error('Error initializing dashboard:', error);
        showAlert('Lỗi khi khởi tạo dashboard', 'error');
    }
}

// Setup visibility based on user role
function setupRoleBasedVisibility() {
    const isHR = isHRManager();
    const isPayroll = isPayrollManager();
    
    if (isHR) {
        // HR_MANAGER: Chỉ hiển thị HR-related, ẩn tất cả Payroll-related
        // ========== SHOW HR-specific KPIs ==========
        const hrKPICards = [
            'kpi-card-departments',
            'kpi-card-positions',
            'kpi-card-workdays'
        ];
        hrKPICards.forEach(id => {
            const element = document.getElementById(id);
            if (element) element.style.display = 'flex';
        });

        // ========== HIDE Payroll-related KPIs ==========
        const salaryKPICards = [
            'kpi-card-avg-salary',
            'kpi-card-gross-salary',
            'kpi-card-monthly-bills'
        ];
        salaryKPICards.forEach(id => {
            const element = document.getElementById(id);
            if (element) element.style.display = 'none';
        });

        // ========== HIDE Payroll-related Sections ==========
        // Hide salary charts row
        const salaryChartsRow = document.getElementById('salary-charts-row');
        if (salaryChartsRow) salaryChartsRow.style.display = 'none';
        
        // Hide salary trend chart
        const salaryTrendChartCard = document.getElementById('salary-trend-chart-card');
        if (salaryTrendChartCard) salaryTrendChartCard.style.display = 'none';
        
        // Hide salary history chart
        const salaryHistoryChartCard = document.getElementById('salary-history-chart-card');
        if (salaryHistoryChartCard) salaryHistoryChartCard.style.display = 'none';

        // Hide salary summary table
        const salarySummaryCard = document.getElementById('salary-summary-card');
        if (salarySummaryCard) salarySummaryCard.style.display = 'none';

        // Hide financial reports section
        const financialReportsCard = document.getElementById('financial-reports-card');
        if (financialReportsCard) financialReportsCard.style.display = 'none';

        // ========== SHOW HR-specific Sections ==========
        // Show positions card
        const positionsCard = document.getElementById('positions-card');
        if (positionsCard) positionsCard.style.display = 'block';

        // Show HR sections row (departments and employees)
        const hrSectionsRow = document.getElementById('hr-sections-row');
        if (hrSectionsRow) hrSectionsRow.style.display = 'flex';

        // Show department stats
        const departmentStatsCard = document.getElementById('department-stats-card');
        if (departmentStatsCard) departmentStatsCard.style.display = 'block';

        // Show employees card
        const employeesCard = document.getElementById('employees-card');
        if (employeesCard) employeesCard.style.display = 'block';

        // Show attendance chart (HR can see attendance)
        const attendanceChartCard = document.getElementById('attendance-chart-card');
        if (attendanceChartCard) attendanceChartCard.style.display = 'block';
        
        // Show trends chart (HR can see trends)
        const trendsChartCard = document.getElementById('trends-chart-card');
        if (trendsChartCard) trendsChartCard.style.display = 'block';

        // Update employees section title
        const employeesTitle = document.getElementById('employees-section-title');
        if (employeesTitle) employeesTitle.textContent = 'Nhân viên mới';
    } else if (isPayroll) {
        // PAYROLL_MANAGER: Chỉ hiển thị Payroll-related, ẩn tất cả HR-related
        // ========== HIDE HR-specific KPIs ==========
        const hrKPICards = [
            'kpi-card-departments',
            'kpi-card-positions',
            'kpi-card-workdays'
        ];
        hrKPICards.forEach(id => {
            const element = document.getElementById(id);
            if (element) element.style.display = 'none';
        });

        // ========== SHOW Payroll-related KPIs ==========
        const salaryKPICards = [
            'kpi-card-avg-salary',
            'kpi-card-gross-salary',
            'kpi-card-monthly-bills'
        ];
        salaryKPICards.forEach(id => {
            const element = document.getElementById(id);
            if (element) element.style.display = 'flex';
        });

        // ========== SHOW Payroll-related Sections ==========
        // Show salary charts row
        const salaryChartsRow = document.getElementById('salary-charts-row');
        if (salaryChartsRow) salaryChartsRow.style.display = 'flex';
        
        // Show salary trend chart
        const salaryTrendChartCard = document.getElementById('salary-trend-chart-card');
        if (salaryTrendChartCard) salaryTrendChartCard.style.display = 'block';
        
        // Show salary history chart
        const salaryHistoryChartCard = document.getElementById('salary-history-chart-card');
        if (salaryHistoryChartCard) salaryHistoryChartCard.style.display = 'block';

        // Show salary summary table
        const salarySummaryCard = document.getElementById('salary-summary-card');
        if (salarySummaryCard) salarySummaryCard.style.display = 'block';

        // Show financial reports section
        const financialReportsCard = document.getElementById('financial-reports-card');
        if (financialReportsCard) financialReportsCard.style.display = 'block';

        // ========== HIDE HR-specific Sections ==========
        // Hide positions card
        const positionsCard = document.getElementById('positions-card');
        if (positionsCard) positionsCard.style.display = 'none';

        // Hide HR sections row (departments and employees)
        const hrSectionsRow = document.getElementById('hr-sections-row');
        if (hrSectionsRow) hrSectionsRow.style.display = 'none';

        // Hide department stats
        const departmentStatsCard = document.getElementById('department-stats-card');
        if (departmentStatsCard) departmentStatsCard.style.display = 'none';

        // Hide employees card
        const employeesCard = document.getElementById('employees-card');
        if (employeesCard) employeesCard.style.display = 'none';

        // Hide attendance chart
        const attendanceChartCard = document.getElementById('attendance-chart-card');
        if (attendanceChartCard) attendanceChartCard.style.display = 'none';
        
        // Hide trends chart
        const trendsChartCard = document.getElementById('trends-chart-card');
        if (trendsChartCard) trendsChartCard.style.display = 'none';
    } else {
        // ADMIN: Show everything
        // Hide HR-specific KPIs in KPI cards (admin can see them but in separate sections)
        const hrKPICards = [
            'kpi-card-departments',
            'kpi-card-positions',
            'kpi-card-workdays'
        ];
        hrKPICards.forEach(id => {
            const element = document.getElementById(id);
            if (element) element.style.display = 'none';
        });

        // Show salary-related KPIs
        const salaryKPICards = [
            'kpi-card-avg-salary',
            'kpi-card-gross-salary',
            'kpi-card-monthly-bills'
        ];
        salaryKPICards.forEach(id => {
            const element = document.getElementById(id);
            if (element) element.style.display = 'flex';
        });

        // Show all sections for ADMIN
        const salaryChartsRow = document.getElementById('salary-charts-row');
        if (salaryChartsRow) salaryChartsRow.style.display = 'flex';
        
        const hrSectionsRow = document.getElementById('hr-sections-row');
        if (hrSectionsRow) hrSectionsRow.style.display = 'flex';
        
        // Show trends chart for ADMIN
        const trendsChartCard = document.getElementById('trends-chart-card');
        if (trendsChartCard) trendsChartCard.style.display = 'block';

        // Hide positions card (admin sees all in separate sections)
        const positionsCard = document.getElementById('positions-card');
        if (positionsCard) positionsCard.style.display = 'none';
    }
}

async function loadDashboardData(year) {
    try {
        const isHR = isHRManager();
        const isPayroll = isPayrollManager();
        
        // Load data based on role
        let overviewRes, salaryStatsRes, attendanceStatsRes, deptStatsRes, employeesRes;
        let positionsRes, employeeStatsRes, dividendsRes, financialReportRes;
        let comparisonRes, topEmployeesRes, topDepartmentsRes, trendsRes;
        
        if (isHR) {
            // HR_MANAGER: Load only HR-related data
            [overviewRes, attendanceStatsRes, deptStatsRes, employeesRes, positionsRes, employeeStatsRes,
             comparisonRes, topEmployeesRes, topDepartmentsRes, trendsRes] = await Promise.all([
                DashboardAPI.getOverview().catch(() => ({ success: false })),
                StatisticsAPI.getAttendanceStatistics(year).catch(() => ({ success: false })),
                StatisticsAPI.getDepartmentStatistics().catch(() => ({ success: false })),
                EmployeesAPI.getAll({ size: 10, page: 1 }).catch(() => ({ success: false })),
                PositionsAPI.getAll().catch(() => ({ success: false })),
                StatisticsAPI.getEmployeeStatistics().catch(() => ({ success: false })),
                DashboardAPI.getComparison().catch(() => ({ success: false })),
                DashboardAPI.getTopEmployees(5).catch(() => ({ success: false })),
                DashboardAPI.getTopDepartments(5).catch(() => ({ success: false })),
                DashboardAPI.getTrends(6).catch(() => ({ success: false }))
            ]);
            
            // Initialize salaryStatsRes as null for HR
            salaryStatsRes = null;
        } else if (isPayroll) {
            // PAYROLL_MANAGER: Load only payroll-related data
            [overviewRes, salaryStatsRes, dividendsRes, financialReportRes,
             comparisonRes, trendsRes] = await Promise.all([
                DashboardAPI.getOverview().catch(() => ({ success: false })),
                StatisticsAPI.getSalaryStatistics(year).catch(() => ({ success: false })),
                DividendsAPI.getAll().catch(() => ({ success: false })),
                ReportsAPI.getFinancialReport(year).catch(() => ({ success: false })),
                DashboardAPI.getComparison().catch(() => ({ success: false })),
                DashboardAPI.getTrends(6).catch(() => ({ success: false }))
            ]);
            
            // Update salary-related data
            if (salaryStatsRes.success) {
                updateSalaryCharts(salaryStatsRes.data);
            }
            
            if (salaryStatsRes.success) {
                updateSalarySummaryTable(salaryStatsRes.data);
            }
            
            updateFinancialReports(overviewRes, dividendsRes, financialReportRes, salaryStatsRes, year);
            
            // Initialize other as null for Payroll
            attendanceStatsRes = null;
            deptStatsRes = null;
            employeesRes = null;
            positionsRes = null;
            employeeStatsRes = null;
        } else {
            // ADMIN: Load all data
            const [overviewResAll, salaryStatsResAll, attendanceStatsResAll, deptStatsResAll, employeesResAll, salariesRes, attendanceRes, dividendsResAll, financialReportResAll,
                   comparisonResAll, topEmployeesResAll, topDepartmentsResAll, trendsResAll] = await Promise.all([
                DashboardAPI.getOverview(),
                StatisticsAPI.getSalaryStatistics(year),
                StatisticsAPI.getAttendanceStatistics(year),
                StatisticsAPI.getDepartmentStatistics().catch(() => ({ success: false })),
                EmployeesAPI.getAll({ size: 5, page: 1 }).catch(() => ({ success: false })),
                SalariesAPI.getAll({ year: year }).catch(() => ({ success: false })),
                AttendanceAPI.getAll({ year: year }).catch(() => ({ success: false })),
                DividendsAPI.getAll().catch(() => ({ success: false })),
                ReportsAPI.getFinancialReport(year).catch(() => ({ success: false })),
                DashboardAPI.getComparison().catch(() => ({ success: false })),
                DashboardAPI.getTopEmployees(5).catch(() => ({ success: false })),
                DashboardAPI.getTopDepartments(5).catch(() => ({ success: false })),
                DashboardAPI.getTrends(6).catch(() => ({ success: false }))
            ]);
            
            overviewRes = overviewResAll;
            salaryStatsRes = salaryStatsResAll;
            attendanceStatsRes = attendanceStatsResAll;
            deptStatsRes = deptStatsResAll;
            employeesRes = employeesResAll;
            dividendsRes = dividendsResAll;
            financialReportRes = financialReportResAll;
            comparisonRes = comparisonResAll;
            topEmployeesRes = topEmployeesResAll;
            topDepartmentsRes = topDepartmentsResAll;
            trendsRes = trendsResAll;
            
            // Update salary-related data
            if (salaryStatsRes.success) {
                updateSalaryCharts(salaryStatsRes.data);
            }
            
            if (salaryStatsRes.success) {
                updateSalarySummaryTable(salaryStatsRes.data);
            }
            
            updateFinancialReports(overviewRes, dividendsRes, financialReportRes, salaryStatsRes, year);
        }

        // Update KPIs (HR-specific or payroll-specific or all) with comparison
        if (overviewRes.success) {
            updateKPIs(overviewRes.data, salaryStatsRes, isHR, employeeStatsRes, comparisonRes);
        }
        
        // Update top employees (use API data if available, otherwise fallback to employeesRes)
        if (topEmployeesRes && topEmployeesRes.success && topEmployeesRes.data && topEmployeesRes.data.length > 0) {
            if (isHR) {
                updateNewEmployees(topEmployeesRes.data);
            } else {
                updateRecentEmployees(topEmployeesRes.data);
            }
        } else if (!isPayroll && employeesRes && employeesRes.success && employeesRes.data.employees) {
            // Fallback to old method
            if (isHR) {
                updateNewEmployees(employeesRes.data.employees);
            } else {
                updateRecentEmployees(employeesRes.data.employees);
            }
        }
        
        // Update top departments (use API data if available)
        if (topDepartmentsRes && topDepartmentsRes.success && topDepartmentsRes.data && topDepartmentsRes.data.length > 0) {
            updateTopDepartmentsTable(topDepartmentsRes.data);
        } else if (!isPayroll && deptStatsRes && deptStatsRes.success) {
            // Fallback to old method
            updateDepartmentStatsTable(deptStatsRes.data);
        }
        
        // Update trends chart if available
        if (trendsRes && trendsRes.success && trendsRes.data) {
            console.log('Trends data:', trendsRes.data); // Debug log
            updateTrendsChart(trendsRes.data);
        } else {
            console.warn('Trends data not available:', trendsRes); // Debug log
        }

        // Update attendance chart (only for HR and ADMIN)
        if (!isPayroll && attendanceStatsRes && attendanceStatsRes.success) {
            updateAttendanceChart(attendanceStatsRes.data);
        }

        // Update department stats table (only for HR and ADMIN)
        if (!isPayroll) {
            if (deptStatsRes && deptStatsRes.success) {
                updateDepartmentStatsTable(deptStatsRes.data);
            } else {
                // Fallback: get departments and count employees (only for HR/ADMIN)
                await updateDepartmentStatsFallback();
            }
        }

        // Update positions stats (only for HR)
        if (isHR && positionsRes && positionsRes.success) {
            updatePositionsStats(positionsRes.data);
        }

        // Note: Top employees đã được xử lý ở trên
    } catch (error) {
        console.error('Error loading dashboard data:', error);
        showAlert('Lỗi khi tải dữ liệu dashboard', 'error');
    }
}

function updateKPIs(overviewData, salaryStats, isHR = false, employeeStats = null, comparisonData = null) {
    // Total Employees
    const totalEmployees = overviewData?.total_employees || employeeStats?.data?.total_employees || 0;
    const kpiTotalEmployees = document.getElementById('kpi-total-employees');
    if (kpiTotalEmployees) {
        const employeeChange = comparisonData?.data?.total_employees_change;
        let displayText = totalEmployees.toLocaleString('vi-VN');
        if (employeeChange && employeeChange.percentage !== null && employeeChange.percentage !== undefined) {
            const trendIcon = employeeChange.trend === 'up' ? '↑' : employeeChange.trend === 'down' ? '↓' : '→';
            const changeColor = employeeChange.trend === 'up' ? '#10b981' : employeeChange.trend === 'down' ? '#ef4444' : '#6b7280';
            displayText += ` <span style="color: ${changeColor}; font-size: 0.8em; margin-left: 0.5rem;">${trendIcon} ${Math.abs(employeeChange.percentage).toFixed(1)}%</span>`;
        } else if (employeeChange && employeeChange.value !== 0) {
            // Hiển thị giá trị thay đổi nếu không có percentage
            const trendIcon = employeeChange.trend === 'up' ? '↑' : employeeChange.trend === 'down' ? '↓' : '→';
            const changeColor = employeeChange.trend === 'up' ? '#10b981' : employeeChange.trend === 'down' ? '#ef4444' : '#6b7280';
            displayText += ` <span style="color: ${changeColor}; font-size: 0.8em; margin-left: 0.5rem;">${trendIcon} ${employeeChange.value > 0 ? '+' : ''}${employeeChange.value}</span>`;
        }
        kpiTotalEmployees.innerHTML = displayText;
    }

    // HR-specific KPIs
    if (isHR) {
        // Total Departments
        const totalDepartments = overviewData?.total_departments || 0;
        const kpiTotalDepartments = document.getElementById('kpi-total-departments');
        if (kpiTotalDepartments) {
            kpiTotalDepartments.textContent = totalDepartments.toLocaleString('vi-VN');
        }

        // Total Positions
        const totalPositions = overviewData?.total_positions || 0;
        const kpiTotalPositions = document.getElementById('kpi-total-positions');
        if (kpiTotalPositions) {
            kpiTotalPositions.textContent = totalPositions.toLocaleString('vi-VN');
        }

        // Total Work Days (Current Month) with comparison
        const totalWorkdays = overviewData?.total_workdays_current_month || 0;
        const kpiTotalWorkdays = document.getElementById('kpi-total-workdays');
        if (kpiTotalWorkdays) {
            const workdaysChange = comparisonData?.data?.total_workdays_change;
            let displayText = totalWorkdays.toLocaleString('vi-VN');
            if (workdaysChange && workdaysChange.percentage !== null && workdaysChange.percentage !== undefined) {
                const trendIcon = workdaysChange.trend === 'up' ? '↑' : workdaysChange.trend === 'down' ? '↓' : '→';
                const changeColor = workdaysChange.trend === 'up' ? '#10b981' : workdaysChange.trend === 'down' ? '#ef4444' : '#6b7280';
                displayText += ` <span style="color: ${changeColor}; font-size: 0.8em; margin-left: 0.5rem;">${trendIcon} ${Math.abs(workdaysChange.percentage).toFixed(1)}%</span>`;
            } else if (workdaysChange && workdaysChange.value !== 0) {
                const trendIcon = workdaysChange.trend === 'up' ? '↑' : workdaysChange.trend === 'down' ? '↓' : '→';
                const changeColor = workdaysChange.trend === 'up' ? '#10b981' : workdaysChange.trend === 'down' ? '#ef4444' : '#6b7280';
                displayText += ` <span style="color: ${changeColor}; font-size: 0.8em; margin-left: 0.5rem;">${trendIcon} ${workdaysChange.value > 0 ? '+' : ''}${workdaysChange.value}</span>`;
            }
            kpiTotalWorkdays.innerHTML = displayText;
        }
    } else {
        // ADMIN: Show salary-related KPIs
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

        // Total Gross Salary with comparison
        let totalGrossSalary = 0;
        if (salaryStats && salaryStats.success && salaryStats.data) {
            const monthlyData = salaryStats.data.monthly_data || [];
            if (monthlyData.length > 0) {
                totalGrossSalary = monthlyData.reduce((sum, month) => sum + (month.total_gross_salary || 0), 0);
            } else if (salaryStats.data.total_gross_salary !== undefined) {
                totalGrossSalary = salaryStats.data.total_gross_salary || 0;
            }
        }
        const kpiTotalGrossSalary = document.getElementById('kpi-total-gross-salary');
        if (kpiTotalGrossSalary) {
            const salaryChange = comparisonData?.data?.total_salary_change;
            let displayText = formatCurrency(totalGrossSalary);
            if (salaryChange && salaryChange.percentage !== null && salaryChange.percentage !== undefined) {
                const trendIcon = salaryChange.trend === 'up' ? '↑' : salaryChange.trend === 'down' ? '↓' : '→';
                const changeColor = salaryChange.trend === 'up' ? '#10b981' : salaryChange.trend === 'down' ? '#ef4444' : '#6b7280';
                displayText += ` <span style="color: ${changeColor}; font-size: 0.8em; margin-left: 0.5rem;">${trendIcon} ${Math.abs(salaryChange.percentage).toFixed(1)}%</span>`;
            } else if (salaryChange && salaryChange.value !== 0) {
                const trendIcon = salaryChange.trend === 'up' ? '↑' : salaryChange.trend === 'down' ? '↓' : '→';
                const changeColor = salaryChange.trend === 'up' ? '#10b981' : salaryChange.trend === 'down' ? '#ef4444' : '#6b7280';
                const changeValue = formatCurrency(Math.abs(salaryChange.value));
                displayText += ` <span style="color: ${changeColor}; font-size: 0.8em; margin-left: 0.5rem;">${trendIcon} ${changeValue}</span>`;
            }
            kpiTotalGrossSalary.innerHTML = displayText;
        }

        // Total Monthly Bills
        const totalMonthlyBills = totalGrossSalary;
        const kpiTotalMonthlyBills = document.getElementById('kpi-total-monthly-bills');
        if (kpiTotalMonthlyBills) {
            kpiTotalMonthlyBills.textContent = formatCurrency(totalMonthlyBills);
        }
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

function updateNewEmployees(employees) {
    // Use recent-employees container for new employees (for HR)
    const container = document.getElementById('recent-employees');
    if (!container) return;

    if (!employees || employees.length === 0) {
        container.innerHTML = '<div class="empty-state">Không có nhân viên mới</div>';
        return;
    }

    // Sort by hire date (most recent first) if available
    const sortedEmployees = [...employees].sort((a, b) => {
        const dateA = new Date(a.HireDate || a.hire_date || a.CreatedAt || a.created_at || 0);
        const dateB = new Date(b.HireDate || b.hire_date || b.CreatedAt || b.created_at || 0);
        return dateB - dateA;
    });

    container.innerHTML = sortedEmployees.slice(0, 5).map(emp => {
        const hireDate = emp.HireDate || emp.hire_date || emp.CreatedAt || emp.created_at;
        const formattedDate = hireDate ? formatDate(hireDate) : 'N/A';
        return `
            <div class="recent-employee-item">
                <div class="employee-avatar">${(emp.FullName || emp.full_name || 'N/A').charAt(0).toUpperCase()}</div>
                <div class="employee-info">
                    <div class="employee-name">${emp.FullName || emp.full_name || 'N/A'}</div>
                    <div class="employee-department">${emp.DepartmentName || emp.department_name || 'N/A'}</div>
                    <div class="employee-date" style="font-size: 0.85rem; color: var(--text-secondary); margin-top: 0.25rem;">
                        Ngày vào: ${formattedDate}
                    </div>
                </div>
            </div>
        `;
    }).join('');
}

function updatePositionsStats(positions) {
    const container = document.getElementById('positions-stats');
    if (!container) return;

    if (!positions || positions.length === 0) {
        container.innerHTML = '<div class="empty-state">Không có dữ liệu chức vụ</div>';
        return;
    }

    const positionsList = positions.slice(0, 5);
    container.innerHTML = positionsList.map(pos => `
        <div class="position-item" style="padding: 0.75rem; border-bottom: 1px solid var(--border-color);">
            <div style="font-weight: 500;">${pos.PositionName || pos.position_name || pos.name || 'N/A'}</div>
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

function updateTopDepartmentsTable(data) {
    const tbody = document.getElementById('department-stats-table');
    if (!tbody) return;

    if (!data || data.length === 0) {
        tbody.innerHTML = '<tr><td colspan="3" class="empty-state">Không có dữ liệu</td></tr>';
        return;
    }

    tbody.innerHTML = data.map(dept => `
        <tr>
            <td>${dept.DepartmentName || dept.department_name || 'N/A'}</td>
            <td><strong>${dept.EmployeeCount || dept.employee_count || 0}</strong></td>
            <td>${new Date().toLocaleDateString('vi-VN')}</td>
        </tr>
    `).join('');
}

let trendsChart = null;

function updateTrendsChart(trendsData) {
    const ctx = document.getElementById('trends-chart');
    if (!ctx) {
        // Nếu không có element, có thể tạo mới hoặc bỏ qua
        return;
    }

    // Destroy existing chart if any
    if (trendsChart) {
        trendsChart.destroy();
        trendsChart = null;
    }

    const employeeTrend = trendsData.employee_trend || [];
    const salaryTrend = trendsData.salary_trend || [];
    const workdaysTrend = trendsData.workdays_trend || [];
    
    console.log('Employee trend:', employeeTrend);
    console.log('Salary trend:', salaryTrend);
    console.log('Workdays trend:', workdaysTrend);
    
    // Log chi tiết salary trend để debug
    if (salaryTrend.length > 0) {
        console.log('Salary trend details:', salaryTrend.map(t => ({ month: t.month, total: t.total, type: typeof t.total })));
    }
    
    if (employeeTrend.length === 0 && salaryTrend.length === 0 && workdaysTrend.length === 0) {
        // Show empty state message
        const chartContainer = ctx.parentElement;
        if (chartContainer) {
            chartContainer.innerHTML = `
                <div style="padding: 2rem; text-align: center; color: var(--text-secondary);">
                    <p>Không có dữ liệu xu hướng cho 6 tháng gần đây</p>
                </div>
            `;
        }
        return;
    }

    // Prepare labels from employee trend or salary trend
    const labels = employeeTrend.length > 0 
        ? employeeTrend.map(t => {
            const [year, month] = t.month ? t.month.split('-') : ['', ''];
            return month ? `${month}/${year}` : '';
        })
        : salaryTrend.map(t => {
            const [year, month] = t.month ? t.month.split('-') : ['', ''];
            return month ? `${month}/${year}` : '';
        });

    const employeeData = employeeTrend.map(t => t.count || 0);
    // Parse total as number, handle both string and number
    const salaryData = salaryTrend.map(t => {
        const total = t.total || t.Total || 0;
        // Convert to number if it's a string
        const numTotal = typeof total === 'string' ? parseFloat(total) : Number(total);
        return isNaN(numTotal) ? 0 : numTotal;
    });
    
    console.log('Parsed salary data:', salaryData);

    // Normalize salary data to match employee data length if needed
    const normalizedSalaryData = salaryData.length === labels.length 
        ? salaryData 
        : new Array(labels.length).fill(0);

    // Xác định đơn vị phù hợp (trăm triệu hoặc tỷ)
    const maxSalary = Math.max(...normalizedSalaryData, 0);
    console.log('Max salary value:', maxSalary, 'from data:', normalizedSalaryData);
    
    // Nếu tất cả giá trị đều là 0, log cảnh báo
    if (maxSalary === 0 && normalizedSalaryData.length > 0) {
        console.warn('⚠️ All salary values are 0! Check backend query and data.');
        console.warn('Raw salary trend:', salaryTrend);
    }
    
    const useBillions = maxSalary >= 1000000000; // >= 1 tỷ thì dùng tỷ, < 1 tỷ thì dùng trăm triệu
    const divisor = useBillions ? 1000000000 : 100000000; // Tỷ hoặc trăm triệu
    const unitLabel = useBillions ? 'tỷ VNĐ' : 'trăm triệu VNĐ';
    const unitLabelShort = useBillions ? 'tỷ' : 'trăm triệu';

    trendsChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [
                {
                    label: 'Số nhân viên',
                    data: employeeData,
                    borderColor: 'rgb(37, 99, 235)',
                    backgroundColor: 'rgba(37, 99, 235, 0.1)',
                    tension: 0.4,
                    fill: true,
                    yAxisID: 'y'
                },
                {
                    label: `Tổng lương (${unitLabel})`,
                    data: normalizedSalaryData.map(s => s / divisor), // Convert to tỷ hoặc trăm triệu
                    borderColor: 'rgb(16, 185, 129)',
                    backgroundColor: 'rgba(16, 185, 129, 0.1)',
                    tension: 0.4,
                    fill: true,
                    yAxisID: 'y1'
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            interaction: {
                mode: 'index',
                intersect: false,
            },
            plugins: {
                legend: {
                    display: true,
                    position: 'top'
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            if (context.datasetIndex === 0) {
                                return context.dataset.label + ': ' + context.parsed.y + ' người';
                            } else {
                                // Hiển thị giá trị gốc trong tooltip
                                const originalValue = normalizedSalaryData[context.dataIndex] || 0;
                                return context.dataset.label + ': ' + formatCurrency(originalValue) + 
                                       ' (' + context.parsed.y.toFixed(2) + ' ' + unitLabelShort + ')';
                            }
                        }
                    }
                }
            },
            scales: {
                y: {
                    type: 'linear',
                    display: true,
                    position: 'left',
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Số nhân viên'
                    }
                },
                y1: {
                    type: 'linear',
                    display: true,
                    position: 'right',
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: `Tổng lương (${unitLabel})`
                    },
                    grid: {
                        drawOnChartArea: false,
                    },
                    ticks: {
                        callback: function(value) {
                            return value.toFixed(1) + ' ' + unitLabelShort;
                        }
                    }
                }
            }
        }
    });
}
