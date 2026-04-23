import { configureAutocompleteInput, fetchOrderName, fetchOrderNumber } from "../shared/utils.js";


export function setupAutocompleteInputs() {
    const inputConfigs = [
        { input: ".employee-search", suggestions: ".employee-search-suggestions", url: "/employees" },
        { input: ".order-name", suggestions: ".order-name-suggestions", url: "/orders/names" },
        { input: ".order-number", suggestions: ".order-number-suggestions", url: "/orders/numbers" },
    ];

    inputConfigs.forEach(config => {
        const inputs = document.querySelectorAll(config.input);
        const suggestions = document.querySelectorAll(config.suggestions);

        for (let i = 0; i < inputs.length; i++) {
            configureAutocompleteInput(inputs[i], suggestions[i], config.url);
        }
    });
}


export function setupOrderSuggestionSync() {
    const orderNameInputs = document.querySelectorAll(".order-name");
    const orderNumberInputs = document.querySelectorAll(".order-number");
    const orderNameSuggestionsLists = document.querySelectorAll(".order-name-suggestions");
    const orderNumberSuggestionsLists = document.querySelectorAll(".order-number-suggestions");

    for (let i = 0; i < orderNameInputs.length; i++) {
        const orderNameInput = orderNameInputs[i];
        const orderNumberInput = orderNumberInputs[i];
        const orderNameSuggestions = orderNameSuggestionsLists[i];
        const orderNumberSuggestions = orderNumberSuggestionsLists[i];

        orderNameSuggestions.addEventListener("click", function (event) {
            if (event.target.classList.contains("suggestion")) {
                orderNameInput.value = event.target.textContent;
                fetchOrderNumber(event.target.textContent, orderNumberInput);
            }
        });

        orderNumberSuggestions.addEventListener("click", function (event) {
            if (event.target.classList.contains("suggestion")) {
                orderNumberInput.value = event.target.textContent;
                fetchOrderName(event.target.textContent, orderNameInput);
            }
        });
    }
}
