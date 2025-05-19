// Handle menu navigation
document.querySelectorAll('.menu-item').forEach(item => {
    item.addEventListener('click', function() {
        const page = this.getAttribute('data-page');
        if (page) {
            window.location.href = page;
        }
    });
});

// Form handling
document.addEventListener('DOMContentLoaded', function() {
    const registrationForm = document.getElementById('registrationForm');
    const photoUpload = document.getElementById('photoUpload');
    const photoPreview = document.getElementById('photoPreview');
    
    if (registrationForm) {
        registrationForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            // Validate form
            if (validateForm()) {
                // Generate visitor ID
                const visitorId = generateVisitorId();
                document.getElementById('visitorId').value = visitorId;
                
                // Generate QR Code
                generateQRCode(visitorId);
                
                // Show success message
                alert('Visitor registered successfully!\nVisitor ID: ' + visitorId);
            }
        });
    }
    
    // Photo upload handling
    if (photoUpload) {
        photoUpload.addEventListener('click', function() {
            const input = document.createElement('input');
            input.type = 'file';
            input.accept = 'image/*';
            input.onchange = function(e) {
                const file = e.target.files[0];
                if (file) {
                    const reader = new FileReader();
                    reader.onload = function(e) {
                        photoPreview.src = e.target.result;
                        photoPreview.style.display = 'block';
                    };
                    reader.readAsDataURL(file);
                }
            };
            input.click();
        });
    }
});

// Form validation
function validateForm() {
    const required = ['firstName', 'lastName', 'purpose', 'contactNo', 'address'];
    let isValid = true;
    
    required.forEach(field => {
        const input = document.getElementById(field);
        if (input && !input.value.trim()) {
            alert(`Please fill in ${field.replace(/([A-Z])/g, ' $1').toLowerCase()}`);
            isValid = false;
        }
    });
    
    // Validate contact number
    const contactNo = document.getElementById('contactNo');
    if (contactNo && contactNo.value) {
        const phonePattern = /^\+?([0-9]{2})\)?[-. ]?([0-9]{3})[-. ]?([0-9]{3})[-. ]?([0-9]{4})$/;
        if (!phonePattern.test(contactNo.value)) {
            alert('Please enter a valid contact number');
            isValid = false;
        }
    }
    
    return isValid;
}

// Generate Visitor ID
function generateVisitorId() {
    const date = new Date();
    const year = date.getFullYear().toString().substr(-2);
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const random = Math.floor(Math.random() * 9999).toString().padStart(4, '0');
    return `V${year}${month}${random}`;
}

// Generate QR Code
function generateQRCode(visitorId) {
    const qrContainer = document.getElementById('qrCode');
    if (qrContainer) {
        // Here you would typically use a QR code library
        // For now, we'll just show a placeholder
        qrContainer.innerHTML = `
            <div class="qr-placeholder">
                <p>QR Code for ${visitorId}</p>
            </div>
        `;
    }
}

// Clear form
function clearForm() {
    document.getElementById('registrationForm').reset();
    document.getElementById('photoPreview').style.display = 'none';
    document.getElementById('qrCode').innerHTML = '';
}
