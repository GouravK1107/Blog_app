// Improved Login Form Validation
document.addEventListener('DOMContentLoaded', function() {
    const loginForm = document.getElementById("loginForm");
    
    if (!loginForm) return;

    // Add loading state helper
    function setLoading(button, isLoading) {
        if (isLoading) {
            button.disabled = true;
            button.dataset.originalText = button.textContent;
            button.textContent = 'Logging in...';
            button.style.opacity = '0.7';
        } else {
            button.disabled = false;
            button.textContent = button.dataset.originalText || 'Login';
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
    const inputs = loginForm.querySelectorAll('input');
    inputs.forEach(input => {
        input.addEventListener('input', function() {
            clearError(this);
        });
    });

    // Form submission
    loginForm.addEventListener("submit", function(e) {
        const emailInput = document.getElementById("email");
        const passwordInput = document.getElementById("password");
        const submitButton = this.querySelector('button[type="submit"]');
        
        const email = emailInput.value.trim();
        const password = passwordInput.value.trim();
        
        let isValid = true;

        // Clear previous errors
        clearError(emailInput);
        clearError(passwordInput);

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
        if (!password) {
            showError(passwordInput, "Password is required");
            isValid = false;
        }

        if (!isValid) {
            e.preventDefault();
            return;
        }

        // Set loading state (Django will handle the redirect)
        setLoading(submitButton, true);
    });

    // Auto-focus first empty input
    const firstInput = loginForm.querySelector('input[type="email"]');
    if (firstInput && !firstInput.value) {
        firstInput.focus();
    }
});