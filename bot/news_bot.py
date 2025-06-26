import requests
from bs4 import BeautifulSoup
import firebase_admin
from firebase_admin import credentials, firestore
import datetime
import tweepy  # For Twitter posting, as an example

# Initialize Firebase Admin SDK
cred = credentials.Certificate("path/to/your/firebase-service-account.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

# Twitter API credentials (replace with your own)
TWITTER_API_KEY = "your-twitter-api-key"
TWITTER_API_SECRET = "your-twitter-api-secret"
TWITTER_ACCESS_TOKEN = "your-twitter-access-token"
TWITTER_ACCESS_SECRET = "your-twitter-access-secret"

auth = tweepy.OAuth1UserHandler(
    TWITTER_API_KEY, TWITTER_API_SECRET, TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_SECRET
)
twitter_api = tweepy.API(auth)

def scrape_news():
    url = "https://example-news-site.com"  # Replace with actual news site
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")

    articles = []
    # Example: find all news articles - adjust selectors as needed
    for item in soup.select(".news-article"):
        title = item.select_one(".title").get_text(strip=True)
        content = item.select_one(".summary").get_text(strip=True)
        published_at = datetime.datetime.now()  # Or parse from the site if available
        articles.append({
            "title": title,
            "content": content,
            "publishedAt": published_at
        })
    return articles

def publish_news_to_firebase(articles):
    for article in articles:
        # Check if article already exists by title or other unique field
        docs = db.collection("news").where("title", "==", article["title"]).stream()
        if any(docs):
            print(f"Article '{article['title']}' already exists. Skipping.")
            continue
        # Add new article
        db.collection("news").add(article)
        print(f"Published article '{article['title']}' to Firebase.")

def post_news_to_twitter(articles):
    for article in articles:
        tweet = f"{article['title']}\n\n{article['content'][:200]}..."  # Limit tweet length
        try:
            twitter_api.update_status(tweet)
            print(f"Posted tweet for article '{article['title']}'")
        except Exception as e:
            print(f"Error posting tweet: {e}")

def main():
    articles = scrape_news()
    publish_news_to_firebase(articles)
    post_news_to_twitter(articles)

if __name__ == "__main__":
    main()
