document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('registrationForm');
    const roleSelect = document.getElementById('role');

    // Handle role selection change
    if (roleSelect) {
        roleSelect.addEventListener('change', function() {
            const userId = document.getElementById('userId');
            switch (this.value) {
                case 'visitor':
                    userId.placeholder = 'Visitor ID (e.g., V123456)';
                    break;
                case 'department':
                    userId.placeholder = 'Department ID (e.g., D123456)';
                    break;
                case 'security':
                    userId.placeholder = 'Security ID (e.g., S123456)';
                    break;
                default:
                    userId.placeholder = 'Enter your ID';
            }
        });
    }

    // Handle form submission
    if (form) {
        form.addEventListener('submit', function(e) {
            e.preventDefault();

            const role = document.getElementById('role').value;
            const userId = document.getElementById('userId').value;
            const name = document.getElementById('name').value;
            const email = document.getElementById('email').value;
            const password = document.getElementById('password').value;
            const confirmPassword = document.getElementById('confirmPassword').value;

            // Basic validation
            if (!role || !userId || !name || !email || !password || !confirmPassword) {
                alert('Please fill in all fields');
                return;
            }

            if (password !== confirmPassword) {
                alert('Passwords do not match!');
                return;
            }

            if (password.length < 8) {
                alert('Password must be at least 8 characters long');
                return;
            }

            // ID format validation
            let idPattern;
            switch (role) {
                case 'visitor':
                    idPattern = /^V\d{6}$/;
                    break;
                case 'department':
                    idPattern = /^D\d{6}$/;
                    break;
                case 'security':
                    idPattern = /^S\d{6}$/;
                    break;
            }

            if (!idPattern.test(userId)) {
                alert(`${role.charAt(0).toUpperCase() + role.slice(1)} ID must be in format: ${role[0].toUpperCase()}123456`);
                return;
            }

            // Email validation
            if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
                alert('Please enter a valid email address');
                return;
            }

            // Send registration request
            fetch('/register', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                },
                body: new URLSearchParams({
                    userId: userId,
                    password: password,
                    role: role,
                    name: name,
                    email: email
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    alert('Registration successful! Please log in.');
                    window.location.href = '/';  // Redirect to login page
                } else {
                    alert(data.message || 'Registration failed. Please try again.');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('An error occurred during registration. Please try again.');
            });
        });
    }
});
