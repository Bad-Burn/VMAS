document.addEventListener('DOMContentLoaded', function() {
    loadVisitorHistory();
    setupEventListeners();
});

// Mock data for visitor history
const mockHistory = [
    {
        id: 'V230501',
        name: 'John Doe',
        address: '123 Main St',
        contactNo: '+63 912 345 6789',
        purpose: 'Meeting',
        location: 'IT Department',
        date: '2025-05-09',
        timeIn: '09:00 AM',
        timeOut: '11:30 AM',
        status: 'Completed'
    },
    {
        id: 'V230502',
        name: 'Jane Smith',
        address: '456 Park Ave',
        contactNo: '+63 923 456 7890',
        purpose: 'Interview',
        location: 'HR Department',
        date: '2025-05-09',
        timeIn: '02:00 PM',
        timeOut: '03:30 PM',
        status: 'Completed'
    },
    // Add more mock data as needed
];

let currentPage = 1;
const itemsPerPage = 10;

function loadVisitorHistory() {
    // Get history from localStorage or use mock data
    const history = JSON.parse(localStorage.getItem('visitorHistory')) || mockHistory;
    
    if (!localStorage.getItem('visitorHistory')) {
        localStorage.setItem('visitorHistory', JSON.stringify(mockHistory));
    }
    
    displayHistoryData(history);
    updatePagination(history);
}

function displayHistoryData(history, page = 1) {
    const tableBody = document.getElementById('historyTableBody');
    const startIndex = (page - 1) * itemsPerPage;
    const endIndex = startIndex + itemsPerPage;
    const paginatedData = history.slice(startIndex, endIndex);
    
    tableBody.innerHTML = '';
    
    paginatedData.forEach(entry => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${entry.id}</td>
            <td>${entry.name}</td>
            <td>${entry.address}</td>
            <td>${entry.contactNo}</td>
            <td>${entry.purpose}</td>
            <td>${entry.location}</td>
            <td>${entry.date}</td>
            <td>${entry.timeIn}</td>
            <td>${entry.timeOut}</td>
            <td><span class="status-${entry.status.toLowerCase()}">${entry.status}</span></td>
        `;
        tableBody.appendChild(row);
    });
}

function updatePagination(history) {
    const totalPages = Math.ceil(history.length / itemsPerPage);
    const prevBtn = document.getElementById('prevPage');
    const nextBtn = document.getElementById('nextPage');
    const currentPageSpan = document.getElementById('currentPage');
    
    currentPageSpan.textContent = `Page ${currentPage} of ${totalPages}`;
    prevBtn.disabled = currentPage === 1;
    nextBtn.disabled = currentPage === totalPages;
}

function setupEventListeners() {
    // Search functionality
    document.getElementById('searchInput').addEventListener('input', function(e) {
        const searchTerm = e.target.value.toLowerCase();
        const history = JSON.parse(localStorage.getItem('visitorHistory')) || mockHistory;
        
        const filteredHistory = history.filter(entry => 
            entry.name.toLowerCase().includes(searchTerm) ||
            entry.id.toLowerCase().includes(searchTerm) ||
            entry.purpose.toLowerCase().includes(searchTerm)
        );
        
        currentPage = 1;
        displayHistoryData(filteredHistory);
        updatePagination(filteredHistory);
    });
    
    // Date filter
    const startDate = document.getElementById('startDate');
    const endDate = document.getElementById('endDate');
    
    [startDate, endDate].forEach(input => {
        input.addEventListener('change', function() {
            if (startDate.value && endDate.value) {
                const history = JSON.parse(localStorage.getItem('visitorHistory')) || mockHistory;
                const filteredHistory = history.filter(entry => {
                    const date = new Date(entry.date);
                    return date >= new Date(startDate.value) && 
                           date <= new Date(endDate.value);
                });
                
                currentPage = 1;
                displayHistoryData(filteredHistory);
                updatePagination(filteredHistory);
            }
        });
    });
    
    // Pagination
    document.getElementById('prevPage').addEventListener('click', function() {
        if (currentPage > 1) {
            currentPage--;
            loadVisitorHistory();
        }
    });
    
    document.getElementById('nextPage').addEventListener('click', function() {
        const history = JSON.parse(localStorage.getItem('visitorHistory')) || mockHistory;
        const totalPages = Math.ceil(history.length / itemsPerPage);
        
        if (currentPage < totalPages) {
            currentPage++;
            loadVisitorHistory();
        }
    });
    
    // Print functionality
    document.getElementById('printHistory').addEventListener('click', function() {
        window.print();
    });
}

// Update menu item active state
document.querySelectorAll('.menu-item').forEach(item => {
    item.addEventListener('click', function() {
        document.querySelectorAll('.menu-item').forEach(i => i.classList.remove('active'));
        this.classList.add('active');
    });
});
