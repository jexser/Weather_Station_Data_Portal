const input = document.getElementById("station-search");
const resultsDiv = document.getElementById("results");

let timeout = null;

input.addEventListener("input", () => {
    clearTimeout(timeout);

    timeout = setTimeout(async () => {
        const query = input.value;

        if (query.length < 2) return;

        const response = await fetch(`/api/v1/stations/search?name=${query}`);
        const data = await response.json();

        renderResults(data.data);
    }, 300); // wait 300ms after typing stops
});

function renderResults(stations) {
    resultsDiv.innerHTML = "";

    stations.forEach(station => {
        const item = document.createElement("div");
        item.classList.add("combo-item");
        item.textContent = `${station.STAID} - ${station.STANAME}`;

        item.onclick = () => {
            document.getElementById("station-search").value = station.STANAME;
            resultsDiv.innerHTML = "";
        };

        resultsDiv.appendChild(item);
    });
}

document.addEventListener("click", (event) => {
    const input = document.getElementById("station-search");
    const results = document.getElementById("results");

    const clickedInside =
        input.contains(event.target) ||
        results.contains(event.target);

    if (!clickedInside) {
        results.innerHTML = "";
    }
});