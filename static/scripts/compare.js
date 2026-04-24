const compareClientForm = document.querySelector("[data-compare-form]");

if (compareClientForm) {
    const stationAInput = compareClientForm.querySelector('input[name="station_a_name"]');
    const stationBInput = compareClientForm.querySelector('input[name="station_b_name"]');
    const stationAIdInput = compareClientForm.querySelector('input[name="station_a_id"]');
    const stationBIdInput = compareClientForm.querySelector('input[name="station_b_id"]');
    const yearInput = compareClientForm.querySelector('input[name="year"]');
    const submitButton = compareClientForm.querySelector("[data-compare-submit]");
    const inlineError = compareClientForm.querySelector("[data-inline-error]");
    const resultsSection = document.querySelector("[data-compare-results]");
    const heading = resultsSection?.querySelector("h2");
    const tableHead = resultsSection?.querySelector("thead tr");
    const tableBody = resultsSection?.querySelector("tbody");

    function showError(message) {
        inlineError.textContent = message;
        inlineError.hidden = false;
    }

    function clearError() {
        inlineError.textContent = "";
        inlineError.hidden = true;
    }

    function formatTemperature(value) {
        if (value === null || value === undefined) {
            return "NULL";
        }

        return `${value.toFixed(1)} degC`;
    }

    function renderComparisonTable(records, stationAName, stationBName, year) {
        heading.textContent = `${stationAName} vs ${stationBName} in ${year}`;
        tableHead.innerHTML = `
            <th>Date</th>
            <th>${stationAName}</th>
            <th>${stationBName}</th>
        `;
        tableBody.innerHTML = records.map((record) => `
            <tr>
                <td>${record.date}</td>
                <td>${formatTemperature(record.stationA)}</td>
                <td>${formatTemperature(record.stationB)}</td>
            </tr>
        `).join("");
        resultsSection.hidden = false;
    }

    compareClientForm.addEventListener("submit", async (event) => {
        event.preventDefault();
        clearError();

        const stationAId = stationAIdInput.value.trim();
        const stationBId = stationBIdInput.value.trim();
        const year = yearInput.value.trim();

        if (!stationAId || !stationBId || !year) {
            showError("Please select both stations and enter a year.");
            return;
        }

        submitButton.disabled = true;
        submitButton.value = "Loading...";

        try {
            const query = new URLSearchParams({
                stationA_id: stationAId,
                stationB_id: stationBId,
                year,
            });
            const json = await window.apiClient.fetchJsonOrThrow(
                `/api/v1/compare?${query.toString()}`,
                { notFoundMessage: "No data found for the selected station / date." }
            );

            renderComparisonTable(
                json.data,
                stationAInput.value.trim() || stationAId,
                stationBInput.value.trim() || stationBId,
                year
            );
        } catch (error) {
            if (error.message !== "Redirecting to error page.") {
                showError(error.message);
            }
        } finally {
            submitButton.value = "Compare";
            submitButton.disabled = !(stationAIdInput.value && stationBIdInput.value && yearInput.value.trim());
        }
    });
}
