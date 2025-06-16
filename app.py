from flask import Flask, request
from flask_restx import Api, Resource
from flask_sqlalchemy import SQLAlchemy
from marshmallow import Schema, fields


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

api = Api(app)
movie_ns = api.namespace('/movies')
directors_ns = api.namespace('/directors')
genres_ns = api.namespace('/genres')


class Movie(db.Model):
    __tablename__ = 'movie'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    description = db.Column(db.String(255))
    trailer = db.Column(db.String(255))
    year = db.Column(db.Integer)
    rating = db.Column(db.Float)
    genre_id = db.Column(db.Integer, db.ForeignKey("genre.id"))
    genre = db.relationship("Genre")
    director_id = db.Column(db.Integer, db.ForeignKey("director.id"))
    director = db.relationship("Director")

class Director(db.Model):
    __tablename__ = 'director'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))


class Genre(db.Model):
    __tablename__ = 'genre'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))

class MovieSchema(Schema):
    id = fields.Int()
    title = fields.Str()
    description = fields.Str()
    trailer = fields.Str()
    year = fields.Int()
    rating = fields.Float()
    genre_id = fields.Int()
    director_id = fields.Int()

class DirectorSchema(Schema):
    id = fields.Int()
    name = fields.Str()

class GenreSchema(Schema):
    id = fields.Int()
    name = fields.Str()


movie_schema = MovieSchema()
movies_schema = MovieSchema(many=True)

director_schema = DirectorSchema()
directors_schema = DirectorSchema(many=True)

genre_schema = GenreSchema()
genres_schema = GenreSchema(many=True)

"""  Возвращает список всех фильмов, добавляет кино в фильмотеку.
     Возвращает конкретный фильм по режиссеру и/или жанру.  """
@movie_ns.route('/')
class MovieView(Resource):
    def get(self):
        director_id = request.args.get("director_id")
        genre_id = request.args.get("genre_id")
        if director_id and genre_id:
            try:
                movie = db.session.query(Movie).filter(Movie.director_id == director_id, Movie.genre_id == genre_id).first()
                return movie_schema.dump(movie), 200
            except Exception as e:
                return {'error': str(e)}, 404
        if director_id:
            try:
                movie = db.session.query(Movie).filter(Movie.director_id == director_id).first()
                return movie_schema.dump(movie), 200
            except Exception as e:
                return {'error': str(e)}, 404
        if genre_id:
            try:
                movie = db.session.query(Movie).filter(Movie.genre_id == genre_id).first()
                return movie_schema.dump(movie), 200
            except Exception as e:
                return {'error': str(e)}, 404
        else:
            all_movies = Movie.query.all()
            if all_movies:
                try:
                    return movies_schema.dump(all_movies), 200
                except Exception as e:
                    return {'error': str(e)}, 404
            else:
                return "В таблице ничего нет"

    def post(self):
        req_json = request.json
        new_movie = Movie(**req_json)

        with db.session.begin():
            db.session.add(new_movie)
            db.session.commit()
        return "", 201

"""  Возвращает информацию о конкретном фильме (по номеру), 
        обновляет и удаляет конкретный фильм  """
@movie_ns.route('/<int:uid>')
class MovieView(Resource):
    def get(self, uid):
        movie = Movie.query.get(uid)
        if movie:
            try:
                return movie_schema.dump(movie), 200
            except Exception as e:
                return {'error': str(e)}, 404
        else:
            return "Фильма с таким id не существует"

    def put(self, uid):
        movie = Movie.query.get(uid)
        if not movie:
            return "", 404
        req_json = request.json

        movie.title = req_json.get("title")
        movie.description = req_json.get("description")
        movie.trailer = req_json.get("trailer")
        movie.year = req_json.get("year")
        movie.rating = req_json.get("rating")
        movie.genre_id = req_json.get("genre_id")
        movie.director_id = req_json.get("director_id")

        db.session.add(movie)
        db.session.commit()
        return "", 204

    def patch(self, uid):
        movie = Movie.query.get(uid)
        if not movie:
            return "", 404
        req_json = request.json

        if "title" in req_json:
            movie.title = req_json.get("title")
        if "description" in req_json:
            movie.description = req_json.get("description")
        if "trailer" in req_json:
            movie.trailer = req_json.get("trailer")
        if "year" in req_json:
            movie.year = req_json.get("year")
        if "rating" in req_json:
            movie.rating = req_json.get("rating")
        if "genre_id" in req_json:
            movie.genre_id = req_json.get("genre_id")
        if "director_id" in req_json:
            movie.director_id = req_json.get("director_id")

        db.session.add(movie)
        db.session.commit()
        return "", 204

    def delete(self, uid):
        movie = Movie.query.get(uid)
        if movie:
            try:
                db.session.delete(movie)
                return f"Фильм номер {uid} удален!"
            except Exception as e:
                return {'error': str(e)}, 404
        else:
            return "Фильма с таким id не существует"

#-------------------------------------------------------------------------------
@directors_ns.route('/')    # Возвращает список всех режиссеров
class DirectorView(Resource):
    def get(self):
        all_directors = Director.query.all()
        if all_directors:
            try:
                return directors_schema.dump(all_directors), 200
            except Exception as e:
                return {'error': str(e)}, 404
        else:
            return "В таблице ничего нет"

"""  Возвращает информацию о конкретном режиссере по его номеру в БД  """
@directors_ns.route('/<int:uid>')
class DirectorView(Resource):
    def get(self, uid):
        director = Director.query.get(uid)
        if director:
            try:
                return director_schema.dump(director), 200
            except Exception as e:
                return {'error': str(e)}, 404
        else:
            return "Режиссера с таким id не существует"

#-------------------------------------------------------------------------------
@genres_ns.route('/')    # Возвращает список всех жанров
class GenreView(Resource):
    def get(self):
        all_genress = Genre.query.all()
        if all_genress:
            try:
                return genres_schema.dump(all_genress), 200
            except Exception as e:
                return {'error': str(e)}, 404
        else:
            return "В таблице ничего нет"

"""  Возвращает информацию о конкретном жанре по его номеру в БД  """
@genres_ns.route('/<int:uid>')
class GenresView(Resource):
    def get(self, uid):
        genre = Genre.query.get(uid)
        if genre:
            try:
                return genre_schema.dump(genre), 200
            except Exception as e:
                return {'error': str(e)}, 404
        else:
            return "Жанра с таким номером в базе нет"

if __name__ == '__main__':
    app.run(debug=True)
