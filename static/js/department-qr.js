let scanner = null;
let isScanning = false;

// Initialize QR scanner
async function initScanner() {
    try {
        scanner = new Instascan.Scanner({ 
            video: document.getElementById('preview'),
            mirror: false,
            backgroundScan: true,
            scanPeriod: 5, // scan every 5ms
            refractoryPeriod: 5000 // wait 5s between successful scans
        });
        
        // Add scan event listener
        scanner.addListener('scan', handleScanResult);
        
        // Get available cameras
        const cameras = await Instascan.Camera.getCameras();
        if (cameras.length > 0) {
            // Try to use the back camera first
            const backCamera = cameras.find(camera => 
                camera.name.toLowerCase().includes('back'));
            await scanner.start(backCamera || cameras[0]);
            isScanning = true;
            updateScannerStatus('Scanner ready');
        } else {
            throw new Error('No cameras found on this device');
        }
    } catch (e) {
        console.error('Scanner initialization error:', e);
        updateScannerStatus('Scanner error: ' + e.message);
        alert('Error accessing camera: ' + e);
    }
}

// Handle QR code scan result
async function handleScanResult(content) {    try {
        // Temporary pause scanning while processing
        if (scanner) scanner.stop();
        
        const data = JSON.parse(content);
        
        // Validate required fields
        if (!data.visitor_id || !data.visit_id) {
            throw new Error('Invalid QR code format: missing required information');
        }
        
        // Update UI with visitor information
        document.getElementById('visitorId').textContent = data.visitor_id;
        document.getElementById('visitorName').textContent = data.name || 'Loading...';
        document.getElementById('visitDate').textContent = data.date ? new Date(data.date).toLocaleDateString() : 'Loading...';
        document.getElementById('visitId').textContent = data.visit_id;
        
        // Show scan result container and update status
        document.getElementById('scanResult').style.display = 'block';
        document.getElementById('visitStatus').textContent = 'Verifying...';
        document.getElementById('visitStatus').className = 'status-pending';// Verify QR code with server
        const response = await fetch('/department/verify_qr', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': document.querySelector('meta[name="csrf-token"]').content
            },
            body: JSON.stringify({
                visitor_id: data.visitor_id,
                visit_id: data.visit_id,
                timestamp: new Date().toISOString()
            })
        });        const result = await response.json();
        if (result.success) {
            // Update visitor information with verified data
            if (result.visitor) {
                document.getElementById('visitorName').textContent = result.visitor.name;
                document.getElementById('visitDate').textContent = result.visitor.visit_date;
            }
            document.getElementById('visitStatus').textContent = result.status;
            document.getElementById('visitStatus').className = 'status-' + result.status.toLowerCase();
            
            // Play success sound or vibrate for feedback
            if ('vibrate' in navigator) {
                navigator.vibrate(200);
            }
        } else {
            throw new Error(result.message || 'Verification failed');
        }
    } catch (e) {
        console.error('Error processing QR code:', e);
        document.getElementById('errorMessage').textContent = e.message;
        document.getElementById('errorMessage').style.display = 'block';
        document.getElementById('visitStatus').textContent = 'Error';
        document.getElementById('visitStatus').className = 'status-error';
    } finally {
        // Resume scanning after a delay
        setTimeout(() => {
            if (scanner && isScanning) {
                scanner.start();
                document.getElementById('errorMessage').style.display = 'none';
            }
        }, 3000);
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
