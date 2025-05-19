document.addEventListener('DOMContentLoaded', function() {
    loadPendingRequests();
    
    // Add event listener for search
    document.getElementById('searchInput').addEventListener('input', searchRequests);
});

function loadPendingRequests() {
    const tableBody = document.getElementById('requestTableBody');
    tableBody.innerHTML = '';
    
    // Fetch pending requests from server
    fetch('/security/get_pending_requests')
        .then(response => response.json())
        .then(data => {
            if (data.success && data.requests && data.requests.length > 0) {
                data.requests.forEach(request => {
                    const row = createRequestRow(request);
                    tableBody.appendChild(row);
                });
            } else {
                showEmptyState(tableBody);
            }
        })
        .catch(error => {
            console.error('Error loading pending requests:', error);
            showEmptyState(tableBody);
        });
}

function createRequestRow(request) {
    const tr = document.createElement('tr');
    
    tr.innerHTML = `
        <td>${request.id}</td>
        <td>${request.name}</td>
        <td>${request.address}</td>
        <td>${request.contactNo}</td>
        <td>${request.purpose}</td>
        <td>${request.date}</td>
        <td><span class="status-${request.status.toLowerCase()}">${request.status}</span></td>
        <td>
            ${request.status === 'Pending' ? `                <div class="approval-buttons">
                    <button class="btn-approve" onclick="updateStatus('${request.id}', true)">
                        <i class="fas fa-check"></i>
                    </button>
                    <button class="btn-reject" onclick="updateStatus('${request.id}', false)">
                        <i class="fas fa-times"></i>
                    </button>
                </div>
            ` : ''}
            <button class="btn-qr" onclick="generateQR('${request.id}', '${request.name}')" title="Generate QR Code">
                <i class="fas fa-qrcode"></i>
            </button>
        </td>
    `;
    
    return tr;
}

function updateStatus(id, isApproved) {
    if (!isApproved) {
        // Handle rejection separately
        // TODO: Implement rejection logic
        return;
    }

    const formData = new FormData();
    formData.append('visitId', id);
    
    // Show loading notification
    showNotification('Processing request...', 'info');
    
    fetch('/security/approve_visit', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showNotification(data.message, 'success');
            // Reload the requests after a short delay
            setTimeout(() => {
                loadPendingRequests();
            }, 1000);
        } else {
            showNotification(data.message || 'Failed to update request', 'error');
            console.error('Error:', data.error);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        showNotification('An error occurred while processing the request', 'error');
    });
}

function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.textContent = message;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.classList.add('fade-out');
        setTimeout(() => {
            notification.remove();
        }, 300);
    }, 3000);
}

function showEmptyState(tableBody) {
    const emptyRow = document.createElement('tr');
    emptyRow.innerHTML = `
        <td colspan="8" style="text-align: center; padding: 20px;">
            <i class="fas fa-inbox" style="font-size: 24px; color: #ccc; margin-bottom: 10px;"></i>
            <p style="margin: 0;">No pending requests found</p>
        </td>
    `;
    tableBody.appendChild(emptyRow);
}

function searchRequests() {
    const searchTerm = document.getElementById('searchInput').value.toLowerCase();
    const rows = document.querySelectorAll('#requestTableBody tr');
    
    rows.forEach(row => {
        const text = row.textContent.toLowerCase();
        row.style.display = text.includes(searchTerm) ? '' : 'none';
    });
}

function generateQR(visitorId, visitorName) {
    // Redirect to QR Management page with query parameters
    window.location.href = `/security/qr?visitorId=${visitorId}&visitorName=${encodeURIComponent(visitorName)}`;
}

// Initialize the page
document.addEventListener('DOMContentLoaded', function() {
    loadPendingRequests();
    
    // Add event listener for search
    document.getElementById('searchInput').addEventListener('input', searchRequests);
    
    // Navigation between pages
    document.querySelectorAll('.menu-item').forEach(item => {
        item.addEventListener('click', function() {
            const page = this.getAttribute('data-page');
            if (page) {
                window.location.href = page;
            }
        });
    });
});
