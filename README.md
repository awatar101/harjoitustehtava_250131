Elokuvien hallintajärjestelmä.

Vaatimukset: 
- Python 3.9.10
- Kirjasto flask-sqlalchemy (asennus: pip install flask flask-sqlalchemy)
- Kirjasto flasgger (asennus: pip install flasgger)
- Kirjasto flask-restplus (pip install flask-restplus)

Järjestelmän käynnistäminen (cmd): 
Luo uusi virtuaaliympäristö
python -m venv venv
Aktivoi virtuaali:
.\venv\Scripts\activate
Asenna vaaditut kirjastot requirements.txt-tiedostosta:
pip install -r requirements.txt
Käynnistä serveri:
python app.py

Järjestelmän testaaminen (powershell):
Lisää uusi elokuva (mallissa kokeiludatana 5 eri elokuvaa) :
invoke-restmethod -uri "http://127.0.0.1:5000/movies" -method post -headers @{"Content-Type"="application/json"} -body '{"title": "Schindlers list", "genre": "Drama", "releaseYear": 1993, "director": "Steven Spielberg", "rating": 9}'
invoke-restmethod -uri "http://127.0.0.1:5000/movies" -method post -headers @{"Content-Type"="application/json"} -body '{"title": "Groundhog Day", "genre": "Comedy", "releaseYear": 1993, "director": "Harold Ramis", "rating": 9}'
invoke-restmethod -uri "http://127.0.0.1:5000/movies" -method post -headers @{"Content-Type"="application/json"} -body '{"title": "Jason Bourne", "genre": "Action", "releaseYear": 2016, "director": "Paul Greengras", "rating": 7}'
invoke-restmethod -uri "http://127.0.0.1:5000/movies" -method post -headers @{"Content-Type"="application/json"} -body '{"title": "The Girl on the Train", "genre": "Thiller", "releaseYear": 2016, "director": "Tate Taylor", "rating": 8}'
invoke-restmethod -uri "http://127.0.0.1:5000/movies" -method post -headers @{"Content-Type"="application/json"} -body '{"title": "Inception", "genre": "Sci-Fi", "releaseYear": 2010, "director": "Cristopher Nolan", "rating": 9}'

Hae kaikki elokuvat:
invoke-restmethod -uri "http://127.0.0.1:5000/movies" -method get

Hae yksittäinen elokuva:
Huom, UUID pitää kopioida elokuvalistasta
invoke-restmethod -uri "http://127.0.0.1:5000/movies/de5b4efa-8954-4c0f-a7f0-074d6bb54817" -method get

Päivitä elokuvan tiedot:
Huom, UUID pitää kopioida elokuvalistasta
invoke-restmethod -uri "http://127.0.0.1:5000/movies/320c3325-6ffd-4826-9d1a-f593685ab4dc" -method put -headers @{"Content-Type"="application/json"} -body '{"title": "Interstellar", "genre": "Sci-Fi", "releaseYear": 2014, "director": "Cristopher Nolan", "rating": 8}'

Poista elokuva:
Huom, UUID pitää kopioida elokuvalistasta
invoke-restmethod -uri "http://127.0.0.1:5000/movies/b2bcb070-d452-415d-af3f-2e6de30c8675" -method delete

Hae elokuvia kriteerien perusteella
invoke-restmethod -uri "http://127.0.0.1:5000/movies/search?genre=comedy" -method get

Hae elokuvia suodatettuna
Invoke-RestMethod -Uri "http://127.0.0.1:5000/movies/search?genre=Comedy&sort_by=rating&sort_order=desc" -Method Get
Invoke-RestMethod -Uri "http://127.0.0.1:5000/movies/search?releaseYear=1993&sort_by=rating&sort_order=asc" -Method Get

Lisää arvostelu elokuvalle:
Powershell
$review = @{ user_name = "Jarmo Pylkko"; review_text = "Loistava elokuva"; rating = 9 }

Luodaan JSON:
$reviewJson = $review | ConvertTo-Json

POST lähetys:
$response = Invoke-RestMethod -Uri "http://127.0.0.1:5000/movies/ad3ff096-b389-432b-a25c-67ab2368c9ef/reviews" -Method Post -Body $reviewJson -ContentType "application/json"

Vastaus:
$response

id          : 1
movie_id    : ad3ff096-b389-432b-a25c-67ab2368c9ef
rating      : 9
review_text : Loistava elokuva
user_name   : Jarmo Pylkko

Katso arvostelu:
Elokuvan id
$movieId = "ad3ff096-b389-432b-a25c-67ab2368c9ef"

Haetaan get
$response = Invoke-RestMethod -Uri "http://127.0.0.1:5000/movies/$movieId/reviews" -Method Get

# Näytetään palvelimen vastaus
$response
(base) PS C:\Users\Jarmo> $response

id rating review_text      user_name
-- ------ -----------      ---------
 1      9 Loistava elokuva Jarmo Pylkko

Swagger dokumentaatio:
http://127.0.0.1:5000/apidocs