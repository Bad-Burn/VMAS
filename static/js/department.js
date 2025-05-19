// Function to format date
function formatDate(dateString) {
    if (!dateString) return 'N/A';
    const date = new Date(dateString);
    if (isNaN(date.getTime())) return 'Invalid Date';
    return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
    });
}

// Function to load departments
function loadDepartments() {
    console.log('Loading departments...');
    const tableBody = document.getElementById('departmentTable');
    tableBody.innerHTML = '<tr><td colspan="5" style="text-align: center;">Loading departments...</td></tr>';

    fetch('/security/get_departments')
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            console.log('Departments data:', data);
            if (data.success && data.departments && data.departments.length > 0) {
                tableBody.innerHTML = '';
                data.departments.forEach(dept => {
                    const row = document.createElement('tr');
                    const statusClass = (dept.status || 'active').toLowerCase();
                    row.innerHTML = `
                        <td>${dept.department_id || 'N/A'}</td>
                        <td>${dept.department_name || 'N/A'}</td>
                        <td>${dept.email || 'N/A'}</td>
                        <td><span class="status-badge ${statusClass}">${dept.status || 'active'}</span></td>
                        <td>${formatDate(dept.created_at)}</td>
                    `;
                    row.addEventListener('click', () => {
                        const allRows = tableBody.getElementsByTagName('tr');
                        for (let r of allRows) {
                            r.classList.remove('selected');
                        }
                        row.classList.add('selected');
                    });
                    tableBody.appendChild(row);
                });
            } else {
                tableBody.innerHTML = '<tr><td colspan="5" style="text-align: center;">' + 
                    (data.departments && data.departments.length === 0 ? 'No departments found' : 
                    'Failed to load departments: ' + (data.message || 'Unknown error')) + '</td></tr>';
            }
        })
        .catch(error => {
            console.error('Error loading departments:', error);
            tableBody.innerHTML = '<tr><td colspan="5" style="text-align: center;">Error loading departments: ' + error.message + '</td></tr>';
        });
}

// Initialize when document is loaded
document.addEventListener('DOMContentLoaded', function() {
    console.log('Document loaded, initializing...');
    loadDepartments();
    
    // Initialize row selection
    document.getElementById('departmentTable').addEventListener('click', function(e) {
        const row = e.target.closest('tr');
        if (row) {
            this.querySelectorAll('tr').forEach(r => r.classList.remove('selected'));
            row.classList.add('selected');
        }
    });
    
    // Add search event listener
    document.getElementById('searchDepartment').addEventListener('input', function() {
        const searchText = this.value.toLowerCase();
        const rows = document.getElementById('departmentTable').getElementsByTagName('tr');
        Array.from(rows).forEach(row => {
            const text = row.textContent.toLowerCase();
            row.style.display = text.includes(searchText) ? '' : 'none';
        });
    });
});
    
    // Add event listeners
    document.getElementById('searchBtn').addEventListener('click', searchAppointments);
    document.getElementById('logoutBtn').addEventListener('click', logout);
    document.getElementById('searchAppointments').addEventListener('keyup', function(e) {
        if (e.key === 'Enter') {
            searchAppointments();
        }
    });
});

function loadStaffInfo() {
    const staffData = JSON.parse(localStorage.getItem('currentUser'));
    if (staffData) {
        document.getElementById('staffName').textContent = staffData.name || 'Department Staff';
        document.getElementById('staffId').textContent = staffData.id || '';
    }
}

function loadDashboardStats() {
    // Get appointments from localStorage
    const appointments = JSON.parse(localStorage.getItem('appointments')) || [];
    const today = new Date().toDateString();
    
    // Count today's appointments
    const todayAppointments = appointments.filter(app => 
        new Date(app.date).toDateString() === today
    ).length;
    
    // Count pending requests
    const pendingRequests = appointments.filter(app => 
        app.status === 'pending'
    ).length;
    
    // Count total visitors
    const visitors = new Set(appointments.map(app => app.visitorId)).size;
    
    // Update the UI
    document.getElementById('todayAppointments').textContent = todayAppointments;
    document.getElementById('pendingRequests').textContent = pendingRequests;
    document.getElementById('totalVisitors').textContent = visitors;
}

function loadAppointments() {
    const appointments = JSON.parse(localStorage.getItem('appointments')) || [];
    const tbody = document.querySelector('#appointmentsTable tbody');
    tbody.innerHTML = '';
    
    const today = new Date().toDateString();
    const todayAppointments = appointments.filter(app => 
        new Date(app.date).toDateString() === today
    );
    
    if (todayAppointments.length === 0) {
        const tr = document.createElement('tr');
        tr.innerHTML = '<td colspan="6" style="text-align: center;">No appointments for today</td>';
        tbody.appendChild(tr);
        return;
    }
    
    todayAppointments.forEach(appointment => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td>${appointment.visitorId}</td>
            <td>${appointment.visitorName}</td>
            <td>${appointment.purpose}</td>
            <td>${appointment.time}</td>
            <td><span class="status-${appointment.status}">${appointment.status}</span></td>
            <td>
                ${appointment.status === 'pending' ? `
                    <button class="action-btn approve-btn" onclick="updateStatus('${appointment.id}', 'approved')">Approve</button>
                    <button class="action-btn reject-btn" onclick="updateStatus('${appointment.id}', 'rejected')">Reject</button>
                ` : `
                    <button class="action-btn view-btn" onclick="viewDetails('${appointment.id}')">View</button>
                `}
            </td>
        `;
        tbody.appendChild(tr);
    });
}

// Function to edit department
function editDepartment() {
    const selectedRow = document.querySelector('#departmentTable tr.selected');
    if (selectedRow) {
        const deptId = selectedRow.cells[0].textContent;
        const deptName = selectedRow.cells[1].textContent;
        const email = selectedRow.cells[2].textContent;
        // TODO: Implement edit functionality
        alert('Edit functionality coming soon');
        console.log('Edit department:', { deptId, deptName, email });
    } else {
        alert('Please select a department to edit');
    }
}

// Function to delete department
function deleteDepartment() {
    const selectedRow = document.querySelector('#departmentTable tr.selected');
    if (selectedRow) {
        const deptId = selectedRow.cells[0].textContent;
        if (confirm('Are you sure you want to delete this department?')) {
            // TODO: Implement delete functionality
            alert('Delete functionality coming soon');
            console.log('Delete department:', deptId);
        }
    } else {
        alert('Please select a department to delete');
    }
}

function viewDetails(appointmentId) {
    const appointments = JSON.parse(localStorage.getItem('appointments')) || [];
    const appointment = appointments.find(app => app.id === appointmentId);
    
    if (appointment) {
        // TODO: Implement appointment details view
        alert(`Viewing details for appointment ${appointmentId}`);
    }
}

function searchAppointments() {
    const searchTerm = document.getElementById('searchAppointments').value.toLowerCase();
    const rows = document.querySelectorAll('#appointmentsTable tbody tr');
    
    rows.forEach(row => {
        const text = row.textContent.toLowerCase();
        row.style.display = text.includes(searchTerm) ? '' : 'none';
    });
}

function logout() {
    localStorage.removeItem('currentUser');
    window.location.href = 'mainweb.html';
}
