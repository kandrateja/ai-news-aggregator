import feedparser
from datetime import datetime, timedelta, UTC
from youtube_transcript_api import YouTubeTranscriptApi, NoTranscriptFound

class YouTubeScraperService:
    def get_channel_id(self, channel_url: str) -> str:
        """Extracts the channel ID from a YouTube channel URL."""
        if "/channel/" in channel_url:
            return channel_url.split("/channel/")[1].split("/")[0]
        elif "/user/" in channel_url:
            raise ValueError("Channel URL in /user/ format not supported yet. Please provide /channel/ URL or channel ID.")
        else:
            raise ValueError("Invalid YouTube channel URL format.")

    def get_latest_videos(self, channel_id: str, timeframe_hours: int = 24) -> list[dict]:
        """Fetches the latest videos from a YouTube channel's RSS feed, filtered by timeframe."""
        base_url = "https://www.youtube.com/feeds/videos.xml?channel_id="
        feed_url = f"{base_url}{channel_id}"
        feed = feedparser.parse(feed_url)

        latest_videos = []
        time_threshold = datetime.now(UTC) - timedelta(hours=timeframe_hours)

        for entry in feed.entries:
            published_date_str = entry.published
            published_date = datetime.fromisoformat(published_date_str.replace('Z', '+00:00'))

            if published_date > time_threshold:
                video_id = entry.yt_videoid
                video_url = entry.link
                title = entry.title
                latest_videos.append({"id": video_id, "title": title, "url": video_url, "published": published_date})
        return latest_videos

    def get_transcript(self, video_id: str) -> str | None:
        """Fetches the transcript for a given YouTube video ID."""
        try:
            transcript_list = YouTubeTranscriptApi()
            transcript = transcript_list.fetch(video_id)
            transcript = " ".join([snippet.text for snippet in transcript.snippets])
            return transcript
        except NoTranscriptFound:
            print(f"No transcript found for video ID: {video_id}")
            return None
        except Exception as e:
            print(f"Error fetching transcript for video ID {video_id}: {e}")
            return None

    def get_videos_with_transcripts(self, channel_id: str, timeframe_hours: int = 24) -> list[dict]:
        """Fetches latest videos and their transcripts for a given channel ID and timeframe."""
        recent_videos = self.get_latest_videos(channel_id, timeframe_hours)
        videos_with_transcripts = []
        for video in recent_videos:
            transcript = self.get_transcript(video["id"])
            if transcript:
                video["transcript"] = transcript
                videos_with_transcripts.append(video)
        return videos_with_transcripts

if __name__ == "__main__":
    # Example Usage for the YouTubeScraperService
    service = YouTubeScraperService()
    channel_id_example = "UCXZCJLdBC09xxGZ6gcdrc6A" # Example Channel ID

    print(f"[Service] Fetching videos and transcripts for channel ID: {channel_id_example}")
    videos_data = service.get_videos_with_transcripts(channel_id_example, timeframe_hours=48) # Check last 48 hours for demo

    if videos_data:
        print(f"[Service] Found {len(videos_data)} recent videos with transcripts:")
        for video in videos_data:
            print(f"- Title: {video['title']}")
            print(f"  URL: {video['url']}")
            print(f"  Video ID: {video['id']}")
            print(f"  Published: {video['published']}")
            print(f"  Transcript Snippet: {video['transcript'][:200]}...") # Print first 200 chars
            print("\n" + "-"*50 + "\n")
    else:
        print("[Service] No recent videos with transcripts found in the last 48 hours.")
