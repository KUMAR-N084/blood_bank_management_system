/* ===================================================================
   Blood Bank Management System — Client-Side Validation
   =================================================================== */

document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('main-form');
    if (!form) return;

    // Rules matching Django backend validators
    const nameRegex = /^[A-Za-z .'-]+$/;
    const phoneRegex = /^[0-9()+ -]{7,15}$/;
    const emailRegex = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;

    // Find input fields
    const nameInput = form.querySelector('[name="name"]') || form.querySelector('[name="patient_name"]') || form.querySelector('[name="donor_name"]') || form.querySelector('[name="requester_name"]');
    const phoneInput = form.querySelector('[name="phone"]') || form.querySelector('[name="contact_number"]') || form.querySelector('[name="donor_phone"]');
    const contactInput = form.querySelector('[name="requester_contact"]');
    const emailInput = form.querySelector('[name="email"]') || form.querySelector('[name="contact_email"]') || form.querySelector('[name="donor_email"]');
    const ageInput = form.querySelector('[name="age"]');
    const slotInput = form.querySelector('[name="slot"]');

    // Register real-time listeners
    if (nameInput) nameInput.addEventListener('input', () => validateName(nameInput));
    if (phoneInput) phoneInput.addEventListener('input', () => validatePhone(phoneInput));
    if (contactInput) contactInput.addEventListener('input', () => validateContact(contactInput));
    if (emailInput) emailInput.addEventListener('input', () => validateEmail(emailInput));
    if (ageInput) ageInput.addEventListener('input', () => validateAge(ageInput));
    if (slotInput) slotInput.addEventListener('change', () => validateSlot(slotInput));

    // Form submit listener
    form.addEventListener('submit', function(e) {
        let isValid = true;

        if (nameInput && !validateName(nameInput)) isValid = false;
        if (phoneInput && !validatePhone(phoneInput)) isValid = false;
        if (contactInput && !validateContact(contactInput)) isValid = false;
        if (emailInput && !validateEmail(emailInput)) isValid = false;
        if (ageInput && !validateAge(ageInput)) isValid = false;
        if (slotInput && !validateSlot(slotInput)) isValid = false;


        // General validation of other required fields
        form.querySelectorAll('[required]').forEach(function(el) {
            if (!el.value.trim()) {
                showError(el, 'This field is required.');
                isValid = false;
            }
        });

        if (!isValid) {
            e.preventDefault();
            // Scroll to the first error
            const firstError = form.querySelector('.is-invalid');
            if (firstError) {
                firstError.scrollIntoView({ behavior: 'smooth', block: 'center' });
                firstError.focus();
            }
        }
    });

    // --- Helper Validation Functions ---

    function showError(el, message) {
        el.classList.remove('is-valid');
        el.classList.add('is-invalid');
        
        let feedback = el.parentNode.querySelector('.field-error');
        if (!feedback) {
            feedback = document.createElement('div');
            feedback.className = 'field-error';
            el.parentNode.appendChild(feedback);
        }
        feedback.innerHTML = `<i class="bi bi-exclamation-circle"></i> ${message}`;
    }

    function showSuccess(el) {
        el.classList.remove('is-invalid');
        el.classList.add('is-valid');
        const feedback = el.parentNode.querySelector('.field-error');
        if (feedback) {
            feedback.remove();
        }
    }

    function validateName(el) {
        const val = el.value.trim();
        if (el.hasAttribute('required') && !val) {
            showError(el, 'Name is required.');
            return false;
        }
        if (val && !nameRegex.test(val)) {
            showError(el, 'Enter a valid name (letters, spaces, dots, hyphens only).');
            return false;
        }
        showSuccess(el);
        return true;
    }

    function validatePhone(el) {
        const val = el.value.trim();
        if (el.hasAttribute('required') && !val) {
            showError(el, 'Phone number is required.');
            return false;
        }
        if (val && !phoneRegex.test(val)) {
            showError(el, 'Enter a valid phone number (7-15 digits, may include + - parentheses).');
            return false;
        }
        showSuccess(el);
        return true;
    }

    function validateContact(el) {
        const val = el.value.trim();
        if (el.hasAttribute('required') && !val) {
            showError(el, 'Contact information is required.');
            return false;
        }
        if (val && !emailRegex.test(val) && !phoneRegex.test(val)) {
            showError(el, 'Enter a valid email address or phone number (7-15 digits).');
            return false;
        }
        showSuccess(el);
        return true;
    }

    function validateEmail(el) {
        const val = el.value.trim();
        if (el.hasAttribute('required') && !val) {
            showError(el, 'Email address is required.');
            return false;
        }
        if (val && !emailRegex.test(val)) {
            showError(el, 'Enter a valid email address.');
            return false;
        }
        showSuccess(el);
        return true;
    }

    function validateAge(el) {
        const val = el.value.trim();
        if (el.hasAttribute('required') && !val) {
            showError(el, 'Age is required.');
            return false;
        }
        if (val) {
            const age = parseInt(val, 10);
            if (isNaN(age) || age < 18 || age > 100) {
                showError(el, 'Age must be between 18 and 100.');
                return false;
            }
        }
        showSuccess(el);
        return true;
    }

    function validateSlot(el) {
        const val = el.value.trim();
        if (el.hasAttribute('required') && !val) {
            showError(el, 'Appointment time is required.');
            return false;
        }
        if (val) {
            const chosenDate = new Date(val);
            const now = new Date();
            if (chosenDate <= now) {
                showError(el, 'Please choose a future date and time for the appointment.');
                return false;
            }
        }
        showSuccess(el);
        return true;
    }
});
