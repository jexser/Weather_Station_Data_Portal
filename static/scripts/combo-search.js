const stationComboboxes = document.querySelectorAll("[data-station-combobox]");

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

        timeout = setTimeout(async () => {
            const query = input.value.trim();

            if (query.length < 2) {
                results.innerHTML = "";
                return;
            }

            const response = await fetch(`/api/v1/stations/search?name=${encodeURIComponent(query)}`);
            const data = await response.json();

            results.innerHTML = "";

            data.data.forEach((station) => {
                const item = document.createElement("div");
                item.classList.add("combo-item");
                item.textContent = `${station.STAID} - ${station.STANAME}`;

                item.onclick = () => {
                    input.value = station.STANAME;
                    hiddenInput.value = station.STAID;
                    results.innerHTML = "";
                    toggleSubmitButtons();
                };

                results.appendChild(item);
            });
        }, 300);

        toggleSubmitButtons();
    });

    document.addEventListener("click", (event) => {
        if (!combobox.contains(event.target)) {
            results.innerHTML = "";
        }
    });
});

const compareForm = document.querySelector("[data-compare-form]");

function toggleSubmitButtons() {
    const chartsForm = document.querySelector("[data-charts-form]");
    if (chartsForm) {
        const chartsButton = chartsForm.querySelector("[data-charts-submit]");
        const stationId = chartsForm.querySelector("[data-station-id]");
        if (chartsButton && stationId) {
            chartsButton.disabled = !stationId.value;
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

if (compareForm) {
    compareForm.addEventListener("input", toggleSubmitButtons);
    toggleSubmitButtons();
}
