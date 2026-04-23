import {
    setupSuggestionListClose,
    setupFilterResetHandler,
    setupPasswordToggle,
    setupScrollToTopButton,
    setupHoursSelection,
    setupDropdownCheckboxListener,
    setupFlashMessageAutoHide
} from "./shared/events.js";
import { setupTaskCreation, setupTaskDeletion } from "./user/tasks.js";
import { setupAutocompleteInputs, setupOrderSuggestionSync } from "./user/suggestions.js";
import { initWorksModal } from "./user/works-modal.js";


const APP_SUGGESTION_SELECTORS = [
    ".employee-search-suggestions",
    ".order-name-suggestions",
    ".order-number-suggestions",
];


function initApp() {
    setupFlashMessageAutoHide();
    setupSuggestionListClose(APP_SUGGESTION_SELECTORS);
    setupFilterResetHandler();
    setupPasswordToggle();
    setupScrollToTopButton();
    setupHoursSelection();
    setupTaskCreation();
    setupTaskDeletion();
    setupAutocompleteInputs();
    setupOrderSuggestionSync();
    setupDropdownCheckboxListener("dropdown-list", "dropdown-selected-text");
    initWorksModal();
}


initApp();
