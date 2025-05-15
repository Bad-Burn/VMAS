// Handle QR scanner initialization and events
let scanner = null;

// Initialize QR scanner
async function initScanner() {
    scanner = new Instascan.Scanner({ video: document.getElementById('preview') });
    
    scanner.addListener('scan', function (content) {
        handleScanResult(content);
    });

    try {
        const cameras = await Instascan.Camera.getCameras();
        if (cameras.length > 0) {
            await scanner.start(cameras[0]);
        } else {
            console.error('No cameras found.');
            alert('No cameras found.');
        }
    } catch (e) {
        console.error('Error accessing camera:', e);
        alert('Error accessing camera: ' + e);
    }
}

// Handle QR code scan result
async function handleScanResult(content) {
    try {
        const data = JSON.parse(content);
        
        // Update UI with visitor information
        document.getElementById('visitorId').textContent = data.visitor_id;
        document.getElementById('visitorName').textContent = data.name;
        document.getElementById('visitDate').textContent = new Date(data.date).toLocaleDateString();
        document.getElementById('visitId').textContent = data.visit_id;
        
        // Show scan result container
        document.getElementById('scanResult').style.display = 'block';

        // Verify QR code with server
        const response = await fetch('/api/verify-visit', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data)
        });

        const result = await response.json();
        if (result.success) {
            document.getElementById('visitStatus').textContent = result.status;
            document.getElementById('visitStatus').className = 'status-' + result.status.toLowerCase();
        } else {
            alert('Error verifying visit: ' + result.message);
        }
    } catch (e) {
        console.error('Invalid QR code content:', e);
        alert('Invalid QR code. Please try again.');
    }
}

// Handle visit approval/rejection
async function handleVisit(action) {
    const visitId = document.getElementById('visitId').textContent;
    
    try {
        const response = await fetch('/api/update-visit-status', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                visitId: visitId,
                action: action
            })
        });

        const result = await response.json();
        if (result.success) {
            document.getElementById('visitStatus').textContent = action.toUpperCase();
            document.getElementById('visitStatus').className = 'status-' + action.toLowerCase();
            alert(`Visit ${action}d successfully`);
        } else {
            alert(`Error ${action}ing visit: ${result.message}`);
        }
    } catch (error) {
        console.error('Error:', error);
        alert(`Error ${action}ing visit`);
    }
}

// Handle QR code image upload
function handleFileUpload() {
    const fileInput = document.getElementById('qrFileInput');
    const file = fileInput.files[0];
    
    if (file) {
        const reader = new FileReader();
        reader.onload = function(e) {
            const qrImage = new Image();
            qrImage.src = e.target.result;
            
            // Here you would need to implement QR code reading from image
            // This would require additional library support for image-based QR scanning
            alert('QR code image upload functionality is not yet implemented');
        };
        reader.readAsDataURL(file);
    } else {
        alert('Please select a file first');
    }
}

// Initialize scanner when page loads
window.addEventListener('load', initScanner);
