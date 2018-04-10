# API handles JS and socket requests
# key word: REQUESTS


import flask
from flask_socketio import join_room, send, emit, leave_room

from init import app, db, socketio
import dataBaser


def check_request():
    token = flask.session['csrf_token']
    if flask.request.form['_csrf_token'] != token:
        app.logger.warn('invalid CSRF token')
        flask.abort(400)
    if flask.session.get('auth_user') != flask.g.user.id:
        app.logger.warn('requesting user %s not logged in (%s)',
                        flask.g.user.id,
                        flask.session.get('auth_user'))
        flask.abort(403)


@socketio.on('connect')
def on_connect():
    if 'auth_user' in flask.session:
        user = dataBaser.User.query.get(flask.session['auth_user'])
        app.logger.info('client ' + user.name + ' connected')
    else:
        app.logger.info('unknown client connected')


@socketio.on('disconnect')
def on_disconnect():
    app.logger.info('client disconnected')


# =====================================
#       Game Actions
# =====================================
@socketio.on('incoming_action')
def input_action(data):
    input_user = data['user_name']
    input_action = data['action_name']
    input_key = data['key']

    game = dataBaser.Game.query.filter_by(key=input_key).first()

    participant = dataBaser.Character.query.filter_by(user_name=input_user, game_id=game.id).frst()
    participant.action = input_action

    # Save changes to the database
    db.commit()

    if game.participants[0].action is not None and game.participants[1].action is not None:
        if participant.user_name == game.participants[0].user_name:
            opponent = game.participants[1]

        print("THEY HAVE BOTH ACTED!")

        me_act = participant.action
        you_act = opponent.action
        me_dmg = 0
        you_dmg = 0
        # The actions can either be 'p_attack', 'attack', or 'defense'
        if me_act is 'p_attack' and you_act is 'defense':
            participant.health -= 10
            me_dmg = 10
        elif you_act is 'p_attack' and me_act is 'defense':
            opponent.health -= 10
            you_dmg = 10
        elif me_act is 'attack' and you_act is 'defense':
            participant.health -= 10
            me_dmg = 10
            opponent.health -= 20
            you_dmg = 20
        elif you_act is 'attack' and me_act is 'defense':
            opponent.health -= 10
            you_dmg = 10
            participant.health -= 20
            me_dmg = 20
        elif me_act is 'p_attack' and you_act is 'attack':
            participant.health -= 20
            me_dmg = 20
            opponent.health -= 30
            you_dmg = 30
        elif you_act is 'p_attack' and me_act is 'attack':
            opponent.health -= 20
            you_dmg = 20
            participant.health -= 30
            me_dmg = 30
        # elif me_act is 'defense' and you_act is 'defense':
            # Nothing Happens
        elif me_act is 'attack' and you_act is 'attack':
            participant.health -= 20
            me_dmg = 20
            opponent.health -= 20
            you_dmg = 20
        elif me_act is 'p_attack' and you_act is 'p_attack':
            participant.health -= 30
            me_dmg = 30
            opponent.health -= 30
            you_dmg = 30

        emit('successful_action', {'user_action': participant.action, 'opponent_action': opponent.action,
                                   'user_hp': participant.health, 'opponent_hp': opponent.health,
                                   'me_dmg': me_dmg, 'you_dmg': you_dmg},
             room=input_key)

        # reset current action to default
        participant.action = "Nah"
        opponent.action = "Nah"

        # Save changes to the database
        db.commit()


# =====================================
#       Chat Room Stuff
# =====================================
@socketio.on('join_room')
def user_join(data):
    topic = data['topic']
    user = data['username']
    join_room(room=topic)
    emit('message', user + ' joined the room.', room=topic)
    emit('join_room', {'username': user, 'room': topic}, room=topic)


# @socketio.on('leave_room')
# def user_leave(data):
#     print("disconnected from " + data['topic'])
#     leave_room(room=data['topic'])


# Received json message from the client
@socketio.on('json')
def socket_message(data):
    # in here, 'data' is a Python object parsed from JSON
    user = data['username']
    message = data['msg']
    emit('message', user + ': ' + message, room=data['room'])


# Received string message from the client
@socketio.on('message')
def socket_message(msg):
    # in here, 'msg' is a string
    print("String received")
    print(msg)
    emit('message', msg)
