import flask
import bcrypt
import re
import io

from init import app, db
import dataBaser


# =====================================================================================================================
# LOGIN / LOGOUT USER HANDLING
# =====================================================================================================================
@app.route('/login')
def login_form():
    # GET request to /login - send the login form
    return flask.render_template('login.html')


@app.route('/login', methods=['POST'])
def handle_login():
    # POST request to /login - check user
    name = flask.request.form['username']
    password = flask.request.form['password']
    # try to find user
    user = dataBaser.User.query.filter_by(name=name).first()

    if user is not None:
#        # hash the password the user gave us
#        #  for verifying, we use their real hash as the salt
        pw_hash = bcrypt.hashpw(password.encode('utf8'), user.pw_hash)
        # is it good?
        if pw_hash == user.pw_hash:
               # yay!
               flask.session['auth_user'] = user.id
               # And redirect to '/', since this is a successful POST
               return flask.redirect(flask.url_for('index'), code=303)


    # if we got this far, either username or password is no good
    # For an error in POST, we'll just re-show the form with an error message
    return flask.render_template('login.html', error_msg="Invalid username or password")


@app.route('/create_user', methods=['POST'])
def create_user():
    name = flask.request.form['username']
    password = flask.request.form['password']

    file = flask.request.files['image']
    photo_type = None
    photo_data = None

    if file.filename != '':
        if not file.mimetype.startswith('image/'):
            # oops
            # in a good app, you provide a useful error message...
            flask.abort(400, "file.filename is not empty, but isn't an image.")
    else:
        file = None

    # do the passwords match?
    error = None
    if password != flask.request.form['confirm_password']:
        error = "Passwords don't match"
    # is the login ok?
    if len(name) > 60:
        error = "Username too long"
    if not re.match(r"^[A-Za-z0-9\.\+_-]*$", name):
        error = "Username contains invalid characters"

    # search for existing user
    existing = dataBaser.User.query.filter_by(name=name).first()

    if existing is not None:
        # oops, found your doppelgänger
        error = "Username already taken"

    if error:
        return flask.render_template('login.html', error_msg=error)

    # create user
    user = dataBaser.User()
    user.name = name
    # hash password
    user.pw_hash = bcrypt.hashpw(password.encode('utf8'), bcrypt.gensalt(15))

    if file is not None:
        user.photo_type = file.mimetype
        photo_data = io.BytesIO()
        file.save(photo_data)
        # now, we put the data into the model object
        user.photo = photo_data.getvalue()

    # save user
    db.session.add(user)
    db.session.commit()

    flask.session['auth_user'] = user.id

    # It's all good!
    return flask.redirect(flask.url_for('index'), 303)


@app.route('/logout')
def handle_logout():
    # user wants to say goodbye, just forget about them
    del flask.session['auth_user']
    del flask.g.user
    # redirect to specified source URL, or / if none is present
    return flask.redirect(flask.url_for('index'), code=303)

