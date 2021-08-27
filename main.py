from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from werkzeug.wrappers import response
from wtforms import StringField, SubmitField, FloatField
from wtforms.validators import InputRequired
import requests
import time
from secret import API

movie_url = 'https://api.themoviedb.org/3/search/movie'
MOVIE_DB_INFO_URL = "https://api.themoviedb.org/3/movie"
MOVIE_DB_IMAGE_URL = "https://image.tmdb.org/t/p/w500"

app = Flask(__name__)
app.config['SECRET_KEY'] = '8BYkEfBA6O6donzWlSihBXox7C0sKR6b'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///movies.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
Bootstrap(app)
db = SQLAlchemy(app)

class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), unique=True, nullable=False)
    year = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String(500), nullable=False)
    rating = db.Column(db.Float)
    ranking = db.Column(db.Float)
    review = db.Column(db.String(250))
    img_url = db.Column(db.String(500), nullable=False)


db.create_all()

class UpdateMovieForm(FlaskForm):
    rating = FloatField('Your rating out of 10. eg 7.5', validators=[InputRequired()])
    review = StringField('Your review', validators=[InputRequired()])
    submit = SubmitField('Done')




@app.route("/")
def home():
    all_movies = Movie.query.order_by(Movie.rating).all()
    for i in range(len(all_movies)):
        all_movies[i].ranking = len(all_movies) - i
    db.session.commit()
    return render_template("index.html", movies=all_movies)

@app.route('/edit/<id>', methods=['GET', 'POST'])
def edit(id):
    form = UpdateMovieForm()
    movie_id = int(id)
    this_movie = Movie.query.get(movie_id)
    if request.method == 'POST':
        if form.validate_on_submit():
            this_movie.rating = form.rating.data
            this_movie.review = form.review.data
            db.session.commit()
            return redirect(url_for('home'))

    return render_template('edit.html', movie=this_movie, form=form)


@app.route('/delete/<id>')
def delete(id):
    movie_id = int(id)
    this_movie = Movie.query.get(movie_id)
    db.session.delete(this_movie)
    db.session.commit()
    return redirect(url_for('home'))

class AddMovieForm(FlaskForm):
    title = StringField('Movie Title', validators=[InputRequired()])
    submit = SubmitField('Add Movie')

@app.route('/add', methods=['GET', 'POST'])
def add():
    form = AddMovieForm()

    if form.validate_on_submit():
        movie_title = form.title.data
        respons = requests.get(movie_url, params={"api_key": API, "query": movie_title})
        data = respons.json()["results"]
        return render_template("select.html", options=data)

    return render_template('add.html', form=form)

@app.route('/select/<id>')
def select(id):
    movie_id = int(id)
    respons = requests.get(f'https://api.themoviedb.org/3/movie/{movie_id}', params={"api_key": API})
    data = respons.json()
    new_movie = Movie(
        title=data["title"],
        year=data["release_date"].split("-")[0],
        img_url=f"{MOVIE_DB_IMAGE_URL}{data['poster_path']}",
        description=data["overview"]
    )
    db.session.add(new_movie)
    db.session.commit()
    return redirect(url_for('edit', id=new_movie.id))


if __name__ == '__main__':
    app.run(debug=True)
