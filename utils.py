import os
from dotenv import load_dotenv
from googleapiclient.discovery import build

load_dotenv()

API = os.getenv("API")

api_service_name = "youtube"
api_version = "v3"

reg1 = "(https:\/\/youtu.be\/)[A-Za-z0-9-_]{11}"
reg2 = "(https:\/\/www.youtube.com\/watch\?v=)[A-Za-z0-9-_]{11}"
reg3 = "(https:\/\/www.youtube.com\/watch\?v=)[A-Za-z0-9-_]{11}(&ab_channel=)[A-Za-z0-9-_]+"

def update_data_entry(get_db_connection,sql,task):
    result = False
    try:
        connection = get_db_connection
        # cur = connection.cursor()
        connection.execute(sql,task)
        # connection.commit()
        # cur.close()
        result = True
    except Exception as e:
        print("UPDATE ERROR",e)
        result = False

    return result

def get_table_initial_entry(get_db_connection):

    sql=""" SELECT * FROM initial_entry ORDER BY updated_at ASC """
    connection = get_db_connection

    result = connection.execute(sql).fetchall()

    return result

def get_table_playing(get_db_connection):

    sql=""" SELECT * FROM playing"""
    connection = get_db_connection
    result = connection.execute(sql).fetchall()


    return result

def get_api_connection():
    return build(api_service_name, api_version, developerKey=API)

def get_search_results(query):
    request = get_api_connection().search().list(
        part="snippet",
        q=query,
        maxResults=5,
        fields="items(etag,id/videoId,snippet(title,thumbnails/default))"
    )
    response = request.execute()

    return [{
            "vid":each['id']['videoId'],
            "vt":each['snippet']['title'],
            "th":each['snippet']['thumbnails']['default']['url'],
        } for each in response['items']]

def get_video_name(vid):
    request = get_api_connection().videos().list(
        part="snippet",
        id=vid,
        fields="items(etag,snippet(title,thumbnails/default))"
    )
    response = request.execute()

    return [{
            "vid":vid,
            "vt":each['snippet']['title'],
            "th":each['snippet']['thumbnails']['default']['url'],
        } for each in response['items']]

def add_to_playing(get_db_connection,video_id,video_name):
    print("PARAMETER",video_id,video_name)

    sql = """ INSERT INTO playing (video,video_name) VALUES (?,?)"""
    db_update = update_data_entry(get_db_connection,sql, (video_id,video_name))
    print(db_update)

    return "OK"

def add_to_initial_entry(get_db_connection,v_id,title):
    print("PARAMETER",v_id,title)

    sql = """ INSERT INTO initial_entry (video_id,video_name) VALUES (?,?)"""
    db_update = update_data_entry(get_db_connection,sql, (v_id,title))
    print(db_update)

    return "OK"

def add_to_already_played(get_db_connection,v_id,v_name):
    print("PARAMETER",v_id,v_name)

    sql = """ INSERT INTO already_played (video_id,video_name) VALUES (?,?)"""
    db_update = update_data_entry(get_db_connection,sql, (v_id,v_name))
    print(db_update)

    return "OK"

def remove_entry(get_db_connection,sql,data):
    result = False
    try:
        connection = get_db_connection
        # cur = connection.cursor()
        connection.execute(sql,(data,))
        # connection.commit()
        # cur.close()
        result = True
    except Exception as e:
        print("DELETE ERROR",e)
        result = False

    return result

def truncate(get_db_connection,sql):
    result = False
    try:
        connection = get_db_connection
        # cur = connection.cursor()
        connection.execute(sql)
        # connection.commit()
        # cur.close()
        result = True
    except Exception as e:
        print("TRUNCATE ERROR",e)
        result = False

    return result