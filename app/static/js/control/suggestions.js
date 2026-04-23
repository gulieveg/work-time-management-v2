import { configureAutocompleteBySelector, fetchRelatedFieldValue } from "../shared/utils.js";


export function setupAutocompleteInputs() {
    const inputConfigs = [
        { input: ".order-name", suggestions: ".order-name-suggestions", url: "/control/orders/names" },
        { input: ".order-number", suggestions: ".order-number-suggestions", url: "/control/orders/numbers" },
        { input: ".user-name", suggestions: ".user-name-suggestions", url: "/control/users/names" },
        { input: ".user-login", suggestions: ".user-login-suggestions", url: "/control/users/logins" },
        { input: ".employee-name", suggestions: ".employee-name-suggestions", url: "/control/employees/names" },
        { input: ".personnel-number", suggestions: ".personnel-number-suggestions", url: "/control/employees/numbers" },
        { input: ".work-name", suggestions: ".work-name-suggestions", url: "/control/works/names" },
    ];

    inputConfigs.forEach(config => {
        if (document.querySelector(config.input) && document.querySelector(config.suggestions)) {
            configureAutocompleteBySelector(config.input, config.suggestions, config.url);
        }
    });
}


export function setupSuggestionSync(configs) {
    configs.forEach(cfg => {
        const input = document.querySelector(cfg.inputSelector);
        const suggestions = document.querySelector(cfg.suggestionsSelector);
        const targetInput = cfg.updateTarget ? document.querySelector(cfg.updateTarget.inputSelector) : null;

        if (input && suggestions) {
            suggestions.addEventListener("click", event => {
                if (event.target.classList.contains("suggestion")) {
                    const selectedValue = event.target.textContent;

                    if (targetInput) {
                        fetchRelatedFieldValue(
                            cfg.resourceType,
                            selectedValue,
                            targetInput,
                            cfg.updateTarget.fieldName,
                            cfg.updateTarget.urlPart
                        );
                    }
                }
            });
        }
    });
}
