import feedparser
from datetime import datetime, timedelta, UTC
from youtube_transcript_api import YouTubeTranscriptApi, NoTranscriptFound
from pydantic import BaseModel, HttpUrl

class ChannelVideo(BaseModel):
    id: str
    title: str
    url: HttpUrl
    published: datetime
    transcript: str | None = None

class Transcript(BaseModel):
    text: str

class YouTubeScraperService:
    def get_channel_id(self, channel_url: str) -> str:
        """Extracts the channel ID from a YouTube channel URL."""
        if "/channel/" in channel_url:
            return channel_url.split("/channel/")[1].split("/")[0]
        elif "/user/" in channel_url:
            raise ValueError("Channel URL in /user/ format not supported yet. Please provide /channel/ URL or channel ID.")
        else:
            raise ValueError("Invalid YouTube channel URL format.")

    def get_latest_videos(self, channel_id: str, timeframe_hours: int = 24) -> list[ChannelVideo]:
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
                latest_videos.append(ChannelVideo(id=video_id, title=title, url=video_url, published=published_date))
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

    def get_videos_with_transcripts(self, channel_id: str, timeframe_hours: int =100) -> list[ChannelVideo]:
        """Fetches latest videos and their transcripts for a given channel ID and timeframe."""
        recent_videos_raw = self.get_latest_videos(channel_id, timeframe_hours)
        videos_with_transcripts: list[ChannelVideo] = []
        for video_item in recent_videos_raw:
            transcript_content = self.get_transcript(video_item.id)
            if transcript_content:
                videos_with_transcripts.append(ChannelVideo(id=video_item.id, title=video_item.title, url=video_item.url, published=video_item.published, transcript=transcript_content))
            else:
                videos_with_transcripts.append(video_item) # Append without transcript if not found
        return videos_with_transcripts
