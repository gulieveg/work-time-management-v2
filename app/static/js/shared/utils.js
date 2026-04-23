export function setupAutocompleteFetch(inputElement, suggestionsList, url) {
    inputElement.addEventListener("input", function () {
        const query = inputElement.value;

        if (query.length >= 2) {
            fetch(`${url}?query=${query}`)
                .then(response => response.json())
                .then(data => {
                    suggestionsList.innerHTML = "";
                    if (data.length > 0) {
                        suggestionsList.style.display = "block";
                        data.forEach(item => {
                            const suggestion = document.createElement("div");
                            suggestion.classList.add("suggestion");
                            suggestion.textContent = item;
                            suggestionsList.appendChild(suggestion);
                        });
                    } else {
                        suggestionsList.style.display = "none";
                    }
                })
                .catch(error => console.error("Failed to retrieve data:", error));
        } else {
            suggestionsList.style.display = "none";
        }
    });
}


export function setupSuggestionSelection(inputElement, suggestionsList) {
    suggestionsList.addEventListener("click", function (event) {
        if (event.target.classList.contains("suggestion")) {
            inputElement.value = event.target.textContent;
            suggestionsList.style.display = "none";
        }
    });
}


export function configureAutocompleteInput(inputElement, suggestionsList, url) {
    if (inputElement && suggestionsList) {
        setupAutocompleteFetch(inputElement, suggestionsList, url);
        setupSuggestionSelection(inputElement, suggestionsList);
    }
}


export function configureAutocompleteBySelector(inputSelector, suggestionsListSelector, url) {
    const inputElement = document.querySelector(inputSelector);
    const suggestionsList = document.querySelector(suggestionsListSelector);

    if (inputElement && suggestionsList) {
        setupAutocompleteFetch(inputElement, suggestionsList, url);
        setupSuggestionSelection(inputElement, suggestionsList);
    }
}


export function fetchRelatedFieldValue(resourceType, value, inputElement, fieldName, urlPart) {
    fetch(`/control/${encodeURIComponent(resourceType)}/${encodeURIComponent(value)}/${encodeURIComponent(urlPart)}`)
        .then(response => response.json())
        .then(data => {
            if (data[fieldName]) {
                inputElement.value = data[fieldName];
            }
        });
}


export function fetchOrderName(orderNumber, orderNameInput) {
    fetch(`/orders/${encodeURIComponent(orderNumber)}/name`)
        .then(response => response.json())
        .then(data => {
            if (data.order_name) {
                orderNameInput.value = data.order_name;
            }
        });
}


export function fetchOrderNumber(orderName, orderNumberInput) {
    fetch(`/orders/${encodeURIComponent(orderName)}/number`)
        .then(response => response.json())
        .then(data => {
            if (data.order_number) {
                orderNumberInput.value = data.order_number;
            }
        });
}
