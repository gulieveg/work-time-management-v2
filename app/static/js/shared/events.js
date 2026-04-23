export function setupFlashMessageAutoHide(delayMs = 8000) {
    const toast = document.getElementById("message");
    if (toast) {
        setTimeout(() => {
            toast.classList.add("hiding");
            toast.addEventListener("animationend", () => toast.remove(), { once: true });
        }, delayMs);
    }
}


export function setupSuggestionListClose(selectors) {
    const selectorString = selectors.join(", ");

    document.addEventListener("click", function (event) {
        document.querySelectorAll(selectorString).forEach(suggestionsList => {
            const inputElement = suggestionsList.previousElementSibling;
            const clickedInsideInput = inputElement && inputElement.contains(event.target);
            const clickedInsideSuggestions = suggestionsList.contains(event.target);

            if (!clickedInsideInput && !clickedInsideSuggestions) {
                suggestionsList.style.display = "none";
            }
        });

        const dropdown = document.querySelector(".dropdown");
        const toggle = document.getElementById("toggle-dropdown");

        if (!dropdown || !toggle) return;

        if (!dropdown.contains(event.target)) {
            toggle.checked = false;
        }
    });

    document.addEventListener("keydown", function (event) {
        if (event.key !== "Escape") return;

        document.querySelectorAll(selectorString).forEach(suggestionsList => {
            if (document.body.contains(suggestionsList)) {
                suggestionsList.style.display = "none";
            }
        });

        const toggle = document.getElementById("toggle-dropdown");
        if (toggle && toggle.checked) {
            toggle.checked = false;
        }
    });
}


export function setupFilterResetHandler() {
    document.addEventListener("click", function (event) {
        const resetButton = event.target.closest(".btn-filters-reset");
        if (!resetButton) return;

        const form = resetButton.closest("form");
        if (!form) return;

        const inputs = form.querySelectorAll("input[type='text'], input[type='number'], input[type='date']");
        inputs.forEach(input => input.value = "");

        const departmentCheckboxes = form.querySelectorAll(".dropdown-content input[type='checkbox'][name='departments[]']");
        departmentCheckboxes.forEach(checkbox => {
            checkbox.checked = false;
        });

        const selectedText = form.querySelector("#dropdown-selected-text");
        if (selectedText) {
            selectedText.textContent = "Все";
        }

        const toggleCheckbox = form.querySelector("#toggle-dropdown");
        if (toggleCheckbox) {
            toggleCheckbox.checked = false;
        }
    });
}


export function setupPasswordToggle() {
    const togglePasswords = document.querySelectorAll(".toggle-password");

    togglePasswords.forEach(toggle => {
        toggle.addEventListener("click", function () {
            const passwordInput = this.previousElementSibling;

            if (passwordInput && (passwordInput.type === "password" || passwordInput.type === "text")) {
                const type = passwordInput.type === "password" ? "text" : "password";
                passwordInput.type = type;
                this.classList.toggle("fa-eye");
                this.classList.toggle("fa-eye-slash");
            }
        });
    });
}


export function setupScrollToTopButton() {
    const scrollButton = document.querySelector(".btn-scroll-top");

    if (scrollButton) {
        window.addEventListener("scroll", function () {
            scrollButton.style.display = window.scrollY > 400 ? "block" : "none";
        });

        scrollButton.addEventListener("click", function () {
            window.scrollTo({ top: 0, behavior: "smooth" });
        });
    }
}


export function setupHoursSelection() {
    const hours = document.querySelectorAll(".hours");
    const hoursTotal = document.querySelector(".hours-sum");
    const resetButton = document.querySelector(".btn-hours-reset");
    const hoursTotalContainer = document.querySelector(".hours-summary");

    if (!hoursTotal || !resetButton || !hoursTotalContainer || hours.length === 0) return;

    function updateSum() {
        let sum = 0;
        let selectedCount = 0;

        hours.forEach(cell => {
            if (cell.classList.contains("selected")) {
                sum += parseFloat(cell.dataset.hours) || 0;
                selectedCount++;
            }
        });

        hoursTotal.textContent = sum.toFixed(2);
        hoursTotalContainer.style.display = selectedCount > 0 ? "flex" : "none";
    }

    hours.forEach(cell => {
        cell.style.cursor = "pointer";
        cell.addEventListener("click", () => {
            cell.classList.toggle("selected");
            updateSum();
        });
    });

    resetButton.addEventListener("click", () => {
        hours.forEach(cell => cell.classList.remove("selected"));
        updateSum();
    });
}


export function setupDropdownCheckboxListener(dropdownId, displayId, defaultText = "Все") {
    const checkboxes = document.querySelectorAll(`#${dropdownId} input[type="checkbox"]`);
    const displayText = document.getElementById(displayId);

    if (displayText) {
        function updateDisplay() {
            const selected = Array.from(checkboxes)
                .filter(cb => cb.checked)
                .map(cb => cb.value);
            displayText.textContent = selected.length ? selected.join(", ") : defaultText;
        }

        checkboxes.forEach(cb => cb.addEventListener("change", updateDisplay));
        updateDisplay();
    }
}
