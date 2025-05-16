let visits = [];
let currentPage = 1;
const itemsPerPage = 10;
let totalPages = 1;

// Load visit data from server
async function loadVisitData() {
    try {
        const response = await fetch('/security/get_history');
        const data = await response.json();
        
        if (data.success) {
            visits = data.visits;
            totalPages = Math.ceil(visits.length / itemsPerPage);
            displayVisits(1);
            updatePagination();
        } else {
            showError('Error loading visit records: ' + data.message);
        }
    } catch (e) {
        console.error('Error:', e);
        showError('Error loading visit records');
    }
}

// Display visits for current page
function displayVisits(page) {
    const tableBody = document.getElementById('historyTableBody');
    const noRecords = document.getElementById('noRecords');
    
    if (!visits || visits.length === 0) {
        tableBody.innerHTML = '';
        noRecords.style.display = 'block';
        return;
    }
    
    noRecords.style.display = 'none';
    const start = (page - 1) * itemsPerPage;
    const end = start + itemsPerPage;
    const paginatedVisits = visits.slice(start, end);
    
    tableBody.innerHTML = '';
    
    paginatedVisits.forEach(visit => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>
                <div class="visitor-info">
                    <img src="${visit.visitor_photo || '/static/images/default-avatar.png'}" 
                         alt="Visitor Photo" class="visitor-photo">
                    <div>
                        <div>${visit.name}</div>
                        <small>${visit.visitor_id}</small>
                    </div>
                </div>
            </td>
            <td>${visit.id}</td>
            <td>${visit.purpose}</td>
            <td>${visit.location}</td>
            <td>${formatDate(visit.date)}</td>
            <td>${formatTime(visit.time_in)}</td>
            <td>${formatTime(visit.time_out)}</td>
            <td>
                <span class="status-badge status-${visit.status.toLowerCase()}">
                    ${visit.status}
                </span>
            </td>
        `;
        tableBody.appendChild(row);
    });
    
    currentPage = page;
    updatePagination();
}

// Format date
function formatDate(dateStr) {
    if (!dateStr) return '-';
    const date = new Date(dateStr);
    return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
    });
}

// Format time
function formatTime(timeStr) {
    if (!timeStr) return '-';
    const [hours, minutes] = timeStr.split(':');
    const date = new Date();
    date.setHours(hours, minutes);
    return date.toLocaleTimeString('en-US', {
        hour: '2-digit',
        minute: '2-digit'
    });
}

// Update pagination controls
function updatePagination() {
    const pagination = document.getElementById('pagination');
    const maxButtons = 5;
    const buttons = [];
    
    // Previous buttons
    buttons.push(`
        <button onclick="changePage(1)" ${currentPage === 1 ? 'disabled' : ''}>
            <i class="fas fa-angle-double-left"></i>
        </button>
        <button onclick="changePage(${currentPage - 1})" ${currentPage === 1 ? 'disabled' : ''}>
            <i class="fas fa-angle-left"></i>
        </button>
    `);
    
    // Page buttons
    let startPage = Math.max(1, currentPage - Math.floor(maxButtons / 2));
    let endPage = Math.min(totalPages, startPage + maxButtons - 1);
    
    if (endPage - startPage + 1 < maxButtons) {
        startPage = Math.max(1, endPage - maxButtons + 1);
    }
    
    for (let i = startPage; i <= endPage; i++) {
        buttons.push(`
            <button class="${i === currentPage ? 'active' : ''}" onclick="changePage(${i})">
                ${i}
            </button>
        `);
    }
    
    // Next buttons
    buttons.push(`
        <button onclick="changePage(${currentPage + 1})" ${currentPage === totalPages ? 'disabled' : ''}>
            <i class="fas fa-angle-right"></i>
        </button>
        <button onclick="changePage(${totalPages})" ${currentPage === totalPages ? 'disabled' : ''}>
            <i class="fas fa-angle-double-right"></i>
        </button>
    `);
    
    pagination.innerHTML = buttons.join('');
}

// Change page
function changePage(page) {
    if (page < 1 || page > totalPages || page === currentPage) return;
    displayVisits(page);
}

// Show error message
function showError(message) {
    const tableBody = document.getElementById('historyTableBody');
    const noRecords = document.getElementById('noRecords');
    tableBody.innerHTML = '';
    noRecords.innerHTML = `
        <i class="fas fa-exclamation-circle"></i>
        <h2>Error</h2>
        <p>${message}</p>
    `;
    noRecords.style.display = 'block';
}

// Search functionality
function handleSearch(searchText) {
    searchText = searchText.toLowerCase();
    const filteredVisits = visits.filter(visit => {
        return (
            visit.name.toLowerCase().includes(searchText) ||
            visit.visitor_id.toLowerCase().includes(searchText) ||
            visit.purpose.toLowerCase().includes(searchText) ||
            visit.location.toLowerCase().includes(searchText)
        );
    });
    
    visits = filteredVisits;
    totalPages = Math.ceil(visits.length / itemsPerPage);
    displayVisits(1);
}

// Date filter functionality
function handleDateFilter() {
    const startDate = document.getElementById('startDate').value;
    const endDate = document.getElementById('endDate').value;
    
    const filteredVisits = visits.filter(visit => {
        const visitDate = new Date(visit.date);
        const start = startDate ? new Date(startDate) : null;
        const end = endDate ? new Date(endDate) : null;
        
        if (start) {
            start.setHours(0, 0, 0, 0);
            if (visitDate < start) return false;
        }
        if (end) {
            end.setHours(23, 59, 59, 999);
            if (visitDate > end) return false;
        }
        return true;
    });
    
    visits = filteredVisits;
    totalPages = Math.ceil(visits.length / itemsPerPage);
    displayVisits(1);
}

// Export to Excel
function exportToExcel() {
    if (!visits || visits.length === 0) {
        alert('No data to export');
        return;
    }
    
    const worksheet = XLSX.utils.json_to_sheet(visits.map(visit => ({
        'Visitor Name': visit.name,
        'Visitor ID': visit.visitor_id,
        'Visit ID': visit.id,
        'Purpose': visit.purpose,
        'Location': visit.location,
        'Date': formatDate(visit.date),
        'Time In': formatTime(visit.time_in),
        'Time Out': formatTime(visit.time_out),
        'Status': visit.status
    })));
    
    const workbook = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(workbook, worksheet, "Visit Records");
    
    const date = new Date().toISOString().split('T')[0];
    XLSX.writeFile(workbook, `visit_records_${date}.xlsx`);
}

// Print records
function printRecords() {
    const printContent = document.querySelector('.history-container').cloneNode(true);
    
    // Remove action buttons and search filters
    const actionBar = printContent.querySelector('.actions-bar');
    if (actionBar) actionBar.remove();
    
    const pagination = printContent.querySelector('.pagination');
    if (pagination) pagination.remove();
    
    const win = window.open('', '_blank');
    win.document.write(`
        <!DOCTYPE html>
        <html>
        <head>
            <title>Visit Records - Print View</title>
            <style>
                body { 
                    font-family: Arial, sans-serif;
                    padding: 20px;
                }
                .history-title {
                    background-color: #13334C;
                    color: white;
                    padding: 15px;
                    text-align: center;
                    margin-bottom: 20px;
                }
                .history-table {
                    width: 100%;
                    border-collapse: collapse;
                    margin-top: 20px;
                }
                .history-table th,
                .history-table td {
                    padding: 8px;
                    border: 1px solid #ddd;
                    text-align: left;
                }
                .history-table th {
                    background-color: #f8f9fa;
                }
                .visitor-info {
                    display: flex;
                    align-items: center;
                    gap: 10px;
                }
                .status-badge {
                    padding: 3px 8px;
                    border-radius: 12px;
                    font-size: 12px;
                }
                @media print {
                    .history-title { -webkit-print-color-adjust: exact; }
                    .status-badge { -webkit-print-color-adjust: exact; }
                }
            </style>
        </head>
        <body>
            ${printContent.innerHTML}
        </body>
        </html>
    `);
    
    win.document.close();
    setTimeout(() => {
        win.print();
        win.close();
    }, 250);
}

// Event listeners
document.getElementById('searchInput').addEventListener('input', (e) => handleSearch(e.target.value));
document.getElementById('startDate').addEventListener('change', handleDateFilter);
document.getElementById('endDate').addEventListener('change', handleDateFilter);

// Initialize
window.addEventListener('load', loadVisitData);