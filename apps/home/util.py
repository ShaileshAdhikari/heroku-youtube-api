import itertools

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime,timedelta
import os, re
import isodate
from dotenv import load_dotenv
from googleapiclient.discovery import build
from .models import VideoVault, InitialEntry, CurrentlyPlaying
from apps.authentication.models import Users
load_dotenv()

API = os.getenv('API')
api_service_name = "youtube"
api_version = "v3"


def peek(iterable):
    try:
        first = next(iterable)
    except StopIteration:
        return None, None
    return first, itertools.chain([first], iterable)

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
        # raise ValueError(f'Invalid URL:"{url}", please check the URL')
        return 'InvalidURL'


# Database Operations
def db_addition(db: SQLAlchemy, dataObject):
    try:
        db.session.add(dataObject)
    except Exception as e:
        print("error:", e)
        return False
    else:
        db.session.commit()
        return True

def db_deletion(db: SQLAlchemy, dataObject):
    try:
        db.session.delete(dataObject)
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


# Get video details from video vault with vault_id
def get_detail_from_vault(vault_id: list) -> dict:
    """
    Gets video details from the database VideoVault.
    """
    if vault_id:
        for each in vault_id:
            video = VideoVault.query.filter_by(id=each.vault_id).first()
            if video:
                yield {
                    "vault_id": video.id,
                    "video_id": video.video_id,
                    "name": video.name,
                    "thumbnail": video.thumbnail,
                    "duration": video.duration,
                    "added_by": Users.query.filter_by(id=video.added_by).first().username
                }
            else:
                yield {"video_id": False}
    else:
        yield {"video_id": False}


def get_video_from_vault():
    """
    Gets video from the database VideoVault.
    """
    video = VideoVault.query.filter(
        VideoVault.last_played_on <= (datetime.now() - timedelta(minutes=90))
    )
    if video.first() is not None:
        result = video.order_by(VideoVault.play_count).first()
        yield {
            "vault_id": result.id,
            "video_id": result.video_id,
            "name": result.name,
            "thumbnail": result.thumbnail,
            "duration": result.duration,
            "added_by": Users.query.filter_by(id=result.added_by).first().username
        }
    else:
        return [None]

def update_video_vault_count(vault_id: str, db: SQLAlchemy) -> bool:
    # sourcery skip: use-named-expression
    """
    Updates video count in the database VideoVault.
    """
    video = VideoVault.query.filter_by(id=vault_id).first()
    if video:
        video.play_count += 1
        return db_addition(db, video)
    return False

def get_most_played() -> list:
    """
    Gets most played video from the database VideoVault.
    """
    video = VideoVault.query.order_by(VideoVault.play_count.desc()).first()
    if video:
        return [{
            "vault_id": video.id,
            "video_id": video.video_id,
            "name": video.name,
            "thumbnail": video.thumbnail,
            "duration": video.duration,
            "added_by": Users.query.filter_by(id=video.added_by).first().username
        }]
    else:
        return [None]

def get_all_from_video_vault() -> list:
    """
    Gets all videos from the database VideoVault.
    """
    video = VideoVault.query.all()
    if video:
        return [{
            "vault_id": video.id,
            "video_id": video.video_id,
            "name": video.name,
            "thumbnail": video.thumbnail,
            "duration": video.duration,
            "added_by": Users.query.filter_by(id=video.added_by).first().username,
            "counts":video.play_count
        } for video in video]
    else:
        return [None]

# Working on Initial Entry Table
def get_initial_entry(get_one: bool = False) -> list:
    """
    Gets videos from initial entry.
    :param get_one: To get one video or all videos
    """
    result = get_detail_from_vault(
        InitialEntry.query.order_by(InitialEntry.added_on).all()
    )
    check,generator = peek(result)
    if not check['video_id']:
        return []
    else:
        return [check] if get_one else list(generator)


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
    res = list(result)
    if res[0]['video_id']:
        return res
    else:
        return [None]


# Working with YouTube APIs
def get_api_connection() -> build:
    return build(api_service_name, api_version, developerKey=API)


def get_search_results(query: str) -> list:
    """ Gets search results from YouTube. """
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
            "duration": str(each['duration']),
            "thumbnail": each['snippet']['thumbnails']['high']['url'],
        } for each in response['items']]
    except Exception as e:
        return [{"SEARCH ERROR": e}]


def get_video_name(vid: str,db: SQLAlchemy) -> list:
    """ Gets video name from YouTube. """
    exist = db.session.query(VideoVault).filter_by(video_id=vid).first()
    if exist:
        return [{
            "id": vid,
            "name": exist.name,
            "duration": exist.duration,
            "thumbnail": exist.thumbnail,
        }]
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
            "duration": str(isodate.parse_duration(each['contentDetails']['duration'])),
            "thumbnail": each['snippet']['thumbnails']['high']['url'],
        } for each in response['items']]
    except Exception as e:
        return [{"ERROR": e}]


def get_video_duration(vid: list) -> list:
    """ Gets video duration from YouTube. """
    request = get_api_connection().videos().list(
        part="contentDetails",
        id=vid,
        fields="items(id,contentDetails(duration))"
    )
    response = request.execute()

    return [{"id": each['id'],
             "duration": each['contentDetails']['duration']
             } for each in response['items']]


def clean_playings(db: SQLAlchemy) -> bool:
    """ Cleans the currently playing table. """
    db.session.query(CurrentlyPlaying).delete()
    db.session.commit()
    return True
