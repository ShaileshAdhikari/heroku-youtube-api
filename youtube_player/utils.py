import os
import re
import isodate
from dotenv import load_dotenv
from flask import jsonify
from googleapiclient.discovery import build

load_dotenv()

API = os.getenv('API')

api_service_name = "youtube"
api_version = "v3"

reg1 = "(https:\/\/youtu.be\/)[A-Za-z0-9-_]{11}"
reg2 = "(https:\/\/www.youtube.com\/watch\?v=)[A-Za-z0-9-_]{11}"
reg3 = "(https:\/\/www.youtube.com\/watch\?v=)[A-Za-z0-9-_]{11}(&ab_channel=)[A-Za-z0-9-_]+"

def to_json(data):
    return jsonify([dict(r) for r in data])

name_list = []

def get_a_name():
  import pickle
  import secrets
  global name_list

  if len(name_list) == 0:
    print("Reading the File")
    with open('static/name_list.pkl', 'rb') as f:
      name_list = pickle.load(f)

  return secrets.choice(name_list)

# Checking url with regex and return video_id
def return_vid(vURL):
    p1 = re.compile(reg1)
    p2 = re.compile(reg2)
    p3 = re.compile(reg3)

    if p1.match(vURL):
        return p1.match(vURL)[0].split('/')[-1]
    elif p2.match(vURL):
        return p2.match(vURL)[0].split('=')[-1]
    elif p3.match(vURL):
        return p3.match(vURL)[0].split('=')[1]
    else:
        raise ValueError('Invalid URL:"{}", please check the URL'.format(vURL))

# Database operations (update, delete and turnucate)
def update_data_entry(get_db_connection, sql, task):
    try:
        connection = get_db_connection
        something = connection.execute(sql, task)
        result = {'status':True,
                  'message': 'Successfully updated'}
    except Exception as e:
        print("UPDATE ERROR", e)
        result = {'status':False,
                  'error': str(e)}

    return result

def remove_entry(get_db_connection, sql, data):
    try:
        connection = get_db_connection
        connection.execute(sql, (data,))
        result = {'status': True,
                  'message': 'Successfully deleted'}
    except Exception as e:
        print("DELETE ERROR", e)
        result = {'status': False,
                  'error': str(e)}

    return result

def truncate(get_db_connection, sql):
    result = False
    try:
        connection = get_db_connection
        connection.execute(sql)
        result = True
    except Exception as e:
        print("TRUNCATE ERROR", e)
        result = False

    return result

# Initial table operations
def initial_table_getall(get_db_connection):
    sql = """ SELECT video_id as id,name,thumbnail,duration,updated_at, (
                SELECT username from users WHERE id = updated_by
                )
              FROM initial_entry ORDER BY updated_at ASC """
    return get_db_connection.execute(sql).mappings().fetchall()

def initial_table_gettop(get_db_connection):
    sql = """ SELECT video_id as id,name,thumbnail,duration,updated_at,updated_by
              FROM initial_entry ORDER BY updated_at ASC """
    return get_db_connection.execute(sql).mappings().first()

def add_to_initial_entry(get_db_connection, v_id,v_title,
                         v_time=0, v_thum='a',v_user='Anonymous'):
    print("Add to initial table", v_id, v_title)

    check_sql = """ SELECT id,token,username FROM users WHERE token = %s """
    check_result = get_db_connection.execute(check_sql, (v_user,)).mappings().first()
    user = dict(check_result)['id'] if check_result is not None else 0

    sql = """ INSERT INTO initial_entry (video_id,name,duration,thumbnail,updated_by) 
              VALUES (%s,%s,%s,%s,%s)"""
    db_update = update_data_entry(get_db_connection,
                                  sql,
                                  (v_id, v_title,v_time,v_thum,user))
    print(db_update)

    return db_update

# Playing table operations
def table_playing(get_db_connection):
    sql = """ SELECT video_id as id,name,thumbnail,duration,updated_by,(
                SELECT username from users WHERE id = updated_by
                )
              FROM playing"""
    return get_db_connection.execute(sql).mappings().first()

def add_to_playing(get_db_connection, video_id, name,duration,thumbnail,user):
    print("Add to playing", video_id, name,duration,thumbnail,user)

    sql = """ INSERT INTO playing (video_id,name,duration,thumbnail,updated_by)
              VALUES (%s,%s,%s,%s,%s)"""
    db_update = update_data_entry(get_db_connection, sql,
                                  (video_id, name,duration,thumbnail,user))
    print(db_update)

    return "OK"


# Already played table operations
def most_played(get_db_connection):
    sql = """SELECT video_id as id, name ,duration, thumbnail, played AS count,updated_by,(
                SELECT username from users WHERE id = updated_by
                )
             FROM already_played 
             ORDER BY count DESC LIMIT 5"""

    return get_db_connection.execute(sql).fetchall()

def get_from_already_played(get_db_connection):
    sql = """SELECT video_id as id, name ,updated_at, thumbnail, duration, updated_by
             FROM already_played 
             WHERE updated_at < (CURRENT_TIMESTAMP - 90 * INTERVAL '1 MINUTE')
             ORDER BY updated_at ASC LIMIT 15"""

    return get_db_connection.execute(sql).mappings().first()

def add_to_already_played(get_db_connection, video_id, name,duration,thumbnail,user):
    print("add to already played", video_id, name,duration,thumbnail,user)

    check_sql = """ SELECT video_id FROM already_played WHERE video_id = %s """
    check_result = get_db_connection.execute(check_sql, (video_id,)).mappings().first()

    if check_result is None:
        sql = """ INSERT INTO already_played (video_id,name,duration,thumbnail,updated_by) 
                  VALUES (%s,%s,%s,%s,%s)"""
        db_update = update_data_entry(get_db_connection, sql, (video_id, name,duration,thumbnail,user))
        print(db_update)
        print("New Entry Updated")
    else:
        sql = """ UPDATE already_played 
                  SET updated_at = CURRENT_TIMESTAMP, played = played + 1
                  WHERE video_id = %s """
        db_update = update_data_entry(get_db_connection, sql, (video_id,))
        print(db_update)
        print("Older Entry Updated")

    return "OK"

# Youtube Api Operations
def get_api_connection():
    return build(api_service_name, api_version, developerKey=API)

def get_search_results(query):
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
        return ("SEARCH ERROR", e)

def get_video_name(vid):
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
        return ("ERROR", e)

def get_video_duration(vid):
    request = get_api_connection().videos().list(
        part="contentDetails",
        id=vid,
        fields="items(id,contentDetails(duration))"
    )
    response = request.execute()

    return [{"id": each['id'],
             "duration": each['contentDetails']['duration']
             } for each in response['items']]

# Getting user information if present
def get_user_details(get_db_connection,user_token):

    import hashlib
    import time

    check_sql = """ SELECT token,username FROM users WHERE token = %s """
    check_result = get_db_connection.execute(check_sql, (user_token,)).mappings().first()

    if check_result is None:
        username = get_a_name()
        tk = username+ str(time.time())
        token = hashlib.sha256(tk.encode('utf-8')).hexdigest()

        sql = """ INSERT INTO users (token,username,status) 
                  VALUES (%s,%s,%s)"""
        db_update = update_data_entry(get_db_connection, sql, (token, username,1))
        print(db_update)
        print("New Entry Updated")

        return {
            'status': False,
            'token':dict(get_db_connection.execute(check_sql, (token,)).mappings().first())
        }
    else:
        return {
            'status': True,
            'token': dict(check_result)
        }

def change_user_name(get_db_connection,user_token,new_name):
    sql = """ UPDATE users 
              SET username = %s
              WHERE token = %s """
    db_update = update_data_entry(get_db_connection, sql, (new_name,user_token))
    print(db_update)
    print("Older Entry Updated")
    return db_update
# _____________________________________________________



# def add_to_already_played(get_db_connection, v_id, v_name):
#     print("PARAMETER", v_id, v_name)
#
#     sql = """ INSERT INTO already_played (video_id,video_name) VALUES (%s,%s)"""
#     db_update = update_data_entry(get_db_connection, sql, (v_id, v_name))
#     print(db_update)
#
#     return "OK"



# def get_table_playing(get_db_connection):
#     sql = """ SELECT * FROM playing"""
#     connection = get_db_connection
#     return connection.execute(sql).fetchall()
#
# def get_table_initial_entry(get_db_connection):
#     sql = """ SELECT * FROM initial_entry ORDER BY updated_at ASC """
#     return get_db_connection.execute(sql).fetchall()
