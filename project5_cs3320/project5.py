from init import app, socketio

import viewer, viewer_auth, api

if __name__ == '__main__':
    socketio.run(app, debug=True)
