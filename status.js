async function loadJSON(path) {
    try { return await (await fetch(path)).json(); }
    catch { return null; }
}

function minutesAgo(ms) {
    const m = Math.floor(ms / 60000);
    if (m <= 0) return "Just now";
    if (m === 1) return "1 minute ago";
    return `${m} minutes ago`;
}

async function initStatus() {
    const status = await loadJSON("data/analytics/system_status.json") || {};
    const last = await loadJSON("data/analytics/last_update.json");

    // --- Last updated ---
    if (last) {
        const diff = new Date() - new Date(last.last_updated);
        document.getElementById("status-last-updated").innerText = minutesAgo(diff);
    } else {
        document.getElementById("status-last-updated").innerText = "Never";
    }

    // --- Last run result ---
    document.getElementById("status-result").innerText =
        status.last_result ? status.last_result.toUpperCase() : "UNKNOWN";

    // --- Subsystems ---
    function apply(id, result) {
        const el = document.getElementById(id);
        const state = result || "unknown";
        el.innerText = state.toUpperCase();
        el.classList.add("status-" + state);
    }

    apply("comp-mps", status.mp_fetch);
    apply("comp-tweets", status.tweet_fetch);
    apply("comp-analytics", status.analytics);
    apply("comp-parties", status.party_stats);
    apply("comp-deploy", status.deploy);
}

initStatus();
