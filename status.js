async function loadJSON(path) {
    try { return await (await fetch(path)).json(); }
    catch { return null; }
}

function minutesAgo(ms) {
    const m = Math.floor(ms / 60000);
    if (m < 1) return "Just now";
    if (m === 1) return "1 minute ago";
    return `${m} minutes ago`;
}

async function initStatus() {

    // --- Load timestamps ---
    const info = await loadJSON("data/analytics/last_update.json");
    const last = info ? new Date(info.last_updated) : null;

    if (last) {
        document.getElementById("status-last-updated").innerText =
            minutesAgo(new Date() - last);
    } else {
        document.getElementById("status-last-updated").innerText =
            "Never";
    }

    // --- Load component statuses ---
    const status = await loadJSON("data/analytics/system_status.json") || {
        mp_fetch: "unknown",
        tweet_fetch: "unknown",
        analytics: "unknown",
        party_stats: "unknown",
        deploy: "unknown",
        last_result: "unknown"
    };

    document.getElementById("status-result").innerText =
        status.last_result.toUpperCase();

    document.getElementById("comp-mps").innerText = status.mp_fetch.toUpperCase();
    document.getElementById("comp-tweets").innerText = status.tweet_fetch.toUpperCase();
    document.getElementById("comp-analytics").innerText = status.analytics.toUpperCase();
    document.getElementById("comp-parties").innerText = status.party_stats.toUpperCase();
    document.getElementById("comp-deploy").innerText = status.deploy.toUpperCase();
}

initStatus();
