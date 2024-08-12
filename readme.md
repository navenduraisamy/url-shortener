# URL Shortener

## Setting up the environment
```shell
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
```

## Start the server
```shell
python app.py
```
There server by default starts on port 80.

## Endpoints
### Create a short url
```shell
curl -X POST <HOST>:80/shorten -d { "url": "<url_to_shorten>"}
```

### Redirect from short url
```shell
curl <shortend-url>
```