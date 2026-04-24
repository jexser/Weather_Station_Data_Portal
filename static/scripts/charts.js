// ── Date field toggle ──────────────────────────────────────────────────────────
const chartTypeSelect = document.getElementById("chart_type");
const dateFieldWrap = document.querySelector(".charts-date-field");
const dateInput = document.getElementById("date");

function syncDateField() {
    const isYearlyTrend = chartTypeSelect.value === "yearly_trend";
    dateInput.disabled = isYearlyTrend;
    dateFieldWrap.classList.toggle("disabled", isYearlyTrend);
    if (isYearlyTrend) {
        dateInput.value = "";
    }
}

chartTypeSelect.addEventListener("change", syncDateField);
syncDateField();

// ── Form submit ───────────────────────────────────────────────────────────────
const form = document.querySelector("[data-charts-form]");
const submitBtn = form.querySelector("[data-charts-submit]");
const chartArea = document.querySelector(".chart-area");
const placeholder = document.getElementById("chart-placeholder");
const canvas = document.getElementById("chart-canvas");
let chartInstance = null;

form.addEventListener("submit", async (e) => {
    e.preventDefault();
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
            showError("No data available for the selected parameters.");
            return;
        }
        renderChart(labels, values, title);
    } catch (err) {
        showError(err.message);
    } finally {
        submitBtn.value = "Load chart";
        submitBtn.disabled = !form.querySelector("[data-station-id]").value;
    }
});

// ── Data fetching ─────────────────────────────────────────────────────────────
async function fetchChartData(stationId, chartType, date) {
    if (chartType === "yearly_trend") {
        const resp = await fetch(`/api/v1/station/${stationId}/yearly`);
        if (!resp.ok) {
            const body = await resp.json().catch(() => ({}));
            throw new Error(body.error?.message ?? "Failed to load data");
        }
        const json = await resp.json();
        return {
            labels: json.data.map((r) => String(r.year)),
            values: json.data.map((r) => r.temperature),
            title: "Annual Mean Temperature",
        };
    }

    const resp = await fetch(`/api/v1/station/${stationId}/date/${encodeURIComponent(date)}`);
    if (!resp.ok) {
        const body = await resp.json().catch(() => ({}));
        throw new Error(body.error?.message ?? "Failed to load data");
    }
    const json = await resp.json();
    return {
        labels: json.data.map((r) => r.date.slice(0, 4)),
        values: json.data.map((r) => r.temperature),
        title: `Temperature on ${date} by Year`,
    };
}

// ── Chart rendering ───────────────────────────────────────────────────────────
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
                        callback: (v) => `${v} °C`,
                    },
                    title: {
                        display: true,
                        text: "Temperature (°C)",
                        color: "#888",
                        font: { size: 11 },
                    },
                },
            },
        },
    });
}

// ── Inline error helpers ──────────────────────────────────────────────────────
function showError(msg) {
    let el = document.getElementById("chart-error");
    if (!el) {
        el = document.createElement("p");
        el.id = "chart-error";
        el.className = "chart-error";
        form.insertAdjacentElement("afterend", el);
    }
    el.textContent = msg;
}

function clearError() {
    document.getElementById("chart-error")?.remove();
}
