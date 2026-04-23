import { setupAutocompleteFetch, setupSuggestionSelection, fetchOrderName, fetchOrderNumber } from "../shared/utils.js";


function createOrderInputGroup(label, name, placeholder, iconClass, suggestionsClass, url, relatedInput, relatedFetchFn) {
    const group = document.createElement("div");
    group.classList.add("form-group");

    const icon = document.createElement("i");
    icon.classList.add("fas", iconClass);
    icon.style.left = "14px";

    const input = document.createElement("input");
    input.type = "text";
    input.name = name;
    input.classList.add(label);
    input.placeholder = placeholder;
    input.autocomplete = "off";
    input.required = true;

    const suggestionsList = document.createElement("div");
    suggestionsList.classList.add(suggestionsClass, "suggestions-list");

    group.appendChild(icon);
    group.appendChild(input);
    group.appendChild(suggestionsList);

    setupAutocompleteFetch(input, suggestionsList, url);
    setupSuggestionSelection(input, suggestionsList);

    suggestionsList.addEventListener("click", function (event) {
        if (event.target.classList.contains("suggestion")) {
            input.value = event.target.textContent;
            relatedFetchFn(event.target.textContent, relatedInput);
        }
    });

    return { group, input, suggestionsList };
}


export function setupTaskCreation() {
    const addTaskButton = document.getElementById("btn-block-add");
    const tasksContainer = document.getElementById("tasks-container");

    if (!addTaskButton || !tasksContainer) return;

    addTaskButton.addEventListener("click", () => {
        const taskNumber = tasksContainer.querySelectorAll(".task-block").length + 1;

        const taskBlock = document.createElement("div");
        taskBlock.classList.add("task-block");

        const taskTitle = document.createElement("p");
        taskTitle.classList.add("task-block-title");
        taskTitle.innerHTML = `Блок &#8470;${taskNumber}`;
        taskBlock.appendChild(taskTitle);

        const orderName = createOrderInputGroup(
            "order-name", "order_name[]", "Наименование заказа",
            "fa-cogs", "order-name-suggestions", "/orders/names",
            null, () => {}
        );
        taskBlock.appendChild(orderName.group);

        const orderNumber = createOrderInputGroup(
            "order-number", "order_number[]", "Номер заказа",
            "fa-hashtag", "order-number-suggestions", "/orders/numbers",
            orderName.input, fetchOrderName
        );
        taskBlock.appendChild(orderNumber.group);

        orderNumber.suggestionsList.addEventListener("click", function (event) {
            if (event.target.classList.contains("suggestion")) {
                fetchOrderName(event.target.textContent, orderName.input);
            }
        });

        orderName.suggestionsList.addEventListener("click", function (event) {
            if (event.target.classList.contains("suggestion")) {
                fetchOrderNumber(event.target.textContent, orderNumber.input);
            }
        });

        const addWorksButton = document.createElement("button");
        addWorksButton.type = "button";
        addWorksButton.classList.add("default-button", "btn-works-add");
        addWorksButton.innerText = "Добавить работы";

        const deleteButton = document.createElement("button");
        deleteButton.type = "button";
        deleteButton.classList.add("default-button", "btn-block-delete");
        deleteButton.innerText = "Удалить блок";

        const buttonsContainer = document.createElement("div");
        buttonsContainer.classList.add("task-actions");
        buttonsContainer.appendChild(addWorksButton);
        buttonsContainer.appendChild(deleteButton);
        taskBlock.appendChild(buttonsContainer);

        const hr = document.createElement("hr");
        taskBlock.appendChild(hr);

        tasksContainer.appendChild(taskBlock);
    });
}


export function setupTaskDeletion() {
    const modal = document.querySelector(".modal-overlay");
    if (!modal) return;

    const closeButton = modal.querySelector(".modal-close");
    const cancelButton = document.getElementById("cancel-delete-task");
    const confirmButton = document.getElementById("confirm-delete-task");

    if (!closeButton || !cancelButton || !confirmButton) return;

    let taskBlockToDelete = null;
    let formToSubmit = null;

    document.addEventListener("click", (event) => {
        if (event.target.closest(".btn-block-delete")) {
            event.preventDefault();
            taskBlockToDelete = event.target.closest(".task-block");
            formToSubmit = null;
            modal.style.display = "flex";
        }

        if (event.target.closest(".btn-delete")) {
            event.preventDefault();
            formToSubmit = event.target.closest("form");
            taskBlockToDelete = null;
            modal.style.display = "flex";
        }
    });

    const closeModal = () => {
        modal.style.display = "none";
        taskBlockToDelete = null;
        formToSubmit = null;
    };

    closeButton.addEventListener("click", closeModal);
    cancelButton.addEventListener("click", closeModal);

    confirmButton.addEventListener("click", () => {
        if (taskBlockToDelete) {
            taskBlockToDelete.remove();
            document.querySelectorAll(".task-block").forEach((block, index) => {
                const title = block.querySelector(".task-block-title");
                if (title) {
                    title.innerHTML = `Блок &#8470;${index + 1}`;
                }
            });
        }

        if (formToSubmit) {
            formToSubmit.submit();
        }

        closeModal();
    });

    window.addEventListener("click", (event) => {
        if (event.target === modal) closeModal();
    });
}
