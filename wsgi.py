from youtube_player import app
import os

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5005))
    app.run(host='localhost', debug=False)