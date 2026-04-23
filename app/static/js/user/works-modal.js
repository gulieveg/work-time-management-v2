function setupWorksModal() {
    const modal = document.querySelector(".works-modal-overlay");
    if (!modal) return;

    const tbody = modal.querySelector("tbody");
    const modalTitle = modal.querySelector("#works-modal-heading");
    const hiddenContainer = document.querySelector("#hidden-work-hours-container");

    document.addEventListener("click", function (event) {
        if (event.target.classList.contains("btn-works-add")) {
            openWorksModal(event.target.closest(".task-block"), modal, tbody, modalTitle, hiddenContainer);
            return;
        }

        if (event.target.classList.contains("works-modal-close") || event.target.closest(".works-modal-close")) {
            modal.style.display = "none";
            return;
        }

        if (event.target === modal) {
            modal.style.display = "none";
        }
    });

    document.addEventListener("keydown", function (event) {
        if (event.key === "Escape" && modal.style.display === "block") {
            modal.style.display = "none";
        }
    });

    const saveWorksButton = document.querySelector("#save-works");
    if (saveWorksButton) {
        saveWorksButton.addEventListener("click", function () {
            modal.style.display = "none";
        });
    }
}


function openWorksModal(taskBlock, modal, tbody, modalTitle, hiddenContainer) {
    const orderNameInput = taskBlock.querySelector(".order-name");
    const orderNumberInput = taskBlock.querySelector(".order-number");

    const orderName = orderNameInput.value.trim();
    const orderNumber = orderNumberInput.value.trim();

    orderNameInput.classList.remove("input-invalid");
    orderNumberInput.classList.remove("input-invalid");
    void orderNameInput.offsetWidth;
    void orderNumberInput.offsetWidth;

    let hasError = false;
    if (!orderName) {
        orderNameInput.classList.add("input-invalid");
        hasError = true;
    }
    if (!orderNumber) {
        orderNumberInput.classList.add("input-invalid");
        hasError = true;
    }
    if (hasError) {
        if (!orderName) orderNameInput.focus();
        else if (!orderNumber) orderNumberInput.focus();
        return;
    }

    fetch(`/orders/${orderNumber}/works`)
        .then(response => response.json())
        .then(data => {
            modalTitle.textContent = `Заказ №${orderNumber}`;
            tbody.innerHTML = "";

            data.forEach(work => {
                const hiddenInputName = `work_hours[${orderNumber}][${work.work_name}]`;
                let existingInput = hiddenContainer.querySelector(`input[name="${CSS.escape(hiddenInputName)}"]`);

                if (!existingInput) {
                    existingInput = document.createElement("input");
                    existingInput.type = "hidden";
                    existingInput.name = hiddenInputName;
                    hiddenContainer.appendChild(existingInput);
                }

                const value = existingInput.value || "";

                const row = document.createElement("tr");
                row.innerHTML = `
                    <td style="width: 280px;">${work.work_name}</td>
                    <td>${work.planned_hours}</td>
                    <td>${work.spent_hours}</td>
                    <td>${work.remaining_hours}</td>
                    <td>
                        <input
                            style="height: 18px; width: 140px; padding-left: 4px;"
                            type="number"
                            name="work_hours[${orderNumber}][${work.work_name}]"
                            min="0"
                            max="12.25"
                            step="0.01"
                            value="${value}"
                        />
                    </td>
                `;

                row.querySelector("input").addEventListener("input", event => {
                    existingInput.value = event.target.value;
                });

                tbody.appendChild(row);
            });

            modal.style.display = "block";
        });
}


export function initWorksModal() {
    setupWorksModal();
}
