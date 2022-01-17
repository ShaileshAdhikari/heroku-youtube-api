import os
from dotenv import load_dotenv
from googleapiclient.discovery import build
import psycopg2

load_dotenv()

API = os.getenv("API")
HOST = os.getenv("HOST")
DATABASE = os.getenv("DATABASE")
USER = os.getenv("USER")
PORT = os.getenv("PORT")
PASSWORD = os.getenv("PASSWORD")

api_service_name = "youtube"
api_version = "v3"

reg1 = "(https:\/\/youtu.be\/)[A-Za-z0-9-_]{11}"
reg2 = "(https:\/\/www.youtube.com\/watch\?v=)[A-Za-z0-9-_]{11}"
reg3 = "(https:\/\/www.youtube.com\/watch\?v=)[A-Za-z0-9-_]{11}(&ab_channel=)[A-Za-z0-9-_]+"

def get_db_connection():
    conn = None
    try:
        conn = psycopg2.connect(host=HOST, port=PORT, database=DATABASE,
                                user=USER, password=PASSWORD)
        print("Successfully Connected to SQLite")
    except Exception as e:
        print("CONNECTION ERROR",e)

    return conn

def update_data_entry(sql,task):
    result = False
    try:
        connection = get_db_connection()
        cur = connection.cursor()
        cur.execute(sql,task)
        connection.commit()
        cur.close()
        result = True
    except Exception as e:
        print("UPDATE ERROR",e)
        result = False

    return result

def get_table_initial_entry():

    sql=""" SELECT * FROM initial_entry ORDER BY updated_at ASC """
    connection = get_db_connection()
    cur = connection.cursor()
    result = cur.execute(sql).fetchall()
    cur.close()

    return result

def get_table_playing():

    sql=""" SELECT * FROM playing"""
    connection = get_db_connection()
    cur = connection.cursor()
    result = cur.execute(sql).fetchall()
    cur.close()

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

def add_to_playing(video_id,video_name):
    print("PARAMETER",video_id,video_name)

    sql = """ INSERT INTO playing (video,video_name) VALUES (?,?)"""
    db_update = update_data_entry(sql, (video_id,video_name))
    print(db_update)

    return "OK"

def add_to_initial_entry(v_id,title):
    print("PARAMETER",v_id,title)

    sql = """ INSERT INTO initial_entry (video_id,video_name) VALUES (?,?)"""
    db_update = update_data_entry(sql, (v_id,title))
    print(db_update)

    return "OK"

def add_to_already_played(v_id,v_name):
    print("PARAMETER",v_id,v_name)

    sql = """ INSERT INTO already_played (video_id,video_name) VALUES (?,?)"""
    db_update = update_data_entry(sql, (v_id,v_name))
    print(db_update)

    return "OK"

def remove_entry(sql,data):
    result = False
    try:
        connection = get_db_connection()
        cur = connection.cursor()
        cur.execute(sql,(data,))
        connection.commit()
        cur.close()
        result = True
    except Exception as e:
        print("DELETE ERROR",e)
        result = False

    return result

def truncate(sql):
    result = False
    try:
        connection = get_db_connection()
        cur = connection.cursor()
        cur.execute(sql)
        connection.commit()
        cur.close()
        result = True
    except Exception as e:
        print("TRUNCATE ERROR",e)
        result = False

    return result