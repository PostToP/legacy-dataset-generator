import requests
import json
from dotenv import load_dotenv
import os

load_dotenv()

API_KEY = os.getenv("YOUTUBE_API_KEY")
if not API_KEY:
    print(
        "YouTube API key not found in environment variables. Please set YOUTUBE_API_KEY in .env file.")
    exit()


POSTTOP_URL = os.getenv("POSTTOP_URL")
if not POSTTOP_URL:
    print(
        "PostTop URL not found in environment variables. Please set POSTTOP_URL in .env file.")
    exit()


def get_youtube_video_details(video_id):
    base_url = "https://youtube.googleapis.com/youtube/v3/videos"
    params = {
        "part": ["snippet", "topicDetails", "localizations", "contentDetails"],
        "id": video_id,
        "key": API_KEY
    }

    response = requests.get(base_url, params=params)

    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
        return None


def extract_video_data(item):
    id = item["id"]
    title = item["snippet"]["title"]
    description = item["snippet"]["description"]
    artist = item["snippet"]["channelTitle"]
    duration = item["contentDetails"]["duration"]
    language = item["snippet"].get("defaultAudioLanguage", None)
    if "topicDetails" in item:
        topics = item["topicDetails"].get("topicCategories", [])
    else:
        topics = []
    category = item["snippet"]["categoryId"]
    if "localizations" in item:
        en_localization = item["localizations"].get("en", {})
        en_gb_localization = item["localizations"].get("en-GB", {})
        en_us_localization = item["localizations"].get("en-US", {})
        jp_localization = item["localizations"].get("ja", {})
        hu_localization = item["localizations"].get("hu", {})
    else:
        en_localization = {}
        en_gb_localization = {}
        en_us_localization = {}
        jp_localization = {}
        hu_localization = {}
    return {
        "id": id,
        "title": title,
        "description": description,
        "artist": artist,
        "duration": duration,
        "language": language,
        "topics": topics,
        "category": category,
        "en_localization": en_localization,
        "en_gb_localization": en_gb_localization,
        "en_us_localization": en_us_localization,
        "jp_localization": jp_localization,
        "hu_localization": hu_localization
    }


def is_valid_video_id(video_id):
    return video_id and video_id != "null" and video_id.strip() and len(video_id) == 11 and all(
        c in 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_' for c in video_id)


def fetch_video_ids_from_posttop():
    response = requests.get(POSTTOP_URL+"/debug")
    json_data = response.json()
    videos = json_data["video"]
    videoIDs = [video["ID"] for video in videos]
    videoIDs = [video for video in videoIDs if is_valid_video_id(video)]
    return videoIDs


def chunk_list(lst, chunk_size):
    return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]


print("Fetching video IDs from PostTop...")
video_ids_from_posttop = fetch_video_ids_from_posttop()
chunked_videos = chunk_list(video_ids_from_posttop, 50)

print("Fetching video details from YouTube...")
current_chunk = 0
total_chunks = len(chunked_videos)
data = []
for chunk in chunked_videos:
    current_chunk += 1
    print(f"Processing chunk {current_chunk+1}/{total_chunks}...")
    result = get_youtube_video_details(chunk)
    for item in result["items"]:
        data.append(extract_video_data(item))

print("Exporting details to data.json...")
with open(f"data.json", "w") as json_file:
    json.dump(data, json_file, indent=4)
print(f"Details exported to exp_details.json")
