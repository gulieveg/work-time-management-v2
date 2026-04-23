import {
    setupFlashMessageAutoHide,
    setupSuggestionListClose
} from "../shared/events.js";
import {
    setupPasswordSwitchHandler,
    setupUserStatusSwitchHandler,
    setupConfirmationModal,
    setupControlFilterResetHandler,
    setupControlPasswordToggle,
    setupDropdownSelector,
    setupFileUpload,
    setupWorkListManagement
} from "./events.js";
import { setupAutocompleteInputs, setupSuggestionSync } from "./suggestions.js";


const CONTROL_SUGGESTION_SELECTORS = [
    ".order-name-suggestions",
    ".order-number-suggestions",
    ".user-name-suggestions",
    ".user-login-suggestions",
    ".employee-name-suggestions",
    ".personnel-number-suggestions",
    ".work-name-suggestions",
];


const SUGGESTION_SYNC_CONFIGS = [
    {
        inputSelector: ".order-name",
        suggestionsSelector: ".order-name-suggestions",
        resourceType: "orders",
        urlPart: "name",
        updateTarget: {
            inputSelector: ".order-number",
            fieldName: "order_number",
            urlPart: "number"
        }
    },
    {
        inputSelector: ".order-number",
        suggestionsSelector: ".order-number-suggestions",
        resourceType: "orders",
        urlPart: "number",
        updateTarget: {
            inputSelector: ".order-name",
            fieldName: "order_name",
            urlPart: "name"
        }
    },
    {
        inputSelector: ".user-login",
        suggestionsSelector: ".user-login-suggestions",
        resourceType: "users",
        urlPart: "login",
        updateTarget: {
            inputSelector: ".user-name",
            fieldName: "user_name",
            urlPart: "name"
        }
    },
    {
        inputSelector: ".user-name",
        suggestionsSelector: ".user-name-suggestions",
        resourceType: "users",
        urlPart: "name",
        updateTarget: {
            inputSelector: ".user-login",
            fieldName: "user_login",
            urlPart: "login"
        }
    },
    {
        inputSelector: ".employee-name",
        suggestionsSelector: ".employee-name-suggestions",
        resourceType: "employees",
        urlPart: "name",
        updateTarget: {
            inputSelector: ".personnel-number",
            fieldName: "personnel_number",
            urlPart: "number"
        }
    },
    {
        inputSelector: ".personnel-number",
        suggestionsSelector: ".personnel-number-suggestions",
        resourceType: "employees",
        urlPart: "number",
        updateTarget: {
            inputSelector: ".employee-name",
            fieldName: "employee_name",
            urlPart: "name"
        }
    },
];


function initControlPanel() {
    setupFlashMessageAutoHide();
    setupSuggestionListClose(CONTROL_SUGGESTION_SELECTORS);
    setupControlFilterResetHandler();
    setupPasswordSwitchHandler();
    setupUserStatusSwitchHandler();
    setupAutocompleteInputs();
    setupConfirmationModal();
    setupSuggestionSync(SUGGESTION_SYNC_CONFIGS);
    setupControlPasswordToggle();
    setupDropdownSelector();
    setupFileUpload();
    setupWorkListManagement();
}


initControlPanel();
