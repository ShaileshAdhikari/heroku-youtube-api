from datetime import datetime

from flask import session, flash, request, render_template, jsonify
from youtube_player import app
from youtube_player.models import User, db
from youtube_player.decorators import logged_in
from .helpers import db_addition

@app.route("/auth/me",methods=['GET'])
@logged_in
def me():
    records = User.query
    return jsonify({
        'success':True,
        "result":{
            'username': session['username'],'email': session['email'],
            'token': records.where(User.email == session['email']).first().token
        }
        })

@app.route('/auth/register',methods=['POST','GET'])
def register():
    records = User.query

    if request.method != 'POST':
        return render_template('register.html')

        # return jsonify({
        #     'success': False,
        #     'result': {'error': 'Invalid request'}
        # })
    data = request.get_json()
    username = data['username']
    email = data['email']
    password = data['password']
    if records.filter_by(email = email).first() is not None:
        app.logger.warning('User already exists')
        return jsonify({
            'success': False,
            'result':{'error': 'Email already registered'},
        })
    db.session.add(User(username=username, email=email, password=password))
    db.session.commit()
    app.logger.info(f'New User registered {email}|{username}')
    return jsonify({
        'success': True,
        'result':{'message': 'Registered Successfully !'},
    })

@app.route("/auth/login",methods=['POST','GET'])
def login():

    if request.method != 'POST':
        return render_template('login.html')
        # return jsonify({
        #     'success': False,
        #     'result':{'error': 'Invalid request'},
        # })

    records = User.query
    data = dict(request.form)
    email = data['user-email']
    password = data['user-password']
    if len(email) != 0 and len(password) != 0:
        login_user = records.filter_by(email = email, password = password).first()
        if login_user is None:
            app.logger.warning(f'Invalid credentials: {email}')

            flash('Email or Password is incorrect. Try Again !','error')
            return render_template('login.html')
            # return jsonify({
            #     'success': False,
            #     'result':{'error': 'Invalid credentials'}
            # })
    else:
        flash('Email or Password is required.','error')
        return render_template('login.html')
        # return jsonify({
        #     'success': False,
        #     'result':{'error': 'Invalid credentials'}
        # })
    session['logged_in'] = True
    session['username'] = login_user.username
    session['email'] = login_user.email

    login_user.last_login = datetime.now()
    db_addition(db,login_user)

    app.logger.info(f'User logged in: {email}')
    # return jsonify({
    #     'success': True,
    #     "result": {
    #         'username': session['username'], 'email': session['email'],
    #         'token': login_user.cookie
    #     }
    # })
    return render_template('index.html')


@app.route('/auth/logout',methods=['POST'])
@logged_in
def logout():
    session['logged_in'] = False
    app.logger.info(f'User logged out: {session["email"]}')
    session.pop('username', None)
    session.pop('email', None)
    # return jsonify({
    #     'success': True, 'result': {'message':'Logged out'}
    # })
    return render_template('index.html')

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html', error=e), 404