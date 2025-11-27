async function loadJSON(url) {
    try {
        const res = await fetch(url);
        return await res.json();
    } catch {
        return null;
    }
}

async function initDashboard() {
    const mps = await loadJSON("data/mps.json");
    const analytics = {};
    const snapshots = {};
    const nowHour = new Date().getHours();

    // Load analytics
    for (const mp of mps) {
        const a = await loadJSON(`data/analytics/${mp.person_id}.json`);
        if (a) analytics[mp.person_id] = a;
    }

    // Load snapshot (last hour)
    const today = new Date();
    const ymd = today.toISOString().split("T")[0];
    const snapshotFile = `data/history/${ymd}-${nowHour}.json`;
    const snapshot = await loadJSON(snapshotFile) || {};

    // Compute totals
    let totalTweets = 0;
    let totalEngagement = 0;

    const rows = mps.map(mp => {
        const a = analytics[mp.person_id] || {};
        totalTweets += a.tweet_count || 0;
        totalEngagement += a.total_engagement || 0;

        const prev = snapshot[mp.person_id]?.total_engagement || 0;

        return {
            ...mp,
            engagement: a.total_engagement || 0,
            tweets: a.tweet_count || 0,
            delta: (a.total_engagement || 0) - prev
        };
    });

    // Update totals
    document.getElementById("totalTweets").textContent = totalTweets;
    document.getElementById("totalEngagement").textContent = totalEngagement;

    // Tables
    fillTable("topEngaging", [...rows].sort((a,b)=>b.engagement-a.engagement).slice(0,10));
    fillTable("leastEngaging", [...rows].sort((a,b)=>a.engagement-b.engagement).slice(0,10));
    fillTable("mostActiveTable", [...rows].sort((a,b)=>b.tweets-a.tweets).slice(0,10));
    fillTable("risingTable", [...rows].sort((a,b)=>b.delta-a.delta).slice(0,10));
    fillTable("fallingTable", [...rows].sort((a,b)=>a.delta-b.delta).slice(0,10));

    document.getElementById("mostActive").textContent =
        rows.sort((a,b)=>b.tweets-a.tweets)[0]?.name || "N/A";

    document.getElementById("leastActive").textContent =
        rows.sort((a,b)=>a.engagement-b.engagement)[0]?.name || "N/A";
}

function fillTable(id, array) {
    const tbody = document.querySelector(`#${id} tbody`);
    tbody.innerHTML = "";
    array.forEach(r => {
        tbody.innerHTML += `
            <tr>
                <td>${r.name}</td>
                <td>${r.party}</td>
                <td>${r.engagement ?? r.tweets ?? r.delta}</td>
            </tr>`;
    });
}

initDashboard();
