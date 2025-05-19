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
        form.addEventListener('submit', async function(e) {
            e.preventDefault();

            // Get form values
            const role = document.getElementById('role').value;
            const userId = document.getElementById('userId').value;
            const name = document.getElementById('name').value;
            const email = document.getElementById('email').value;
            const password = document.getElementById('password').value;
            const confirmPassword = document.getElementById('confirmPassword').value;

            // 1. Basic validation
            if (!role || !userId || !name || !email || !password || !confirmPassword) {
                alert('Please fill in all fields');
                return;
            }

            // 2. Password validation
            if (password !== confirmPassword) {
                alert('Passwords do not match!');
                return;
            }
            
            if (password.length < 8) {
                alert('Password must be at least 8 characters long');
                return;
            }

            // 3. ID format validation
            const idPatterns = {
                visitor: /^V\d{6}$/,
                department: /^D\d{6}$/,
                security: /^S\d{6}$/
            };

            if (!idPatterns[role]?.test(userId)) {
                alert(`${role.charAt(0).toUpperCase() + role.slice(1)} ID must be in format: ${role[0].toUpperCase()}123456`);
                return;
            }

            // 4. Email validation
            if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
                alert('Please enter a valid email address');
                return;
            }

            try {
                // Show loading state
                const submitButton = form.querySelector('button[type="submit"]');
                const originalText = submitButton.textContent;
                submitButton.disabled = true;
                submitButton.textContent = 'Registering...';

                // 5. Send registration request
                const response = await fetch('/register', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/x-www-form-urlencoded',
                    },
                    body: new URLSearchParams({
                        userId,
                        password,
                        role,
                        name,
                        email
                    })
                });

                const data = await response.json();
                
                if (data.success) {
                    const successMessage = `Account created successfully!\n\nYour details:\nID: ${userId}\nRole: ${role}\nName: ${name}\nEmail: ${email}\n\nPlease remember your ID and password for login.`;
                    alert(successMessage);
                    window.location.href = '/';  // Redirect to login page
                } else {
                    alert(data.message || 'Registration failed. Please try again.');
                }
            } catch (error) {
                console.error('Registration error:', error);
                alert('An error occurred during registration. Please try again.');
            } finally {
                // Reset button state
                const submitButton = form.querySelector('button[type="submit"]');
                submitButton.disabled = false;
                submitButton.textContent = 'Register';
            }
        });
    }
});
