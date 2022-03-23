from flask_sqlalchemy import SQLAlchemy

import os, re
import isodate
from dotenv import load_dotenv
from googleapiclient.discovery import build
from ..models import VideoVault, InitialEntry, CurrentlyPlaying, User
load_dotenv()

API = os.getenv('API')
api_service_name = "youtube"
api_version = "v3"


# Checking url with regex and return video_id
def return_vid(url: str) -> str:
    reg1 = "(https:\/\/youtu.be\/)[A-Za-z0-9-_]{11}"
    reg2 = "(https:\/\/www.youtube.com\/watch\?v=)[A-Za-z0-9-_]{11}"
    reg3 = "(https:\/\/www.youtube.com\/watch\?v=)[A-Za-z0-9-_]{11}(&ab_channel=)[A-Za-z0-9-_]+"

    p1 = re.compile(reg1)
    p2 = re.compile(reg2)
    p3 = re.compile(reg3)

    if p1.match(url):
        return p1.match(url)[0].split('/')[-1]
    elif p2.match(url):
        return p2.match(url)[0].split('=')[-1]
    elif p3.match(url):
        return p3.match(url)[0].split('=')[1]
    else:
        raise ValueError(f'Invalid URL:"{url}", please check the URL')


# Database Operations
def db_addition(db: SQLAlchemy,dataObject):
    try:
        db.session.add(dataObject)
    except Exception as e:
        print("error:", e)
        return False
    else:
        db.session.commit()
        return True

# Working on Video Vault Table
def insert_to_video_vault(
        video_id: str, name: str, thumbnail: str,
        duration: str, added_by: str, db: SQLAlchemy) -> dict:
    """
    Inserts video details into the database VideoVault.
    """
    exist = db.session.query(VideoVault).filter_by(video_id=video_id).first()
    if exist:
        return {"video_id": exist.id}

    vaultObject = VideoVault(
        video_id=video_id, name=name, thumbnail=thumbnail,
        duration=duration, added_by=added_by
    )
    return (
        {"video_id": vaultObject.id}
        if db_addition(db, vaultObject)
        else {"video_id": False}
    )


def get_detail_from_vault(vault_id: list) -> dict:
    """
    Gets video details from the database VideoVault.
    """
    for each in vault_id:
        video = VideoVault.query.filter_by(id=each.vault_id).first()
        if video:
            yield {
                "video_id": video.video_id,
                "name": video.name,
                "thumbnail": video.thumbnail,
                "duration": video.duration,
                "added_by": User.query.filter_by(id=video.added_by).first().username
            }
        else:
            yield {"video_id": False}

# Working on Initial Entry Table
def get_initial_entry() -> list:
    """
    Gets videos from initial entry.
    """
    result = get_detail_from_vault(
        InitialEntry.query.all()
    )
    return list(result)


def insert_to_initial_entry(vault_id: int, db: SQLAlchemy) -> bool:
    """
    Inserts video into the initial entry.
    """
    initialObject = InitialEntry(vault_id=vault_id)
    return bool(db_addition(db, initialObject))

def remove_from_initial_entry(vault_id: int, db: SQLAlchemy) -> dict:
    """
    Removes video from the initial entry.
    """
    pass

def get_playing() -> list:
    """
    Gets currently playing video.
    """
    result = get_detail_from_vault(
        CurrentlyPlaying.query.all()
    )
    return list(result)

# Working with YouTube APIs
def get_api_connection() -> build:
    return build(api_service_name, api_version, developerKey=API)


def get_search_results(query: str) -> list:
    try:
        request = get_api_connection().search().list(
            part="snippet",
            q=query,
            maxResults=10,
            type="video",
            fields="items(etag,id/videoId,snippet(title,thumbnails/high))"
        )
        response = request.execute()
        video_id = [each['id']['videoId'] for each in response['items']]
        mapper = get_video_duration(video_id)

        for item in response['items']:
            for m in mapper:
                if item['id']['videoId'] == m['id']:
                    item['duration'] = isodate.parse_duration(m['duration'])

        return [{
            "id": each['id']['videoId'],
            "name": each['snippet']['title'],
            "duration": each['duration'],
            "thumbnail": each['snippet']['thumbnails']['default']['url'],
        } for each in response['items']]
    except Exception as e:
        return [{"SEARCH ERROR": e}]


def get_video_name(vid: str) -> list:
    try:
        request = get_api_connection().videos().list(
            part="snippet,contentDetails",
            id=vid,
            fields="items(etag,snippet(title,thumbnails/high),contentDetails(duration))"
        )
        response = request.execute()

        return [{
            "id": vid,
            "name": each['snippet']['title'],
            "duration": isodate.parse_duration(each['contentDetails']['duration']),
            "thumbnail": each['snippet']['thumbnails']['default']['url'],
        } for each in response['items']]
    except Exception as e:
        return [{"ERROR": e}]


def get_video_duration(vid: list) -> list:
    request = get_api_connection().videos().list(
        part="contentDetails",
        id=vid,
        fields="items(id,contentDetails(duration))"
    )
    response = request.execute()

    return [{"id": each['id'],
             "duration": each['contentDetails']['duration']
             } for each in response['items']]
