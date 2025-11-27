// ===============================
//  PARTY COLOUR MAP
// ===============================
const PARTY_COLOURS = {
    "Conservative": "#0087DC",
    "Labour": "#E4003B",
    "Liberal Democrat": "#FDBB30",
    "SNP": "#FFF95D",
    "Green": "#00A859",
    "Reform UK": "#00B2FF",
    "Plaid Cymru": "#008142",
    "DUP": "#6F001A",
    "Sinn Féin": "#326760",
    "Alliance": "#F6CB2F",
    "SDLP": "#009A44",
    "Independent": "#666666",
    "Speaker": "#444444"
};

// ===============================
//  FETCH JSON HELPERS
// ===============================
async function loadJSON(path) {
    try {
        const r = await fetch(path);
        return await r.json();
    } catch {
        return null;
    }
}

// ===============================
//  LAST UPDATED TIMER
// ===============================
function showLastUpdated(timestamp) {
    if (!timestamp) return;

    const updatedEl = document.getElementById("lastUpdated");
    const then = new Date(timestamp);
    const now = new Date();

    const diffMinutes = Math.floor((now - then) / 60000);

    updatedEl.textContent = `Last updated ${diffMinutes} minute${diffMinutes !== 1 ? "s" : ""} ago`;
}

// ===============================
//  BUILD PARTY STAT TILES
// ===============================
function buildPartyTiles(data) {
    const container = document.getElementById("partyTiles");
    container.innerHTML = "";

    const sorted = Object.values(data).sort(
        (a, b) => b.total_engagement - a.total_engagement
    );

    sorted.forEach(p => {
        const tile = document.createElement("div");
        tile.className = "party-tile";
        tile.style.borderLeft = `10px solid ${PARTY_COLOURS[p.party] || "#999"}`;

        tile.innerHTML = `
            <h3>${p.party}</h3>
            <p><strong>${p.total_engagement.toLocaleString()}</strong> engagement</p>
            <p>${p.total_tweets.toLocaleString()} tweets • ${p.mps} MPs</p>
        `;

        container.appendChild(tile);
    });
}

// ===============================
//  BUILD BAR CHART
// ===============================
function buildChart(data) {
    const ctx = document.getElementById("partyChart");

    const labels = Object.keys(data);
    const engagement = labels.map(p => data[p].total_engagement);
    const colours = labels.map(p => PARTY_COLOURS[p] || "#999");

    new Chart(ctx, {
        type: "bar",
        data: {
            labels,
            datasets: [{
                label: "Total Engagement",
                data: engagement,
                backgroundColor: colours
            }]
        },
        options: {
            responsive: true,
            plugins: { legend: { display: false } },
            scales: {
                y: { beginAtZero: true }
            }
        }
    });
}

// ===============================
//  BUILD TABLE
// ===============================
function buildTable(data) {
    const tbody = document.querySelector("#partyTable tbody");
    tbody.innerHTML = "";

    const sorted = Object.values(data).sort(
        (a, b) => b.total_engagement - a.total_engagement
    );

    sorted.forEach(p => {
        const tr = document.createElement("tr");

        tr.innerHTML = `
            <td><span class="party-dot" style="background:${PARTY_COLOURS[p.party] || "#999"}"></span> ${p.party}</td>
            <td>${p.mps}</td>
            <td>${p.total_tweets.toLocaleString()}</td>
            <td>${p.total_engagement.toLocaleString()}</td>
            <td>${Math.round(p.total_tweets / p.mps).toLocaleString()}</td>
            <td>${Math.round(p.total_engagement / p.mps).toLocaleString()}</td>
        `;

        tbody.appendChild(tr);
    });
}

// ===============================
//  MAIN LOAD SEQUENCE
// ===============================
async function initPartyStats() {
    const summary = await loadJSON("data/analytics/party_summary.json");
    const status = await loadJSON("status.json");

    if (!summary) {
        document.querySelector(".content").innerHTML =
            "<p>Party analytics not available.</p>";
        return;
    }

    showLastUpdated(status?.last_updated_utc);
    buildPartyTiles(summary);
    buildChart(summary);
    buildTable(summary);
}

initPartyStats();
