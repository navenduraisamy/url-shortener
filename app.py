import time

from flask import Flask, request, jsonify, redirect
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Integer, String, Text
from sqlalchemy.orm import DeclarativeBase, mapped_column, Mapped

from service import generate_hash

app = Flask(__name__)
SERVER_HOST = "127.0.0.1"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///store.db"


class Base(DeclarativeBase):
    pass


db = SQLAlchemy(model_class=Base)
db.init_app(app)


class HashToURL(db.Model):
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    hash: Mapped[str] = mapped_column(String(64), nullable=False, unique=True)
    original_url: Mapped[str] = mapped_column(Text, nullable=False, unique=True)


def get_url_by_hash(hash_value: str):
    result = db.session.scalar(db.select(HashToURL).where(HashToURL.hash == hash_value))
    return result


@app.route("/")
def test():
    return "connection successful", 200


@app.route("/<hash_value>", methods=["GET"])
def redirect_to_original_site(hash_value: str):
    result = get_url_by_hash(hash_value)
    if not result:
        return jsonify(error="Not Found"), 404

    original_url = result.original_url
    return redirect(original_url)


@app.route("/shorten", methods=["POST"])
def shorten_url():
    payload = request.get_json()
    if not payload or not payload.get("url"):
        return jsonify(error="Invalid request payload"), 400

    original_url = payload.get("url")
    hash_value = generate_hash(original_url)[:10]
    existence = get_url_by_hash(hash_value)

    if existence:
        saved_url = existence.original_url
        if saved_url == original_url:
            return jsonify(
                shortened_url=f"https://{SERVER_HOST}/{hash_value}",
                original_url=original_url
            ), 200

    # Hash collision
    while existence:
        # add salt
        original_url += str(time.time())
        hash_value = generate_hash(original_url)[:10]
        existence = get_url_by_hash(hash_value)

    url_record = HashToURL(hash=hash_value, original_url=original_url)
    db.session.add(url_record)
    db.session.commit()

    return jsonify(
        shortened_url=f"http://{SERVER_HOST}/{hash_value}",
        original_url=original_url
    ), 201


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=80, debug=True)
