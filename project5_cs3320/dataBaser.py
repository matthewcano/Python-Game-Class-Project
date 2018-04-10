from init import db, app


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(20))
    pw_hash = db.Column(db.String(64))

    photo = db.Column(db.BLOB)
    photo_type = db.Column(db.String(50))


class Game(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    key = db.Column(db.String(20))
    participants = db.relationship('Character', backref='game')


class Character(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_name = db.Column(db.String(20))

    health = db.Column(db.Integer)
    action = db.Column(db.String(20))

    game_id = db.Column(db.Integer, db.ForeignKey('game.id'))


db.create_all(app=app)
