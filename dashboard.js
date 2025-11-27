async function loadJSON(url){return fetch(url).then(r=>r.json())}

async function loadAnalytics(){
  const index=await loadJSON('data/mps.json')
  const list=[]
  for(const mp of index){
    try{
      const stats=await loadJSON(`data/analytics/${mp.person_id}.json`)
      list.push(stats)
    }catch(e){}
  }
  list.sort((a,b)=>a.engagement_per_tweet - b.engagement_per_tweet)
  return list
}

async function init(){
  const app=document.getElementById('app')
  const mps=await loadJSON('data/mps.json')

  for(const mp of mps){
    let tweets=[],stats=null
    try{
      tweets=await loadJSON(`data/twitter/${mp.person_id}.json`)
      stats=await loadJSON(`data/analytics/${mp.person_id}.json`)
    }catch(e){continue}

    const card=document.createElement('div')
    card.className='account-card'
    card.innerHTML=`
      <h2>${mp.name} (${mp.party})</h2>
      <p>Engagement per tweet: <span class="${stats.risk_flag}">${stats.engagement_per_tweet}</span></p>
      <p>Total engagement: ${stats.total_engagement}</p>

      <h3>Top Words</h3>
      <ul>
        ${stats.top_words.map(([w,c])=>`<li>${w}: ${c}</li>`).join("")}
      </ul>

      <h3>Latest Tweets</h3>
      ${tweets.map(t=>`
        <p><a href="${t.url}" target="_blank">${t.text}</a><br>
        Likes: ${t.likes}, RTs: ${t.retweets}, Replies: ${t.replies}</p>
      `).join("")}
    `;
    app.appendChild(card)
  }

  const leaderboard=await loadAnalytics()
  const lb=document.getElementById('leaderboard')
  lb.innerHTML = `
    <h2>Who Is The Most Unpopular Online?</h2>
    <ol>
      ${leaderboard.slice(0,20).map(mp=>`
        <li>${mp.name} – <span class="${mp.risk_flag}">${mp.engagement_per_tweet}</span> EPT</li>
      `).join("")}
    </ol>
  `
}

init()
