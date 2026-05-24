from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
import logic

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(100), nullable = False)
    email = db.Column(db.String(100), nullable = False)

    def __repr__(self):
        return '<User %r>' % self.id

class Conversion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    youtube_url = db.Column(db.String(500))
    spotify_playlist_id = db.Column(db.String(200))


@app.route('/', methods=['POST', 'GET'])
def index():
    if request.method == 'POST':
        link = request.form["playlist"]
        genre = request.form["genre"]

        youtube_list, spotify_list = logic.main(link, genre)
        return render_template(
            'index.html',
            youtube_list=youtube_list,
            spotify_list=spotify_list
        )

    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)