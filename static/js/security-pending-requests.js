document.addEventListener('DOMContentLoaded', function() {
    loadPendingRequests();
    
    // Add event listener for search
    document.getElementById('searchInput').addEventListener('input', searchRequests);
});

function loadPendingRequests() {
    // Get requests from localStorage or use default empty array
    const requests = JSON.parse(localStorage.getItem('pendingRequests')) || getMockData();
    const tableBody = document.getElementById('requestTableBody');
    tableBody.innerHTML = '';
    
    if (requests.length === 0) {
        showEmptyState(tableBody);
        return;
    }
    
    requests.forEach(request => {
        const row = createRequestRow(request);
        tableBody.appendChild(row);
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

function updateStatus(requestId, isApproved) {
    const requests = JSON.parse(localStorage.getItem('pendingRequests')) || [];
    
    if (confirm(confirmMessage)) {
        const status = isApproved ? 'Approved' : 'Rejected';
        row.cells[6].innerHTML = `<span class="status-${status.toLowerCase()}">${status}</span>`;
        
        // Update status in storage
        const requestIndex = pendingRequests.findIndex(req => req.id === visitorId);
        if (requestIndex !== -1) {
            pendingRequests[requestIndex].status = status;
            localStorage.setItem('pendingRequests', JSON.stringify(pendingRequests));
        }
        
        // Remove approval buttons after decision
        row.cells[7].innerHTML = '';
        
        // Show success message
        alert(`Successfully ${action}d the request from ${visitorName}`);
    }
}

// Add new pending request to the table
function addPendingRequest(request) {
    const tbody = document.getElementById('requestTableBody');
    const row = document.createElement('tr');
    
    row.innerHTML = `
        <td>${request.id}</td>
        <td>${request.name}</td>
        <td>${request.address}</td>
        <td>${request.contactNo}</td>
        <td>${request.purpose}</td>
        <td>${request.date}</td>
        <td><span class="status-pending">Pending</span></td>
        <td>
            <div class="approval-buttons">
                <button class="btn-approve"><i class="fas fa-check"></i></button>
                <button class="btn-reject"><i class="fas fa-times"></i></button>
            </div>
        </td>
    `;
    
    tbody.appendChild(row);
}

// Load mock data
const mockRequests = [
    {
        id: 'V230501',
        name: 'John Doe',
        address: '123 Main St',
        contactNo: '+63 912 345 6789',
        purpose: 'Meeting',
        date: '2025-05-09',
        status: 'Pending'
    },
    {
        id: 'V230502',
        name: 'Jane Smith',
        address: '456 Park Ave',
        contactNo: '+63 923 456 7890',
        purpose: 'Inquiry',
        date: '2025-05-09',
        status: 'Pending'
    },
    {
        id: 'V230503',
        name: 'Mike Johnson',
        address: '789 Oak St',
        contactNo: '+63 934 567 8901',
        purpose: 'Delivery',
        date: '2025-05-09',
        status: 'Pending'
    }
];

function generateQR(visitorId, visitorName) {
    // Store the visitor info in localStorage to pass it to the QR Management page
    const visitorInfo = {
        id: visitorId,
        name: visitorName
    };
    localStorage.setItem('pendingVisitorForQR', JSON.stringify(visitorInfo));
    
    // Redirect to QR Management page
    window.location.href = 'QR-Management.html';
}

// Initialize the page
document.addEventListener('DOMContentLoaded', function() {
    // Load saved requests or use mock data
    pendingRequests = JSON.parse(localStorage.getItem('pendingRequests')) || mockRequests;
    
    // If no saved requests, save mock data
    if (!localStorage.getItem('pendingRequests')) {
        localStorage.setItem('pendingRequests', JSON.stringify(mockRequests));
    }
    
    // Display all requests
    pendingRequests.forEach(request => addPendingRequest(request));
    
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
