# Elokuvien hallintajarjestelma
# Jarmo Pylkko 250129

import uuid
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flasgger import Swagger, swag_from

app = Flask(__name__)
swagger = Swagger(app)

# Maaritellaan tietokanta
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///elokuvat.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Tietokannan taulun muoto
class Movie(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title = db.Column(db.String(200), nullable=False)
    genre = db.Column(db.String(100), nullable=False)
    releaseYear = db.Column(db.Integer, nullable=False)
    director = db.Column(db.String(150), nullable=False)
    rating = db.Column(db.Integer, nullable=False)

# Luo tietokanta ja taulu
with app.app_context():
    db.create_all()
    
class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    movie_id = db.Column(db.String(36), db.ForeignKey('movie.id'), nullable=False)
    user_name = db.Column(db.String(100), nullable=False)
    review_text = db.Column(db.Text, nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    movie = db.relationship('Movie', backref=db.backref('reviews', lazy=True))

# Luo tietokanta ja taulu
with app.app_context():
    db.create_all()

# Hae kaikki elokuvat
@app.route('/movies', methods=['GET'])
@swag_from({
    'responses': {
        200: {
            'description': 'List of all movies',
            'schema': {
                'type': 'array',
                'items': {
                    'type': 'object',
                    'properties': {
                        'id': {'type': 'string'},
                        'title': {'type': 'string'},
                        'genre': {'type': 'string'},
                        'releaseYear': {'type': 'integer'},
                        'director': {'type': 'string'},
                        'rating': {'type': 'integer'}
                    }
                }
            }
        }
    }
})
def get_movies():
    movies = Movie.query.all()
    return jsonify([{"id": m.id, "title": m.title, "genre": m.genre, "releaseYear": m.releaseYear, "director": m.director, "rating": m.rating} for m in movies])

# Hae yksittainen elokuva
@app.route('/movies/<string:movieId>', methods=['GET'])
@swag_from({
    'responses': {
        200: {
            'description': 'Details of a single movie',
            'schema': {
                'type': 'object',
                'properties': {
                    'id': {'type': 'string'},
                    'title': {'type': 'string'},
                    'genre': {'type': 'string'},
                    'releaseYear': {'type': 'integer'},
                    'director': {'type': 'string'},
                    'rating': {'type': 'integer'}
                }
            }
        },
        404: {
            'description': 'Movie not found',
            'examples': {
                'application/json': {
                    'NOK': 'Elokuvaa ei loydy!'
                }
            }
        }
    }
})
def get_movie(movieId):
    movie = Movie.query.get(movieId)
    if movie:
        return jsonify({"id": movie.id, "title": movie.title, "genre": movie.genre, "releaseYear": movie.releaseYear, "director": movie.director, "rating": movie.rating})
    return jsonify({"NOK": f"Elokuvaa {movieId} ei loydy!"}), 404

# Lisaa uusi elokuva
@app.route('/movies', methods=['POST'])
@swag_from({
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'title': {'type': 'string'},
                    'genre': {'type': 'string'},
                    'releaseYear': {'type': 'integer'},
                    'director': {'type': 'string'},
                    'rating': {'type': 'integer'}
                }
            }
        }
    ],
    'responses': {
        201: {
            'description': 'New movie added',
            'schema': {
                'type': 'object',
                'properties': {
                    'id': {'type': 'string'},
                    'title': {'type': 'string'},
                    'genre': {'type': 'string'},
                    'releaseYear': {'type': 'integer'},
                    'director': {'type': 'string'},
                    'rating': {'type': 'integer'}
                }
            }
        },
        400: {
            'description': 'Invalid input or missing data',
            'examples': {
                'application/json': {
                    'NOK': 'Vaadittu tieto puuttuu: title'
                }
            }
        }
    }
})
def add_movie():
    if request.is_json:
        data = request.get_json()
        try:
            newMovie = Movie(
                title=data['title'],
                genre=data['genre'],
                releaseYear=data['releaseYear'],
                director=data['director'],
                rating=data['rating']
            )
            db.session.add(newMovie)
            db.session.commit()
            return jsonify({"id": newMovie.id, "title": newMovie.title, "genre": newMovie.genre, "releaseYear": newMovie.releaseYear, "director": newMovie.director, "rating": newMovie.rating}), 201
        except KeyError as e:
            return jsonify({"NOK": f"Vaadittu tieto puuttuu: {e.args[0]}"}), 400
        except Exception as e:
            return jsonify({"NOK": f"Vikatilanne: {str(e)}"}), 500
    return jsonify({"NOK": "Rakenne ei ole JSON mukainen"}), 400

# Lisaa uusi arvostelu
@app.route('/movies/<string:movie_id>/reviews', methods=['POST'])
@swag_from({
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'user_name': {'type': 'string'},
                    'review_text': {'type': 'string'},
                    'rating': {'type': 'integer'}
                }
            }
        }
    ],
    'responses': {
        201: {
            'description': 'New review added',
            'schema': {
                'type': 'object',
                'properties': {
                    'id': {'type': 'integer'},
                    'movie_id': {'type': 'string'},
                    'user_name': {'type': 'string'},
                    'review_text': {'type': 'string'},
                    'rating': {'type': 'integer'}
                }
            }
        },
        400: {
            'description': 'Invalid input or missing data',
            'examples': {
                'application/json': {
                    'NOK': 'Vaadittu tieto puuttuu: user_name'
                }
            }
        },
        404: {
            'description': 'Movie not found',
            'examples': {
                'application/json': {
                    'NOK': 'Elokuvaa ei loydy!'
                }
            }
        }
    }
})
def add_review(movie_id):
    movie = Movie.query.get(movie_id)
    if not movie:
        return jsonify({"NOK": "Elokuvaa ei loydy!"}), 404
    
    data = request.get_json()
    try:
        new_review = Review(
            movie_id=movie.id,
            user_name=data['user_name'],
            review_text=data['review_text'],
            rating=data['rating']
        )
        db.session.add(new_review)
        db.session.commit()
        return jsonify({"id": new_review.id, "movie_id": new_review.movie_id, "user_name": new_review.user_name, "review_text": new_review.review_text, "rating": new_review.rating}), 201
    except KeyError as e:
        return jsonify({"NOK": f"Vaadittu tieto puuttuu: {e.args[0]}"}), 400
    except Exception as e:
        return jsonify({"NOK": f"Vikatilanne: {str(e)}"}), 500

# Hae elokuvan arvostelut
@app.route('/movies/<string:movie_id>/reviews', methods=['GET'])
@swag_from({
    'responses': {
        200: {
            'description': 'List of all reviews for the specified movie',
            'schema': {
                'type': 'array',
                'items': {
                    'type': 'object',
                    'properties': {
                        'id': {'type': 'integer'},
                        'user_name': {'type': 'string'},
                        'review_text': {'type': 'string'},
                        'rating': {'type': 'integer'}
                    }
                }
            }
        },
        404: {
            'description': 'Movie not found',
            'examples': {
                'application/json': {
                    'NOK': 'Elokuvaa ei loydy!'
                }
            }
        }
    }
})
def get_reviews(movie_id):
    movie = Movie.query.get(movie_id)
    if not movie:
        return jsonify({"NOK": "Elokuvaa ei loydy!"}), 404
    
    reviews = Review.query.filter_by(movie_id=movie.id).all()
    return jsonify([{"id": review.id, "user_name": review.user_name, "review_text": review.review_text, "rating": review.rating} for review in reviews])

# Paivita elokuvan tiedot
@app.route('/movies/<string:movieId>', methods=['PUT'])
@swag_from({
    'parameters': [
        {
            'name': 'body',
            'in': 'body',
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'title': {'type': 'string'},
                    'genre': {'type': 'string'},
                    'releaseYear': {'type': 'integer'},
                    'director': {'type': 'string'},
                    'rating': {'type': 'integer'}
                }
            }
        }
    ],
    'responses': {
        200: {
            'description': 'Updated movie details',
            'schema': {
                'type': 'object',
                'properties': {
                    'id': {'type': 'string'},
                    'title': {'type': 'string'},
                    'genre': {'type': 'string'},
                    'releaseYear': {'type': 'integer'},
                    'director': {'type': 'string'},
                    'rating': {'type': 'integer'}
                }
            }
        },
        404: {
            'description': 'Movie not found',
            'examples': {
                'application/json': {
                    'NOK': 'Elokuvaa ei loydy!'
                }
            }
        }
    }
})
def update_movie(movieId):
    movie = Movie.query.get(movieId)
    if not movie:
        return jsonify({"NOK": "Elokuvaa ei loydy!"}), 404
    data = request.json
    movie.title = data.get('title', movie.title)
    movie.genre = data.get('genre', movie.genre)
    movie.releaseYear = data.get('releaseYear', movie.releaseYear)
    movie.director = data.get('director', movie.director)
    movie.rating = data.get('rating', movie.rating)
    db.session.commit()
    return jsonify({"id": movie.id, "title": movie.title, "genre": movie.genre, "releaseYear": movie.releaseYear, "director": movie.director, "rating": movie.rating})

# Poista elokuva
@app.route('/movies/<string:movieId>', methods=['DELETE'])
@swag_from({
    'responses': {
        200: {
            'description': 'Movie deleted successfully',
            'examples': {
                'application/json': {
                    'OK': 'Elokuva poistettu'
                }
            }
        },
        404: {
            'description': 'Movie not found',
            'examples': {
                'application/json': {
                    'NOK': 'Elokuvaa ei loydetty!'
                }
            }
        }
    }
})
def delete_movie(movieId):
    movie = Movie.query.get(movieId)
    if not movie:
        return jsonify({"NOK": "Elokuvaa ei loydetty!"}), 404
    db.session.delete(movie)
    db.session.commit()
    return jsonify({"OK": "Elokuva poistettu"})

# Etsi elokuva jonkin kriterian perusteella
@app.route('/movies/search', methods=['GET'])
@swag_from({
    'parameters': [
        {
            'name': 'id',
            'in': 'query',
            'type': 'string',
            'required': False,
            'description': 'Movie ID to search'
        },
        {
            'name': 'title',
            'in': 'query',
            'type': 'string',
            'required': False,
            'description': 'Title of the movie to search'
        },
        {
            'name': 'genre',
            'in': 'query',
            'type': 'string',
            'required': False,
            'description': 'Genre of the movie to search'
        },
        {
            'name': 'releaseYear',
            'in': 'query',
            'type': 'integer',
            'required': False,
            'description': 'Release year of the movie to search'
        },
        {
            'name': 'director',
            'in': 'query',
            'type': 'string',
            'required': False,
            'description': 'Director of the movie to search'
        },
        {
            'name': 'rating',
            'in': 'query',
            'type': 'integer',
            'required': False,
            'description': 'Rating of the movie to search'
        },
        {
            'name': 'sort_by',
            'in': 'query',
            'type': 'string',
            'required': False,
            'description': 'Field to sort by (releaseYear, rating, title, director, genre)',
            'default': 'releaseYear'
        },
        {
            'name': 'sort_order',
            'in': 'query',
            'type': 'string',
            'required': False,
            'description': 'Sort order (asc or desc)',
            'default': 'asc'
        },
        {
            'name': 'page',
            'in': 'query',
            'type': 'integer',
            'required': False,
            'description': 'Page number for pagination',
            'default': 1
        },
        {
            'name': 'per_page',
            'in': 'query',
            'type': 'integer',
            'required': False,
            'description': 'Number of items per page for pagination',
            'default': 10
        }
    ],
    'responses': {
        200: {
            'description': 'List of movies matching search criteria',
            'schema': {
                'type': 'object',
                'properties': {
                    'total_pages': {'type': 'integer'},
                    'current_page': {'type': 'integer'},
                    'total_items': {'type': 'integer'},
                    'results': {
                        'type': 'array',
                        'items': {
                            'type': 'object',
                            'properties': {
                                'id': {'type': 'string'},
                                'title': {'type': 'string'},
                                'genre': {'type': 'string'},
                                'releaseYear': {'type': 'integer'},
                                'director': {'type': 'string'},
                                'rating': {'type': 'integer'}
                            }
                        }
                    }
                }
            }
        },
        400: {
            'description': 'Invalid input or missing required criteria',
            'examples': {
                'application/json': {
                    'NOK': 'Vahintaan yksi kriteeri vaaditaan.'
                }
            }
        }
    }
})
def search_movie():
    id_search = request.args.get('id')
    title_search = request.args.get('title')
    genre_search = request.args.get('genre')
    release_year_search = request.args.get('releaseYear')
    director_search = request.args.get('director')
    rating_search = request.args.get('rating')
    sort_by = request.args.get('sort_by', 'releaseYear')
    sort_order = request.args.get('sort_order', 'asc')
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)

    query = Movie.query
    search_criteria = False

    if id_search:
        query = query.filter(Movie.id.ilike(f"%{id_search}%"))
        search_criteria = True
    if title_search:
        query = query.filter(Movie.title.ilike(f"%{title_search}%"))
        search_criteria = True
    if genre_search:
        query = query.filter(Movie.genre.ilike(f"%{genre_search}%"))
        search_criteria = True
    if release_year_search:
        try:
            year = int(release_year_search)
            query = query.filter(Movie.releaseYear == year)
            search_criteria = True
        except ValueError:
            return jsonify({"NOK": "Tarkista elokuvan julkaisuvuosi!"}), 400
    if director_search:
        query = query.filter(Movie.director.ilike(f"%{director_search}%"))
        search_criteria = True
    if rating_search:
        try:
            rating = int(rating_search)
            query = query.filter(Movie.rating == rating)
            search_criteria = True
        except ValueError:
            return jsonify({"NOK": "Tarkista elokuvan arvio!"}), 400

    if not search_criteria:
        return jsonify({"NOK": "Vahintaan yksi kriteeri vaaditaan."}), 400

    # Aloita lajittelu
    if sort_order == 'asc':
        if sort_by == 'releaseYear':
            query = query.order_by(Movie.releaseYear.asc())
        elif sort_by == 'rating':
            query = query.order_by(Movie.rating.asc())
        elif sort_by == 'title':
            query = query.order_by(Movie.title.asc())
        elif sort_by == 'director':
            query = query.order_by(Movie.director.asc())
        elif sort_by == 'genre':
            query = query.order_by(Movie.genre.asc())
    elif sort_order == 'desc':
        if sort_by == 'releaseYear':
            query = query.order_by(Movie.releaseYear.desc())
        elif sort_by == 'rating':
            query = query.order_by(Movie.rating.desc())
        elif sort_by == 'title':
            query = query.order_by(Movie.title.desc())
        elif sort_by == 'director':
            query = query.order_by(Movie.director.desc())
        elif sort_by == 'genre':
            query = query.order_by(Movie.genre.desc())

    paginatedQuery = query.paginate(page=page, per_page=per_page)

    results = [{"id": movie.id, "title": movie.title, "genre": movie.genre, "releaseYear": movie.releaseYear, "director": movie.director, "rating": movie.rating} for movie in paginatedQuery.items]
    return jsonify({
        "total_pages": paginatedQuery.pages,
        "current_page": paginatedQuery.page,
        "total_items": paginatedQuery.total,
        "results": results
    })
    
# Kaynnista elokuvien hallintajarjestelma
if __name__ == '__main__':
    app.run(debug=True)
