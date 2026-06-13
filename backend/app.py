import json
import random
from urllib.request import urlopen

from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

MET_API_BASE_URL = (
    "https://collectionapi.metmuseum.org/public/collection/v1/objects/"
)

ARTWORKS = [
    {
        "object_id": 436524,
        "hints": [
            "This artwork was created by a Dutch painter.",
            "It depicts flowers arranged in a vase.",
            "The artist is Vincent van Gogh."
        ]
    },
    {
        "object_id": 437853,
        "hints": [
            "This portrait was painted by a Dutch artist.",
            "The subject is a young woman wearing an unusual piece of jewelry.",
            "The artist is Johannes Vermeer."
        ]
    },
    {
        "object_id": 435882,
        "hints": [
            "This artwork depicts a dramatic maritime scene.",
            "The artist was known for expressive landscapes and powerful use of light.",
            "The artist is J. M. W. Turner."
        ]
    }
]


def fetch_artwork(object_id):
    url = f"{MET_API_BASE_URL}{object_id}"

    with urlopen(url) as response:
        return json.load(response)


@app.get("/api/puzzle")
def get_puzzle():
    selected = random.choice(ARTWORKS)
    artwork = fetch_artwork(selected["object_id"])

    puzzle = {
        "id": artwork["objectID"],
        "title": "Museum Mystery",
        "image_url": artwork["primaryImageSmall"],
        "hints": selected["hints"],
        "answer": artwork["title"],
        "explanation": (
            f"{artwork['title']} was created by "
            f"{artwork['artistDisplayName']} in {artwork['objectDate']}. "
            f"It belongs to the {artwork['department']} collection "
            "at The Metropolitan Museum of Art."
        ),
        "source": artwork["objectURL"]
    }

    return jsonify(puzzle)


if __name__ == "__main__":
    app.run(debug=True, port=5000)