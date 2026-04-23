import { setupFilterResetHandler, setupPasswordToggle } from "../shared/events.js";


export function setupPasswordSwitchHandler() {
    const passwordSwitch = document.getElementById("password-toggle-switch");
    const passwordField = document.getElementById("password-input-group");

    if (!passwordSwitch || !passwordField) return;

    const passwordInput = passwordField.querySelector("input[name='user_password']");
    if (!passwordInput) return;

    passwordSwitch.addEventListener("change", function() {
        const enabled = passwordSwitch.checked;
        passwordField.style.display = enabled ? "block" : "none";

        if (enabled) {
            passwordInput.setAttribute("required", "required");
        } else {
            passwordInput.removeAttribute("required");
            passwordInput.value = "";
        }
    });
}


export function setupUserStatusSwitchHandler() {
    const switches = document.querySelectorAll(".user-active-toggle");

    switches.forEach(switchEl => {
        switchEl.addEventListener("change", function() {
            const isActive = this.checked;
            const userId = this.dataset.userId;

            fetch(`/control/users/update_user_status/${userId}`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ is_active: isActive })
            })
            .then(response => response.json())
            .then(data => console.log(data));
        });
    });
}


export function setupConfirmationModal() {
    const confirmationTexts = {
        "delete-user": { message: "Вы уверены, что хотите удалить пользователя?", button: "Удалить" },
        "reset-user-password": { message: "Вы уверены, что хотите сбросить пароль пользователя?", button: "Сбросить" },
        "delete-order": { message: "Вы уверены, что хотите удалить заказ?", button: "Удалить" },
        "delete-employee": { message: "Вы уверены, что хотите удалить работника?", button: "Удалить" },
        "delete-work": { message: "Вы уверены, что хотите удалить работу?", button: "Удалить" },
        "delete-hours": { message: "Вы уверены, что хотите удалить часы?", button: "Удалить" },
    };

    const modal = document.getElementById("modal-confirm-dialog");
    if (!modal) return;

    const modalTextElem = modal.querySelector("#modal-confirm-message");
    const closeButton = modal.querySelector(".modal-close");
    const cancelButton = modal.querySelector("#modal-cancel");
    const confirmButton = modal.querySelector("#modal-confirm");

    if (!modalTextElem || !closeButton || !cancelButton || !confirmButton) return;

    let formToSubmit = null;

    document.addEventListener("click", (event) => {
        const actionButton = event.target.closest("[data-action]");
        if (!actionButton) return;

        event.preventDefault();
        formToSubmit = actionButton.closest("form");

        const actionType = actionButton.dataset.action;
        const textConfig = confirmationTexts[actionType];
        if (!textConfig) return;

        modalTextElem.textContent = textConfig.message;
        confirmButton.textContent = textConfig.button;
        modal.style.display = "flex";
    });

    const closeModal = () => {
        modal.style.display = "none";
        formToSubmit = null;
    };

    closeButton.addEventListener("click", closeModal);
    cancelButton.addEventListener("click", closeModal);
    window.addEventListener("click", (event) => {
        if (event.target === modal) closeModal();
    });

    confirmButton.addEventListener("click", () => {
        if (formToSubmit) formToSubmit.submit();
        closeModal();
    });
}


export function setupControlFilterResetHandler() {
    setupFilterResetHandler();
}


export function setupControlPasswordToggle() {
    setupPasswordToggle();
}


export function setupDropdownSelector() {
    document.querySelectorAll(".dropdown").forEach(dropdown => {
        const hiddenInput = dropdown.querySelector("input[type='hidden']");
        const labelText = dropdown.querySelector(".dropdown-label span");
        const options = dropdown.querySelectorAll(".dropdown-content label");
        const toggleCheckbox = dropdown.querySelector("input[type='checkbox']");

        if (!hiddenInput || !labelText || !options.length || !toggleCheckbox) return;

        options.forEach(option => {
            option.addEventListener("click", () => {
                hiddenInput.value = option.getAttribute("data-value");
                labelText.textContent = option.textContent;
                labelText.classList.add("selected");
                toggleCheckbox.checked = false;
            });
        });

        document.addEventListener("click", (event) => {
            if (!dropdown.contains(event.target)) {
                toggleCheckbox.checked = false;
            }
        });

        document.addEventListener("keydown", (event) => {
            if (event.key === "Escape") {
                toggleCheckbox.checked = false;
            }
        });
    });
}


export function setupFileUpload() {
    const container = document.querySelector(".file-input-group");
    if (!container) return;

    const fileInput = container.querySelector(".file-input");
    const fileLabel = container.querySelector(".file-input-label");
    const uploadButton = container.querySelector(".btn-file-choose");
    const removeButton = container.querySelector(".btn-file-remove");

    uploadButton.addEventListener("click", () => fileInput.click());

    fileInput.addEventListener("change", () => {
        if (fileInput.files.length > 0) {
            fileLabel.textContent = fileInput.files[0].name;
            if (removeButton) removeButton.style.display = "inline-block";
        } else {
            fileLabel.textContent = "Таблица не выбрана";
            if (removeButton) removeButton.style.display = "none";
        }
    });

    if (removeButton) {
        removeButton.addEventListener("click", () => {
            fileInput.value = "";
            fileLabel.textContent = "Таблица не выбрана";
            removeButton.style.display = "none";
        });
    }
}


export function setupWorkListManagement() {
    const tabButtons = document.querySelectorAll(".sub-tab");
    const tabPanels = document.querySelectorAll(".tab-panel");
    const tbody = document.getElementById("works-body");
    const addRowButton = document.getElementById("btn-row-add");

    if (!tabButtons.length || !tabPanels.length || !tbody || !addRowButton) return;

    tabButtons.forEach(button => {
        button.addEventListener("click", () => {
            tabButtons.forEach(btn => btn.classList.remove("active"));
            tabPanels.forEach(panel => panel.classList.remove("active"));

            button.classList.add("active");
            const targetPanel = document.getElementById(button.dataset.tab);
            if (targetPanel) {
                targetPanel.classList.add("active");
            }
        });
    });

    tbody.addEventListener("click", event => {
        const deleteRowButton = event.target.closest(".btn-row-delete");
        if (deleteRowButton) {
            deleteRowButton.closest("tr").remove();
        }
    });

    addRowButton.addEventListener("click", () => {
        const newRow = document.createElement("tr");
        newRow.innerHTML = `
            <td><input type="text" name="work_name[]" autocomplete="off" required></td>
            <td><input type="text" name="work_planned_hours[]" autocomplete="off" required></td>
            <td><button type="button" class="btn-row-delete">&times;</button></td>
        `;
        tbody.appendChild(newRow);
    });
}
