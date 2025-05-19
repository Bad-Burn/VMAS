document.addEventListener('DOMContentLoaded', function() {
    // Load pending requests when the page loads
    loadPendingRequests();
    
    // Add event listener for search
    const searchInput = document.getElementById('searchInput');
    if (searchInput) {
        searchInput.addEventListener('input', searchRequests);
    }
});

function loadPendingRequests() {
    const tableBody = document.getElementById('requestTableBody');
    if (!tableBody) {
        console.error('Table body element not found!');
        return;
    }

    // Show loading state
    tableBody.innerHTML = '<tr><td colspan="7" style="text-align:center;">Loading pending requests...</td></tr>';
    
    // Fetch pending requests from server
    fetch('/security/get_pending_requests')
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            console.log('Received pending requests:', data); // Debug log
            tableBody.innerHTML = ''; // Clear loading state

            if (data.success && data.requests && data.requests.length > 0) {
                data.requests.forEach(request => {
                    // Format date
                    if (request.date) {
                        try {
                            const date = new Date(request.date);
                            request.date = date.toISOString().split('T')[0];
                        } catch (e) {
                            console.warn('Error formatting date:', e);
                        }
                    }

                    const row = document.createElement('tr');
                    row.innerHTML = `
                        <td>${request.visitor_id || request.id}</td>
                        <td>${request.name}</td>
                        <td>${request.purpose}</td>
                        <td>${request.location || 'N/A'}</td>
                        <td>${request.date || 'Not set'}</td>
                        <td><span class="status-badge status-pending">Pending</span></td>
                        <td class="actions-cell">
                            <button class="btn btn-approve" onclick="approveRequest('${request.id}')">
                                <i class="fas fa-check"></i> Approve
                            </button>
                            <button class="btn btn-reject" onclick="rejectRequest('${request.id}')">
                                <i class="fas fa-times"></i> Reject
                            </button>
                        </td>
                    `;
                    tableBody.appendChild(row);
                });
            } else {
                tableBody.innerHTML = '<tr><td colspan="7" style="text-align:center;">No pending requests found</td></tr>';
            }
        })
        .catch(error => {
            console.error('Error loading pending requests:', error);
            tableBody.innerHTML = '<tr><td colspan="7" style="text-align:center;">Error loading requests. Please try again.</td></tr>';
        });
}

// Search functionality
function searchRequests() {
    const searchText = document.getElementById('searchInput').value.toLowerCase();
    const rows = document.querySelectorAll('#requestTableBody tr');
    
    rows.forEach(row => {
        const text = row.textContent.toLowerCase();
        row.style.display = text.includes(searchText) ? '' : 'none';
    });
}

function showNotification(message, isSuccess = true) {
    const notification = document.getElementById('notification');
    if (!notification) return;
    
    notification.className = `notification ${isSuccess ? 'success' : 'error'}`;
    document.getElementById('notification-message').textContent = message;
    notification.style.display = 'flex';
    
    setTimeout(() => {
        notification.style.display = 'none';
    }, 5000);
}

function closeNotification() {
    const notification = document.getElementById('notification');
    if (notification) {
        notification.style.display = 'none';
    }
}

// Approve request
function approveRequest(requestId) {
    if (!confirm('Are you sure you want to approve this request?')) return;
    
    fetch('/security/approve_request', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ requestId: requestId })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showNotification('Request approved successfully!');
            setTimeout(() => {
                window.location.href = '/security/qr';  // Redirect to QR management
            }, 1500);
        } else {
            showNotification(data.error || 'Failed to approve request', false);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showNotification('An error occurred while approving the request', false);
    });
}

// Reject request
function rejectRequest(requestId) {
    if (!confirm('Are you sure you want to reject this request?')) return;
    
    fetch('/security/reject_request', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ requestId: requestId })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showNotification('Request rejected successfully');
            setTimeout(() => {
                loadPendingRequests();  // Reload the requests
            }, 1500);
        } else {
            showNotification(data.error || 'Failed to reject request', false);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showNotification('An error occurred while rejecting the request', false);
    });
}
