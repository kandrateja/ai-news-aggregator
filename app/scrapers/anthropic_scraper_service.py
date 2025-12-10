import feedparser
import time # Import the time module
from datetime import datetime, timedelta, UTC
from pydantic import BaseModel, HttpUrl

class AnthropicArticle(BaseModel):
    title: str
    description: str
    link: HttpUrl
    published: datetime
    guid: str # GUID is usually unique for each item

class AnthropicScraperService:
    def get_latest_articles(self, feed_urls: list[str], timeframe_hours: int = 100) -> list[AnthropicArticle]:
        """Fetches the latest articles from multiple Anthropic RSS feeds, filtered by timeframe."""
        all_articles: list[AnthropicArticle] = []
        time_threshold = datetime.now(UTC) - timedelta(hours=timeframe_hours)

        for feed_url in feed_urls:
            # print(f"[Debug Anthropic] Feed URL: {feed_url}")
            feed = feedparser.parse(feed_url)
            for entry in feed.entries:
                # feedparser provides 'published_parsed' as a time.struct_time object
                published_date_struct = getattr(entry, 'published_parsed', None)
                
                if not published_date_struct:
                    continue
                published_date = datetime.fromtimestamp(time.mktime(published_date_struct), tz=UTC)

                if published_date > time_threshold:
                    title = entry.title
                    description = entry.description
                    link = entry.link
                    guid = entry.guid
                    all_articles.append(AnthropicArticle(title=title, description=description, link=link, published=published_date, guid=guid))
                # else:
                #     # Optionally log which entries are skipped due to missing/old dates
                #     print(f"[Debug Anthropic] Skipping entry due to missing or old date: {entry.title if hasattr(entry, 'title') else 'N/A'}")
        
        # Remove duplicates based on GUID, keeping the most recent if any duplicates exist
        unique_articles: dict[str, AnthropicArticle] = {}
        for article in all_articles:
            if article.guid not in unique_articles or article.published > unique_articles[article.guid].published:
                unique_articles[article.guid] = article
                
        # Sort articles by published date, most recent first
        sorted_articles = sorted(unique_articles.values(), key=lambda x: x.published, reverse=True)
        return sorted_articles

if __name__ == "__main__":
    # Example Usage for the AnthropicScraperService
    service = AnthropicScraperService()
    anthropic_feed_urls = [
        "https://raw.githubusercontent.com/Olshansk/rss-feeds/main/feeds/feed_anthropic_news.xml",
        "https://raw.githubusercontent.com/Olshansk/rss-feeds/main/feeds/feed_anthropic_engineering.xml",
        "https://raw.githubusercontent.com/Olshansk/rss-feeds/main/feeds/feed_anthropic_research.xml"
    ]

    print(f"[Service] Fetching latest Anthropic articles...")
    articles_data = service.get_latest_articles(anthropic_feed_urls, timeframe_hours=72) # Check last 72 hours for demo

    if articles_data:
        print(f"[Service] Found {len(articles_data)} recent Anthropic articles:")
        for article in articles_data:
            print(f"- Title: {article.title}")
            print(f"  Link: {article.link}")
            print(f"  Published: {article.published}")
            print(f"  GUID: {article.guid}")
            print(f"  Description: {article.description[:200]}...") # Print first 200 chars
            print("\n" + "-"*50 + "\n")
    else:
        print("[Service] No recent Anthropic articles found in the last 72 hours.")
