import os
from flask import Flask, request, jsonify, render_template
from flask_restful import Api, Resource
from flask_sqlalchemy import SQLAlchemy
from http import HTTPStatus
from flask_migrate import Migrate

db_host = os.environ.get('DB_HOST', default='localhost')
db_name = os.environ.get('DB_NAME', default='movies')
db_user = os.environ.get('DB_USERNAME', default='movies')
db_password = os.environ.get('DB_PASSWORD', default='')
db_port = os.environ.get('DB_PORT', default='5432')

class Config:
    SQLALCHEMY_DATABASE_URI = f"postgresql+psycopg2://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"


class DevelopmentConfig(Config):
    SQLALCHEMY_DATABASE_URI = f"postgresql+psycopg2://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"


class ProductionConfig(Config):
    uri = os.environ.get("DATABASE_URL")
    if uri and uri.startswith("postgres://"):
        uri = uri.replace("postgres://", "postgresql://", 1)
    SQLALCHEMY_DATABASE_URI = uri


env = os.environ.get("ENV", "Development")


if env == "Production":
    config_string = ProductionConfig
else:
    config_string = DevelopmentConfig


app = Flask(__name__)


app.config.from_object(config_string)

api = Api(app)

db = SQLAlchemy(app)

migrate = Migrate(app, db)


class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)  # this is the primary key
    title = db.Column(db.String(80), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    genre = db.Column(db.String(80), nullable=False)

    @staticmethod
    def add_movie(title, year, genre):
        new_movie = Movie(title=title, year=year, genre=genre)
        db.session.add(new_movie)
        db.session.commit()

    @staticmethod
    def get_one_movie(id):
        my_movie = Movie.query.filter_by(id=id).first()
        return my_movie

    @staticmethod
    def delete_movie(id):
        my_movie = Movie.query.filter_by(id=id).delete()
        return my_movie

    @staticmethod
    def get_movie():
        return Movie.query.all()

    @staticmethod
    def update_movie(id):
        updated_data = Movie.query.filter_by(id=id).update(request.get_json())
        db.session.commit()
        return updated_data


class AllMovies(Resource):
    def post(self):
        data = request.get_json()
        print(data)
        Movie.add_movie(title=data["title"], year=data["year"], genre=data["genre"])
        return {"status": HTTPStatus.OK}

    def get(self):
        data = Movie.get_movie()
        movielist = []

        for i in data:
            temp_dict = {'title': i.title, 'year': i.year, 'genre': i.genre}
            movielist.append(temp_dict)
        return jsonify((movielist), {"status": HTTPStatus.OK})


class OneMovie(Resource):
    def get(self, id):
        data = Movie.get_one_movie(id)
        print(data)
        if data:
            movie_dict = {"title": data.title, "year": data.year, "genre": data.genre}
            return jsonify((movie_dict), {"status": HTTPStatus.OK})
        else:
            return {"message": "ID not found", "status": HTTPStatus.NOT_FOUND}

    def delete(self, id):
        data = Movie.delete_movie(id)
        if data:
            return HTTPStatus.OK
        else:
            return HTTPStatus.NOT_FOUND

    def put(self, id):
        new_data = Movie.update_movie(id)
        print(new_data)
        data = Movie.get_movie()
        print(data)
        if data:
            movie_list = []
            for movie in data:
                movie_list.append({"title": movie.title, "year": movie.year, "genre": movie.genre})
            return jsonify((movie_list), {"status": HTTPStatus.OK})
        else:
            return {"message": "ID not found", "status": HTTPStatus.NOT_FOUND}


api.add_resource(AllMovies, "/movies")
api.add_resource(OneMovie, "/movies/<int:id>")


@app.route('/')
def entry_page():
    return render_template("index.html")


if __name__ == "__main__":
    app.run()
