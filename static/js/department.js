document.addEventListener('DOMContentLoaded', function() {
    // Load staff information
    loadStaffInfo();
    
    // Load dashboard statistics
    loadDashboardStats();
    
    // Load appointments
    loadAppointments();
    
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

function updateStatus(appointmentId, status) {
    const appointments = JSON.parse(localStorage.getItem('appointments')) || [];
    const appointmentIndex = appointments.findIndex(app => app.id === appointmentId);
    
    if (appointmentIndex !== -1) {
        appointments[appointmentIndex].status = status;
        localStorage.setItem('appointments', JSON.stringify(appointments));
        
        // Reload the dashboard
        loadDashboardStats();
        loadAppointments();
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
