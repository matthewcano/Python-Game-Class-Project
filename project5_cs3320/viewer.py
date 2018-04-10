import io

import flask
import base64, os
from sqlalchemy import or_
import bcrypt
import re
import uuid
from collections import deque

from init import app, db, socketio
import dataBaser


# Create Queue List for those waiting for a game
waiting_list = deque([])


@app.before_request
def setup_csrf():
    # make a cross-site request forgery preventing token
    if 'csrf_token' not in flask.session:
        flask.session['csrf_token'] = base64.b64encode(os.urandom(32)).decode('ascii')


@app.before_request
def setup_user():
    """
    Figure out if we have an authorized user, and look them up.
    This runs for every request, so we don't have to duplicate code.
    """
    if 'auth_user' in flask.session:
        user = dataBaser.User.query.get(flask.session['auth_user'])
        if user is None:
            # old bad cookie, no good
            del flask.session['auth_user']
        # save the user in `flask.g`, which is a set of globals for this request
        flask.g.user = user


@app.route('/')
def index():
    return flask.render_template('index.html')


@app.route('/u/<u_name>')
def user_page(u_name):
    user = dataBaser.User.query.filter_by(name=u_name).first()
    return flask.render_template('user.html', user=user)


# a URL handler to return the photo data
@app.route('/u/<u_name>/photo')
def get_photo(u_name):
    if flask.g.user is None:
        flask.abort(403)
    user = dataBaser.User.query.filter_by(name=u_name).first()

    if user.photo is not None:
        return flask.send_file(io.BytesIO(user.photo))
    else:
        return flask.send_file('static/noavatar.gif')


@app.route('/join_waitlist', methods=['POST'])
def add_wait():
    new_wait = flask.request.form['username']
    waiting_list.append(new_wait)

    # check to see if there are 2 or more people in the waiting list
    if len(waiting_list) > 1:
        user1 = waiting_list.popleft()
        user2 = waiting_list.popleft()
        return flask.redirect(flask.url_for('create_game', user1=user1, user2=user2), code=303)

    return flask.render_template('waitingroom.html')


@app.route('/create_game/<user1>/<user2>')
@app.route('/create_game/')
def create_game(user1, user2):
    # create new game
    game = dataBaser.Game()
    game.key = base64.urlsafe_b64encode(uuid.uuid4().bytes)[:12].decode('ascii')

    # create user1 as participant
    u1 = dataBaser.Character()
    u1.user_name = user1
    u1.health = 10
    u1.action = "Nah"
    u1.game_id = game.id
    game.participants.append(u1)
    # create user2 as participant
    u2 = dataBaser.Character()
    u2.user_name = user2
    u2.health = 10
    u2.action = "Nah"
    u2.game_id = game.id
    game.participants.append(u2)

    # save game to database
    db.session.add(game)
    db.session.add(u1)
    db.session.add(u2)
    db.session.commit()

    url = flask.url_for('go_go_game', key=game.key)
    socketio.emit('two in waitinglist', url, broadcast=True)

    return flask.redirect(flask.url_for('go_go_game', key=game.key), code=303)


@app.route('/g/<key>')
def go_go_game(key):
    game = dataBaser.Game.query.filter_by(key=key).first()
    if flask.g.user is None:
        flask.abort(400)
    user = flask.g.user
    # game_user = dataBaser.Participant.query.filter_by(user_name=user.name, game_id=game.id).frst()
    game_user = None
    opponent = None
    print(len(game.participants))
    for frank in game.participants:
        print("frank name: " + frank.user_name)
        if frank.user_name == user.name:
            game_user = frank
        else:
            opponent = frank

    if game_user is not None:
        return flask.render_template('gameroom.html', chat_key=key, user=game_user, opponent=opponent)
    else:
        flask.abort(403)




