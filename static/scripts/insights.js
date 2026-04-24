const insightsForm = document.querySelector("[data-insights-form]");

if (insightsForm) {
    const stationInput = insightsForm.querySelector("[data-station-input]");
    const stationIdInput = insightsForm.querySelector("[data-station-id]");
    const dateInput = insightsForm.querySelector("#date");
    const submitButton = insightsForm.querySelector('input[type="submit"]');
    const inlineError = insightsForm.querySelector("[data-inline-error]");
    const resultsSection = document.querySelector("[data-insights-results]");
    const heading = resultsSection?.querySelector("[data-insights-heading]");

    const DATE_REQUIRED_TOOLTIP = "Provide a date (MM-DD) to get this insight.";
    const DATE_PATTERN = /^\d{2}-\d{2}$/;

    const INSIGHT_CONFIG = [
        { type: "hottest_year", formatter: (data) => `${data.year} at ${data.value} °C` },
        { type: "coldest_year", formatter: (data) => `${data.year} at ${data.value} °C` },
        { type: "hottest_day", formatter: (data) => `${data.date} at ${data.value} °C` },
        { type: "coldest_day", formatter: (data) => `${data.date} at ${data.value} °C` },
        { type: "avg_for_date", formatter: (data) => `${data.avg_temp} °C`, dateDependent: true },
        { type: "temp_variability", formatter: (data) => `+/-${data.std_dev} °C`, dateDependent: true },
        { type: "missing_data_count", formatter: (data) => String(data.missing_count) },
    ];

    function showError(message) {
        inlineError.textContent = message;
        inlineError.hidden = false;
    }

    function clearError() {
        inlineError.textContent = "";
        inlineError.hidden = true;
    }

    function setDateDependentPlaceholder(type) {
        const row = resultsSection.querySelector(`[data-insight-row="${type}"]`);
        const valueCell = resultsSection.querySelector(`[data-insight-value="${type}"]`);

        row.classList.add("muted");
        row.title = DATE_REQUIRED_TOOLTIP;
        valueCell.textContent = "-";
    }

    function clearDateDependentPlaceholder(type) {
        const row = resultsSection.querySelector(`[data-insight-row="${type}"]`);
        row.classList.remove("muted");
        row.removeAttribute("title");
    }

    function updateHeading(stationName, date) {
        heading.textContent = date
            ? `Insights for ${stationName} on ${date}`
            : `Insights for ${stationName}`;
    }

    async function loadInsights(stationId, date, allowDateDependentRequests) {
        const requests = INSIGHT_CONFIG.map(async (config) => {
            if (config.dateDependent && !allowDateDependentRequests) {
                setDateDependentPlaceholder(config.type);
                return;
            }

            if (config.dateDependent) {
                clearDateDependentPlaceholder(config.type);
            }

            const query = new URLSearchParams({ type: config.type });
            if (config.dateDependent) {
                query.set("date", date);
            }

            const json = await window.apiClient.fetchJsonOrThrow(
                `/api/v1/insights/${stationId}?${query.toString()}`,
                { notFoundMessage: "No data found for the selected station / date." }
            );

            const valueCell = resultsSection.querySelector(`[data-insight-value="${config.type}"]`);
            valueCell.textContent = config.formatter(json.data);
        });

        await Promise.all(requests);
    }

    insightsForm.addEventListener("submit", async (event) => {
        event.preventDefault();
        clearError();

        const stationId = stationIdInput.value.trim();
        const stationName = stationInput.value.trim();
        const date = dateInput.value.trim();
        const hasValidDate = !date || DATE_PATTERN.test(date);

        if (!stationId) {
            showError("Please select a station.");
            return;
        }

        if (!hasValidDate) {
            showError("Please enter a date (MM-DD)");
        }

        submitButton.disabled = true;
        submitButton.value = "Loading...";

        try {
            await loadInsights(stationId, date, hasValidDate && Boolean(date));
            updateHeading(stationName, date);
            resultsSection.hidden = false;
        } catch (error) {
            if (error.message !== "Redirecting to error page.") {
                showError(error.message);
            }
        } finally {
            submitButton.value = "Load insights";
            submitButton.disabled = !stationIdInput.value;
        }
    });
}
