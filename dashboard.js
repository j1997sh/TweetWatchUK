// ============================================================
//  LOAD JSON HELPER
// ============================================================
async function loadJSON(path) {
    try {
        const r = await fetch(path);
        return await r.json();
    } catch {
        return null;
    }
}

// ============================================================
//  LAST UPDATED TIMER
// ============================================================
function showLastUpdated(timestamp) {
    if (!timestamp) return;

    const el = document.getElementById("lastUpdated");
    const then = new Date(timestamp);
    const now = new Date();

    const mins = Math.floor((now - then) / 60000);
    el.textContent = `Last updated ${mins} minute${mins !== 1 ? "s" : ""} ago`;
}

// ============================================================
//  BUILD TABLE ROWS
// ============================================================
function makeRow(cols) {
    const tr = document.createElement("tr");
    tr.innerHTML = cols.map(c => `<td>${c}</td>`).join("");
    return tr;
}

// ============================================================
//  MAIN DASHBOARD LOGIC
// ============================================================
async function initDashboard() {
    const status = await loadJSON("status.json");
    const mps = await loadJSON("data/mps.json");

    showLastUpdated(status?.last_updated_utc);

    let analytics = {};

    // Load individual MP analytics files
    for (let mp of mps) {
        const id = mp.person_id;
        const file = await loadJSON(`data/analytics/${id}.json`);
        if (file) analytics[id] = file;
    }

    const list = Object.values(analytics);
    if (list.length === 0) return;

    // ============================================================
    //  COMPUTE DASHBOARD METRICS
    // ============================================================

    // Today = tweets in last 24 hours
    const now = new Date();
    let totalTweetsToday = 0;
    let totalEngagementToday = 0;

    list.forEach(mp => {
        const tweets = mp.engagement_last_hour ? mp.engagement_last_hour : 0;

        // engagement today = engagement_last_hour * 24 (RSS limit)
        totalEngagementToday += mp.engagement_last_hour;

        totalTweetsToday += mp.tweets;
    });

    document.getElementById("totalTweetsToday").textContent = totalTweetsToday.toLocaleString();
    document.getElementById("totalEngagementToday").textContent = totalEngagementToday.toLocaleString();

    // Most active MP
    const mostActive = [...list].sort((a, b) => b.tweets - a.tweets)[0];
    document.getElementById("mostActive").textContent =
        mostActive ? `${mostActive.name} (${mostActive.tweets} tweets)` : "—";

    // Most unpopular MP (lowest engagement per tweet)
    const leastLiked = [...list]
        .filter(a => a.tweets > 0)
        .sort((a, b) => (a.engagement / a.tweets) - (b.engagement / b.tweets))[0];

    document.getElementById("mostUnpopular").textContent =
        leastLiked ? `${leastLiked.name} (${Math.round(leastLiked.engagement / leastLiked.tweets)} per tweet)` : "—";

    // ============================================================
    //  TABLES
    // ============================================================

    // Top 10 engaging
    const topEng = [...list].sort((a, b) => b.engagement - a.engagement).slice(0, 10);
    const tbodyTopEng = document.getElementById("topEngaging").querySelector("tbody");

    topEng.forEach(mp => {
        tbodyTopEng.appendChild(makeRow([
            mp.name,
            mp.party,
            mp.engagement.toLocaleString()
        ]));
    });

    // Top 10 least engaging
    const lowEng = [...list].sort((a, b) => a.engagement - b.engagement).slice(0, 10);
    const tbodyLowEng = document.getElementById("leastEngaging").querySelector("tbody");

    lowEng.forEach(mp => {
        tbodyLowEng.appendChild(makeRow([
            mp.name,
            mp.party,
            mp.engagement.toLocaleString()
        ]));
    });

    // Top 10 most active (tweet count)
    const active = [...list].sort((a, b) => b.tweets - a.tweets).slice(0, 10);
    const tbodyActive = document.getElementById("mostActiveList").querySelector("tbody");

    active.forEach(mp => {
        tbodyActive.appendChild(makeRow([
            mp.name,
            mp.party,
            mp.tweets.toLocaleString()
        ]));
    });

    // Rising MPs (based on engagement_last_hour)
    const rising = [...list].sort((a, b) => b.engagement_last_hour - a.engagement_last_hour).slice(0, 10);
    const tbodyRising = document.getElementById("risingMps").querySelector("tbody");

    rising.forEach(mp => {
        tbodyRising.appendChild(makeRow([
            mp.name,
            mp.party,
            mp.engagement_last_hour
        ]));
    });

    // Falling MPs (reverse = lowest last hour engagement)
    const falling = [...list].sort((a, b) => a.engagement_last_hour - b.engagement_last_hour).slice(0, 10);
    const tbodyFalling = document.getElementById("fallingMps").querySelector("tbody");

    falling.forEach(mp => {
        tbodyFalling.appendChild(makeRow([
            mp.name,
            mp.party,
            mp.engagement_last_hour
        ]));
    });
}

// ============================================================
//  START
// ============================================================
initDashboard();
