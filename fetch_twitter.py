import feedparser, json, os, re
from collections import Counter

NITTER="https://nitter.poast.org"
STOPWORDS={"the","and","a","to","in","of","for","on","is","it","that","this","with","at","as","be","are","was","were"}

os.makedirs("data/twitter",exist_ok=True)
os.makedirs("data/analytics",exist_ok=True)

with open("data/mps.json") as f:
    mps=json.load(f)

def clean_text(text):
    text=text.lower()
    text=re.sub(r"http\S+","",text)
    text=re.sub(r"[^a-z\s]","",text)
    return [w for w in text.split() if w not in STOPWORDS]

for mp in mps:
    pid=str(mp['person_id'])
    username=mp.get("twitter_username")
    if not username: 
        continue

    feed=feedparser.parse(f"{NITTER}/{username}/rss")
    tweets=[]
    word_list=[]
    likes_total=ret_total=rep_total=0

    for e in feed.entries[:20]:
        content=e.title

        def extract(pattern):
            m=re.search(pattern, content)
            return int(m.group(1)) if m else 0

        likes=extract(r"(\d+) Likes")
        rts=extract(r"(\d+) Retweets")
        reps=extract(r"(\d+) Replies")

        likes_total+=likes
        ret_total+=rts
        rep_total+=reps

        words=clean_text(content)
        word_list.extend(words)

        tweets.append({
            "text": content,
            "url": e.link,
            "date": e.published,
            "likes": likes,
            "retweets": rts,
            "replies": reps
        })

    with open(f"data/twitter/{pid}.json","w") as f:
        json.dump(tweets,f,indent=2)

    total=len(tweets)
    ept = (likes_total+ret_total+rep_total)/total if total else 0

    if ept <= 3:
        risk="RED"
    elif ept <= 10:
        risk="AMBER"
    else:
        risk="GREEN"

    analytics={
        "person_id": pid,
        "name": mp["name"],
        "party": mp["party"],
        "total_tweets": total,
        "total_engagement": likes_total+ret_total+rep_total,
        "engagement_per_tweet": round(ept,2),
        "top_words": Counter(word_list).most_common(10),
        "risk_flag": risk
    }

    with open(f"data/analytics/{pid}.json","w") as f:
        json.dump(analytics,f,indent=2)
