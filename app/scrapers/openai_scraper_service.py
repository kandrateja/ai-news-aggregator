import feedparser
from datetime import datetime, timedelta, UTC
from pydantic import BaseModel, HttpUrl

class OpenAINewsArticle(BaseModel):
    title: str
    description: str
    link: HttpUrl
    published: datetime
    category: str | None = None
    guid: str

class OpenAIScraperService:
    def get_latest_news(self, timeframe_hours: int = 24) -> list[OpenAINewsArticle]:
        """Fetches the latest news articles from OpenAI's RSS feed, filtered by timeframe."""
        feed_url = "https://openai.com/news/rss.xml"
        feed = feedparser.parse(feed_url)

        latest_news_articles = []
        time_threshold = datetime.now(UTC) - timedelta(hours=timeframe_hours)

        for entry in feed.entries:
            published_date_str = entry.published
            # Example format: 'Thu, 04 Dec 2025 19:00:00 GMT'
            # We need to use strptime to parse this specific format
            # After parsing, we assume GMT means UTC and make it timezone-aware
            published_date = datetime.strptime(published_date_str, "%a, %d %b %Y %H:%M:%S GMT").replace(tzinfo=UTC)

            # Debugging date comparison
            # print(f"Entry Published Date: {published_date} (Type: {type(published_date)}) (TZ: {published_date.tzinfo})")
            # print(f"Time Threshold: {time_threshold} (Type: {type(time_threshold)}) (TZ: {time_threshold.tzinfo})")
            # print(f"Comparison Result (published_date > time_threshold): {published_date > time_threshold}")

            if published_date > time_threshold:
                title = entry.title
                description = entry.description
                link = entry.link
                category = entry.get('category') # category might not always be present
                guid = entry.guid
                latest_news_articles.append(OpenAINewsArticle(title=title, description=description, link=link, published=published_date, category=category, guid=guid))
        return latest_news_articles

if __name__ == "__main__":
    # Example Usage for the OpenAIScraperService
    service = OpenAIScraperService()

    print(f"[Service] Fetching latest OpenAI news articles...")
    news_data = service.get_latest_news(timeframe_hours=48) # Check last 48 hours for demo

    if news_data:
        print(f"[Service] Found {len(news_data)} recent OpenAI news articles:")
        for article in news_data:
            print(f"- Title: {article.title}")
            print(f"  Link: {article.link}")
            print(f"  Published: {article.published}")
            if article.category:
                print(f"  Category: {article.category}")
            print(f"  GUID: {article.guid}")
            print(f"  Description: {article.description[:200]}...") # Print first 200 chars
            print("\n" + "-"*50 + "\n")
    else:
        print("[Service] No recent OpenAI news articles found in the last 48 hours.")
