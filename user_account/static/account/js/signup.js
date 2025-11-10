// Improved Signup Form Validation
document.addEventListener('DOMContentLoaded', function() {
    const signupForm = document.getElementById("signupForm");
    
    if (!signupForm) return;

    // Add loading state helper
    function setLoading(button, isLoading) {
        if (isLoading) {
            button.disabled = true;
            button.dataset.originalText = button.textContent;
            button.textContent = 'Creating account...';
            button.style.opacity = '0.7';
        } else {
            button.disabled = false;
            button.textContent = button.dataset.originalText || 'Create Account';
            button.style.opacity = '1';
        }
    }

    // Show error message below input
    function showError(input, message) {
        // Remove existing error
        const existingError = input.parentElement.querySelector('.error-message');
        if (existingError) existingError.remove();

        // Create new error message
        const errorDiv = document.createElement('div');
        errorDiv.className = 'error-message';
        errorDiv.style.color = '#dc2626';
        errorDiv.style.fontSize = '0.875rem';
        errorDiv.style.marginTop = '0.25rem';
        errorDiv.textContent = message;
        
        input.style.borderColor = '#fca5a5';
        input.parentElement.appendChild(errorDiv);
    }

    // Clear error message
    function clearError(input) {
        const errorDiv = input.parentElement.querySelector('.error-message');
        if (errorDiv) errorDiv.remove();
        input.style.borderColor = '#e0e0e0';
    }

    // Clear errors on input
    const inputs = signupForm.querySelectorAll('input');
    inputs.forEach(input => {
        input.addEventListener('input', function() {
            clearError(this);
        });
    });

    // Real-time password match indicator
    const password1Input = document.getElementById("password1");
    const password2Input = document.getElementById("password2");

    password2Input.addEventListener('input', function() {
        if (this.value && password1Input.value) {
            if (this.value === password1Input.value) {
                this.style.borderColor = '#86efac';
                clearError(this);
            } else {
                this.style.borderColor = '#fca5a5';
            }
        }
    });

    // Form submission
    signupForm.addEventListener("submit", function(e) {
        const usernameInput = document.getElementById("username");
        const emailInput = document.getElementById("email");
        const submitButton = this.querySelector('button[type="submit"]');
        
        const username = usernameInput.value.trim();
        const email = emailInput.value.trim();
        const pass1 = password1Input.value;
        const pass2 = password2Input.value;
        
        let isValid = true;

        // Clear previous errors
        clearError(usernameInput);
        clearError(emailInput);
        clearError(password1Input);
        clearError(password2Input);

        // Validate username
        if (!username) {
            showError(usernameInput, "Username is required");
            isValid = false;
        } else if (username.length < 3) {
            showError(usernameInput, "Username must be at least 3 characters");
            isValid = false;
        } else if (!/^[a-zA-Z0-9_]+$/.test(username)) {
            showError(usernameInput, "Username can only contain letters, numbers, and underscores");
            isValid = false;
        }

        // Validate email
        if (!email) {
            showError(emailInput, "Email is required");
            isValid = false;
        } else {
            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            if (!emailRegex.test(email)) {
                showError(emailInput, "Please enter a valid email address");
                isValid = false;
            }
        }

        // Validate password
        if (!pass1) {
            showError(password1Input, "Password is required");
            isValid = false;
        } else if (pass1.length < 8) {
            showError(password1Input, "Password must be at least 8 characters");
            isValid = false;
        } else if (!/(?=.*[a-z])(?=.*[A-Z])(?=.*\d)/.test(pass1)) {
            showError(password1Input, "Password must contain uppercase, lowercase, and a number");
            isValid = false;
        }

        // Validate password confirmation
        if (!pass2) {
            showError(password2Input, "Please confirm your password");
            isValid = false;
        } else if (pass1 !== pass2) {
            showError(password2Input, "Passwords do not match");
            isValid = false;
        }

        if (!isValid) {
            e.preventDefault();
            return;
        }

        // Set loading state (Django will handle the redirect)
        setLoading(submitButton, true);
    });

    // Auto-focus first input
    const firstInput = signupForm.querySelector('input[type="text"]');
    if (firstInput && !firstInput.value) {
        firstInput.focus();
    }

    // Password strength indicator (optional visual feedback)
    password1Input.addEventListener('input', function() {
        const password = this.value;
        const hasUpper = /[A-Z]/.test(password);
        const hasLower = /[a-z]/.test(password);
        const hasNumber = /\d/.test(password);
        const hasLength = password.length >= 8;

        // Visual feedback without blocking submission
        if (password && hasUpper && hasLower && hasNumber && hasLength) {
            this.style.borderColor = '#86efac';
        } else if (password) {
            this.style.borderColor = '#fbbf24';
        }
    });
});