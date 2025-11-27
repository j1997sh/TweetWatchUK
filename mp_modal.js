async function loadJSON(url) {
    const res = await fetch(url);
    return await res.json();
}

async function openMPModal(id) {
    const modal = document.getElementById("mpModal");
    const body = document.getElementById("mpModalBody");

    const tweets = await loadJSON(`data/twitter/${id}.json`).catch(() => null);
    const analytics = await loadJSON(`data/analytics/${id}.json`).catch(() => null);

    let html = `<h2>MP Profile</h2>`;

    if (analytics) {
        html += `
            <p><strong>Total Engagement:</strong> ${analytics.total_engagement}</p>
            <p><strong>Total Tweets:</strong> ${analytics.tweet_count}</p>
            <h3>Recent Tweets</h3>
        `;
    }

    if (tweets && tweets.tweets) {
        html += tweets.tweets.map(t => `
            <div class="tweet-block">
                <p>${t.text}</p>
                <small>${t.date}</small>
            </div>
        `).join("");
    } else {
        html += `<p>No tweets found.</p>`;
    }

    body.innerHTML = html;
    modal.style.display = "block";
}

document.querySelector(".close").onclick = () =>
    document.getElementById("mpModal").style.display = "none";

window.onclick = e => {
    if (e.target === document.getElementById("mpModal")) {
        document.getElementById("mpModal").style.display = "none";
    }
};
