from app.scrapers.youtube_scraper_service import YouTubeScraperService, ChannelVideo
from app.scrapers.openai_scraper_service import OpenAIScraperService, OpenAINewsArticle
from app.scrapers.anthropic_scraper_service import AnthropicScraperService, AnthropicArticle
from typing import List, Union

class NewsAggregatorService:
    def __init__(self):
        self.youtube_scraper = YouTubeScraperService()
        self.openai_scraper = OpenAIScraperService()
        self.anthropic_scraper = AnthropicScraperService()

    def aggregate_news(self, youtube_channel_ids: List[str], timeframe_hours: int = 100) -> List[Union[ChannelVideo, OpenAINewsArticle, AnthropicArticle]]:
        all_articles: List[Union[ChannelVideo, OpenAINewsArticle, AnthropicArticle]] = []
        print(f"[Service] Fetching YouTube videos...")
        print(f"what is the time frame hours? {timeframe_hours}")
        # Fetch YouTube videos
        for channel_id in youtube_channel_ids:
            youtube_videos = self.youtube_scraper.get_videos_with_transcripts(channel_id, timeframe_hours)
            all_articles.extend(youtube_videos)
        print(f"[Service] Found {len(youtube_videos)} recent YouTube videos:")
        # Fetch OpenAI news
        openai_news = self.openai_scraper.get_latest_news(timeframe_hours)
        all_articles.extend(openai_news)
        print(f"[Service] Found {len(openai_news)} recent OpenAI news articles:")
        # Fetch Anthropic articles
        anthropic_feed_urls = [
            "https://raw.githubusercontent.com/Olshansk/rss-feeds/main/feeds/feed_anthropic_news.xml",
            "https://raw.githubusercontent.com/Olshansk/rss-feeds/main/feeds/feed_anthropic_engineering.xml",
            "https://raw.githubusercontent.com/Olshansk/rss-feeds/main/feeds/feed_anthropic_research.xml"
        ]
        anthropic_articles = self.anthropic_scraper.get_latest_articles(anthropic_feed_urls, timeframe_hours)
        print(f"[Service] Found {len(anthropic_articles)} recent Anthropic articles:")
        all_articles.extend(anthropic_articles)
        
        # Sort all articles by published date, most recent first
        all_articles.sort(key=lambda x: x.published, reverse=True)

        return all_articles

if __name__ == "__main__":
    # Example Usage for NewsAggregatorService
    aggregator = NewsAggregatorService()
    
    # Example YouTube channels
    # You can get channel IDs from YouTube channel URLs like https://www.youtube.com/channel/UC_Fh8sn_oQyvL0zY0vN7Q8Q
    example_youtube_channels = [
        "UCXZCJLdBC09xxGZ6gcdrc6A", # Example Channel ID
    ]

    print("[Service] Aggregating news from all sources...")
    combined_articles = aggregator.aggregate_news(example_youtube_channels, timeframe_hours=100) # Get news from last 24 hours

    if combined_articles:
        print(f"[Service] Found {len(combined_articles)} aggregated articles:")
        for article in combined_articles:
            print(f"- Title: {article.title}")
            print(f"  Source: {type(article).__name__}")
            print(f"  Link: {article.url if hasattr(article, 'url') else article.link}")
            print(f"  Published: {article.published}")
            if hasattr(article, 'transcript') and article.transcript:
                print(f"  Transcript Snippet: {article.transcript[:200]}...")
            elif hasattr(article, 'description') and article.description:
                print(f"  Description Snippet: {article.description[:200]}...")
            print("\n" + "-"*50 + "\n")
    else:
        print("[Service] No recent articles found from any source in the last 24 hours.")
