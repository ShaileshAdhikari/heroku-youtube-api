from flask import session, Response, request, render_template
from youtube_player import app
from youtube_player.models import *

@app.route("/auth/me",methods=['GET'])
def index():
    records = User.select()

    if session.get('logged_in'):
        return Response(
            response={
                'username': session['username'],
                'email': session['email'],
                'token': records.where(User.email == session['email']).get().token
            },
            status=200,mimetype='application/json'
        )
    else:
        return Response(
            response={'error': 'Not logged in'},
            status=401,mimetype='application/json'
        )

@app.route('/auth/register',methods=['POST'])
def register():
    records = User.select()

    if request.method != 'POST':
        return Response(
            response={'error': 'Invalid request'},
            status=401,mimetype='application/json'
        )
    username = request.form['username']
    email = request.form['email']
    password = request.form['password']
    if records.where(User.email == email).exists():
        return Response(
            response={'error': 'Email already registered'},
            status=401,mimetype='application/json'
        )
    new_user = User.create(username=username, email=email, password=password)
    new_user.save()
    return Response(
        response={'success': 'Registered'},
        status=200,mimetype='application/json'
    )

@app.route("/auth/login",methods=['POST'])
def login():
    records = User.select()

    if request.method != 'POST':
        return Response(
            response={'error': 'Invalid request'},
            status=401,mimetype='application/json'
        )
    email = request.form['email']
    password = request.form['password']
    login_user = records.where(User.email == email, User.password == password).get()
    if login_user.exists():
        session['logged_in'] = True
        session['username'] = login_user['username']
        session['email'] = email
        return Response(
            response={'success': 'Logged in'},
            status=200,mimetype='application/json'
        )
    else:
        return Response(
            response={'error': 'Invalid credentials'},
            status=401,mimetype='application/json'
        )

@app.route('/auth/logout')
def logout():
    session['logged_in'] = False
    return Response(
        response={'success': 'Logged out'},
        status=200,mimetype='application/json'
    )

@app.errorhandler(404)
def page_not_found(e):
    return render_template('../templates/404.html'), 404