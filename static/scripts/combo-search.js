const stationComboboxes = document.querySelectorAll("[data-station-combobox]");
const compareForm = document.querySelector("[data-compare-form]");

function getOrCreateComboboxError(combobox) {
    let errorElement = combobox.querySelector("[data-combobox-error]");

    if (!errorElement) {
        errorElement = document.createElement("p");
        errorElement.className = "inline-error";
        errorElement.dataset.comboboxError = "";
        errorElement.hidden = true;
        combobox.appendChild(errorElement);
    }

    return errorElement;
}

function showComboboxError(combobox, message) {
    const errorElement = getOrCreateComboboxError(combobox);
    errorElement.textContent = message;
    errorElement.hidden = false;
}

function clearComboboxError(combobox) {
    const errorElement = getOrCreateComboboxError(combobox);
    errorElement.textContent = "";
    errorElement.hidden = true;
}

function toggleSubmitButtons() {
    const chartsForm = document.querySelector("[data-charts-form]");
    if (chartsForm) {
        const chartsButton = chartsForm.querySelector("[data-charts-submit]");
        const stationId = chartsForm.querySelector("[data-station-id]");

        if (chartsButton && stationId) {
            chartsButton.disabled = !stationId.value;
        }
    }

    const insightsForm = document.querySelector("[data-insights-form]");
    if (insightsForm) {
        const insightsButton = insightsForm.querySelector('input[type="submit"]');
        const stationId = insightsForm.querySelector("[data-station-id]");

        if (insightsButton && stationId) {
            insightsButton.disabled = !stationId.value;
        }
    }

    if (!compareForm) {
        return;
    }

    const compareButton = compareForm.querySelector("[data-compare-submit]");
    const stationA = compareForm.querySelector('input[name="station_a_id"]');
    const stationB = compareForm.querySelector('input[name="station_b_id"]');
    const year = compareForm.querySelector('input[name="year"]');

    if (!compareButton || !stationA || !stationB || !year) {
        return;
    }

    compareButton.disabled = !(stationA.value && stationB.value && year.value.trim());
}

stationComboboxes.forEach((combobox) => {
    const input = combobox.querySelector("[data-station-input]");
    const hiddenInput = combobox.querySelector("[data-station-id]");
    const results = combobox.querySelector("[data-station-results]");

    if (!input || !hiddenInput || !results) {
        return;
    }

    let timeout = null;

    input.addEventListener("input", () => {
        hiddenInput.value = "";
        clearTimeout(timeout);
        clearComboboxError(combobox);

        timeout = setTimeout(async () => {
            const query = input.value.trim();

            if (query.length < 2) {
                results.innerHTML = "";
                return;
            }

            try {
                const data = await window.apiClient.fetchJsonOrThrow(
                    `/api/v1/stations/search?name=${encodeURIComponent(query)}`,
                    { notFoundMessage: "No stations found." }
                );

                results.innerHTML = "";

                data.data.forEach((station) => {
                    const item = document.createElement("div");
                    item.classList.add("combo-item");
                    item.textContent = `${station.STAID} - ${station.STANAME}`;

                    item.onclick = () => {
                        input.value = station.STANAME;
                        hiddenInput.value = station.STAID;
                        results.innerHTML = "";
                        clearComboboxError(combobox);
                        toggleSubmitButtons();
                    };

                    results.appendChild(item);
                });
            } catch (error) {
                if (error.message !== "Redirecting to error page.") {
                    results.innerHTML = "";
                    showComboboxError(combobox, error.message);
                }
            }
        }, 300);

        toggleSubmitButtons();
    });

    document.addEventListener("click", (event) => {
        if (!combobox.contains(event.target)) {
            results.innerHTML = "";
        }
    });
});

if (compareForm) {
    compareForm.addEventListener("input", toggleSubmitButtons);
}

toggleSubmitButtons();
