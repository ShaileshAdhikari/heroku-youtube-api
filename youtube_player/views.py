from flask import session, Response, request, render_template, jsonify
from youtube_player import app
from youtube_player.models import *
from .decorators import logged_in

@app.route("/auth/me",methods=['GET'])
def me():

    if not session.get('logged_in'):
        return jsonify({
                'success':False,
                'result':{'error':'Not logged in'}
            })

    records = User.query
    return jsonify({
        'success':True,
        "result":{
            'username': session['username'],'email': session['email'],
            'token': records.where(User.email == session['email']).first().token
        }
        })

@app.route('/auth/register',methods=['POST'])
def register():
    records = User.query

    if request.method != 'POST':
        return jsonify({
            'success': False,
            'result': {'error': 'Invalid request'}
        })
    data = request.get_json()
    username = data['username']
    email = data['email']
    password = data['password']
    if records.filter_by(email = email).first() is not None:
        return jsonify({
            'success': False,
            'result':{'error': 'Email already registered'},
        })
    db.session.add(User(username=username, email=email, password=password))
    db.session.commit()
    return jsonify({
        'success': True,
        'result':{'message': 'Registered Successfully !'},
    })

@app.route("/auth/login",methods=['POST'])
def login():
    records = User.query

    if request.method != 'POST':
        return jsonify({
            'success': False,
            'result':{'error': 'Invalid request'},
        })
    data = request.get_json()
    email = data['email']
    password = data['password']

    login_user = records.filter_by(email = email, password = password).first()
    if login_user is None:
        return jsonify({
            'success': False,
            'result':{'error': 'Invalid credentials'}
        })
    session['logged_in'] = True
    session['username'] = login_user.username
    session['email'] = login_user.email
    return jsonify({
        'success': True,
        "result": {
            'username': session['username'], 'email': session['email'],
            'token': login_user.cookie
        }
    })


@app.route('/auth/logout',methods=['POST'])
@logged_in
def logout():
    session['logged_in'] = False
    return Response({
        'success': True, 'result': {'message':'Logged out'}
    })

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html',redirect='/',error=e), 404