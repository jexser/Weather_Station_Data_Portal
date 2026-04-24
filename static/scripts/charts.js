const chartTypeSelect = document.getElementById("chart_type");
const dateFieldWrap = document.querySelector(".charts-date-field");
const dateInput = document.getElementById("date");
const form = document.querySelector("[data-charts-form]");
const submitBtn = form.querySelector("[data-charts-submit]");
const chartArea = document.querySelector(".chart-area");
const placeholder = document.getElementById("chart-placeholder");
const canvas = document.getElementById("chart-canvas");
const inlineError = form.querySelector("[data-inline-error]");
let chartInstance = null;

function syncDateField() {
    const isYearlyTrend = chartTypeSelect.value === "yearly_trend";
    dateInput.disabled = isYearlyTrend;
    dateFieldWrap.classList.toggle("disabled", isYearlyTrend);

    if (isYearlyTrend) {
        dateInput.value = "";
    }
}

function showError(message) {
    inlineError.textContent = message;
    inlineError.hidden = false;
}

function clearError() {
    inlineError.hidden = true;
    inlineError.textContent = "";
}

function renderChart(labels, values, title) {
    placeholder.style.display = "none";
    canvas.style.display = "block";
    chartArea.classList.add("has-chart");

    if (chartInstance) {
        chartInstance.destroy();
    }

    chartInstance = new Chart(canvas.getContext("2d"), {
        type: "line",
        data: {
            labels,
            datasets: [{
                label: title,
                data: values,
                borderColor: "#1e2a3a",
                backgroundColor: "rgba(170, 255, 0, 0.08)",
                borderWidth: 2,
                pointRadius: 3,
                pointBackgroundColor: "#aaff00",
                pointBorderColor: "#1e2a3a",
                pointBorderWidth: 1,
                tension: 0.2,
                fill: true,
            }],
        },
        options: {
            responsive: true,
            plugins: {
                legend: { display: false },
                title: {
                    display: true,
                    text: title,
                    color: "#1e2a3a",
                    font: { size: 13, weight: "600" },
                    padding: { bottom: 16 },
                },
            },
            scales: {
                x: {
                    grid: { color: "#e4e4e4" },
                    ticks: { color: "#666", maxTicksLimit: 20, maxRotation: 45 },
                },
                y: {
                    grid: { color: "#e4e4e4" },
                    ticks: {
                        color: "#666",
                        callback: (value) => `${value} C`,
                    },
                    title: {
                        display: true,
                        text: "Temperature (C)",
                        color: "#888",
                        font: { size: 11 },
                    },
                },
            },
        },
    });
}

async function fetchChartData(stationId, chartType, date) {
    if (chartType === "yearly_trend") {
        const json = await window.apiClient.fetchJsonOrThrow(
            `/api/v1/station/${stationId}/yearly`,
            { notFoundMessage: "No data found for the selected station / date." }
        );

        return {
            labels: json.data.map((record) => String(record.year)),
            values: json.data.map((record) => record.temperature),
            title: "Annual Mean Temperature",
        };
    }

    const json = await window.apiClient.fetchJsonOrThrow(
        `/api/v1/station/${stationId}/date/${encodeURIComponent(date)}`,
        { notFoundMessage: "No data found for the selected station / date." }
    );

    return {
        labels: json.data.map((record) => record.date.slice(0, 4)),
        values: json.data.map((record) => record.temperature),
        title: `Temperature on ${date} by Year`,
    };
}

chartTypeSelect.addEventListener("change", syncDateField);
syncDateField();

form.addEventListener("submit", async (event) => {
    event.preventDefault();
    clearError();

    const stationId = form.querySelector("[data-station-id]").value;
    const chartType = chartTypeSelect.value;
    const date = dateInput.value.trim();

    if (chartType === "same_date" && !date) {
        showError("Please enter a date (MM-DD)");
        return;
    }

    submitBtn.disabled = true;
    submitBtn.value = "Loading...";

    try {
        const { labels, values, title } = await fetchChartData(stationId, chartType, date);

        if (labels.length === 0) {
            showError("No data found for the selected station / date.");
            return;
        }

        renderChart(labels, values, title);
    } catch (error) {
        if (error.message !== "Redirecting to error page.") {
            showError(error.message);
        }
    } finally {
        submitBtn.value = "Load chart";
        submitBtn.disabled = !form.querySelector("[data-station-id]").value;
    }
});
