document.addEventListener('DOMContentLoaded', function() {
    loadProfileData();
});

function loadProfileData() {
    // Load profile data from localStorage or use default data
    const profileData = JSON.parse(localStorage.getItem('securityProfile')) || {
        email: 'security@lspu.edu.ph',
        name: 'John Doe',
        securityId: 'SEC-2025-001',
    };

    // Display profile information
    document.getElementById('emailDisplay').textContent = profileData.email;
    document.getElementById('nameDisplay').textContent = profileData.name;
    document.getElementById('securityIdDisplay').textContent = profileData.securityId;
}

function saveProfile() {
    // Get form values
    const email = document.getElementById('email').value;
    const name = document.getElementById('name').value;
    const securityId = document.getElementById('securityId').value;
    const phone = document.getElementById('phone').value;
    const shift = document.getElementById('shift').value;
    const department = document.getElementById('department').value;
    const password = document.getElementById('password').value;
    const confirmPassword = document.getElementById('confirmPassword').value;

    // Validate required fields
    if (!email || !name || !securityId) {
        alert('Please fill in all required fields');
        return;
    }

    // Validate email format
    if (!isValidEmail(email)) {
        alert('Please enter a valid email address');
        return;
    }

    // Validate password if changing
    if (password || confirmPassword) {
        if (password !== confirmPassword) {
            alert('Passwords do not match');
            return;
        }
        if (password.length < 6) {
            alert('Password must be at least 6 characters long');
            return;
        }
    }

    // Save profile data
    const profileData = {
        email,
        name,
        securityId,
        phone,
        shift,
        department,
    };

    localStorage.setItem('securityProfile', JSON.stringify(profileData));

    // Show success message
    alert('Profile updated successfully');

    // Clear password fields
    document.getElementById('password').value = '';
    document.getElementById('confirmPassword').value = '';
}

function resetForm() {
    if (confirm('Are you sure you want to reset the form? All unsaved changes will be lost.')) {
        loadProfileData();
        document.getElementById('password').value = '';
        document.getElementById('confirmPassword').value = '';
    }
}

function isValidEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}

// Update navigation menu active state
document.querySelectorAll('.menu-item').forEach(item => {
    item.addEventListener('click', function() {
        document.querySelectorAll('.menu-item').forEach(i => i.classList.remove('active'));
        this.classList.add('active');
    });
});
