document.addEventListener('DOMContentLoaded', function() {
    // Display profile information from the server-side data
    if (typeof user !== 'undefined') {
        document.getElementById('emailDisplay').textContent = user.email;
        document.getElementById('nameDisplay').textContent = user.username;
        document.getElementById('securityIdDisplay').textContent = user.security_id;
    }
});

// Update navigation menu active state
document.querySelectorAll('.menu-item').forEach(item => {
    item.addEventListener('click', function() {
        document.querySelectorAll('.menu-item').forEach(i => i.classList.remove('active'));
        this.classList.add('active');
    });
});
