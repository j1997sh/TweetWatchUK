async function loadJSON(url) {
    const res = await fetch(url);
    return await res.json();
}

async function initDashboard() {
    const mps = await loadJSON("data/mps.json");
    const analytics = {};

    // Load analytics for MPs
    for (let mp of mps) {
        try {
            const data = await loadJSON(`data/analytics/${mp.person_id}.json`);
            analytics[mp.person_id] = data;
        } catch (e) {}
    }

    // Compute totals
    let totalTweets = 0;
    let totalEngagement = 0;

    for (let id in analytics) {
        const a = analytics[id];
        totalTweets += a.tweet_count || 0;
        totalEngagement += a.total_engagement || 0;
    }

    document.getElementById("total-tweets").innerText = totalTweets;
    document.getElementById("total-engagement").innerText = totalEngagement;

    // Build leaderboards
    const rows = mps.map(mp => {
        const a = analytics[mp.person_id] || {};
        return {
            name: mp.name,
            party: mp.party,
            engagement: a.total_engagement || 0,
            tweets: a.tweet_count || 0
        };
    });

    // Most engaging
    const topEngaging = [...rows].sort((a,b) => b.engagement - a.engagement).slice(0,10);
    fillTable("top-engaging-table", topEngaging);

    // Least engaging
    const least = [...rows].sort((a,b) => a.engagement - b.engagement).slice(0,10);
    fillTable("least-engaging-table", least);

    // Most active
    const active = [...rows].sort((a,b) => b.tweets - a.tweets).slice(0,10);
    fillTable("most-active-table", active);

    document.getElementById("most-active").innerText = active[0]?.name || "N/A";
    document.getElementById("most-unpopular").innerText = least[0]?.name || "N/A";
}

function fillTable(id, rows) {
    const tbody = document.querySelector(`#${id} tbody`);
    tbody.innerHTML = "";
    rows.forEach(r => {
        const tr = document.createElement("tr");
        tr.innerHTML = `
            <td>${r.name}</td>
            <td>${r.party}</td>
            <td>${r.engagement}</td>
        `;
        tbody.appendChild(tr);
    });
}

initDashboard();

init()
