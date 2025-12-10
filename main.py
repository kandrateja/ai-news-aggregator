from app.scrapers.youtube_scraper_service import YouTubeScraperService, ChannelVideo
from app.scrapers.openai_scraper_service import OpenAIScraperService, OpenAINewsArticle
from app.scrapers.anthropic_scraper_service import AnthropicScraperService, AnthropicArticle
from app.services.news_aggregator_service import NewsAggregatorService
from docling.document_converter import DocumentConverter
from typing import Union

def main():
    print("Hello from ai-news-aggregator!")
    
    # Initialize Markdown converter
    converter = DocumentConverter()

    # Initialize News Aggregator Service
    aggregator_service = NewsAggregatorService()

    # Define YouTube channels to monitor
    youtube_channel_ids = [
        "UCXZCJLdBC09xxGZ6gcdrc6A", # Example Channel ID
    ]

    print("\n" + "=" * 70 + "\n") # Separator
    print(f"Aggregating news from all sources for the last 100 hours...")
    combined_articles = aggregator_service.aggregate_news(youtube_channel_ids, timeframe_hours=100)

    if combined_articles:
        print(f"Found {len(combined_articles)} aggregated articles:")
        for article in combined_articles:
            print("\n" + "-"*50 + "\n")
            print(f"- Title: {article.title}")
            print(f"  Source: {type(article).__name__}")
            
            article_link = getattr(article, 'url', None) or getattr(article, 'link', None)
            if article_link:
                print(f"  Link: {article_link}")
                # Convert article link to Markdown
                print(f"[Main] Converting article link to Markdown: {article_link}")
                try:
                    result = converter.convert(str(article_link))
                    document = result.document
                    markdown_output = document.export_to_markdown()
                    print("[Main] Article Markdown snippet:")
                    print(markdown_output[:200]) # Print first 200 chars
                except Exception as e:
                    print(f"[Main] Error converting {article_link} to Markdown: {e}")
            
            print(f"  Published: {article.published}")
            if hasattr(article, 'video_id') and article.video_id:
                print(f"  Video ID: {article.video_id}")
            if hasattr(article, 'category') and article.category:
                print(f"  Category: {article.category}")
            if hasattr(article, 'guid') and article.guid:
                print(f"  GUID: {article.guid}")
            if hasattr(article, 'transcript') and article.transcript:
                print(f"  Transcript Snippet: {article.transcript[:200]}...")
            elif hasattr(article, 'description') and article.description:
                print(f"  Description Snippet: {article.description[:200]}...")
            
    else:
        print("No recent articles found from any source in the last 24 hours.")


if __name__ == "__main__":
    main()
