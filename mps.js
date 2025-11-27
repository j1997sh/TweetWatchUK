async function loadJSON(url) {
    const res = await fetch(url);
    return await res.json();
}

let mpData = [];
let analyticsData = {};

async function initMPList() {
    mpData = await loadJSON("data/mps.json");

    for (let mp of mpData) {
        try {
            analyticsData[mp.person_id] =
                await loadJSON(`data/analytics/${mp.person_id}.json`);
        } catch (e) {}
    }

    populatePartyFilter();
    renderTable(mpData);

    document.getElementById("search-input").addEventListener("input", applyFilters);
    document.getElementById("party-filter").addEventListener("change", applyFilters);
}

function populatePartyFilter() {
    const select = document.getElementById("party-filter");
    const parties = [...new Set(mpData.map(mp => mp.party))].sort();
    parties.forEach(p => {
        const opt = document.createElement("option");
        opt.value = p;
        opt.innerText = p;
        select.appendChild(opt);
    });
}

function applyFilters() {
    const search = document.getElementById("search-input").value.toLowerCase();
    const party = document.getElementById("party-filter").value;

    const filtered = mpData.filter(mp => {
        const matchSearch =
            mp.name.toLowerCase().includes(search) ||
            mp.constituency.toLowerCase().includes(search) ||
            mp.party.toLowerCase().includes(search);

        const matchParty = party === "" || mp.party === party;

        return matchSearch && matchParty;
    });

    renderTable(filtered);
}

function renderTable(rows) {
    const tbody = document.querySelector("#mp-table tbody");
    tbody.innerHTML = "";

    rows.forEach(mp => {
        const a = analyticsData[mp.person_id] || {};
        const tr = document.createElement("tr");

        tr.innerHTML = `
            <td class="mp-click" data-id="${mp.person_id}">${mp.name}</td>
            <td>${mp.party}</td>
            <td>${mp.constituency}</td>
            <td>${a.total_engagement || 0}</td>
            <td>${a.tweet_count || 0}</td>
        `;

        tbody.appendChild(tr);
    });

    document.querySelectorAll(".mp-click").forEach(el => {
        el.onclick = () => openMPModal(el.dataset.id);
    });
}

initMPList();
