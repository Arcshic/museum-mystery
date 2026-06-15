import json
import os
import random
from urllib.request import urlopen

import requests
from dotenv import load_dotenv
from flask import Flask, jsonify
from flask_cors import CORS

load_dotenv(dotenv_path="../.env")

app = Flask(__name__)
CORS(app)

MET_API_BASE_URL = "https://collectionapi.metmuseum.org/public/collection/v1/objects/"

SEARCH_SERVICE_NAME = os.getenv("AZURE_SEARCH_SERVICE_NAME")
SEARCH_INDEX_NAME = os.getenv("AZURE_SEARCH_INDEX_NAME")
SEARCH_API_KEY = os.getenv("AZURE_SEARCH_API_KEY")
SEARCH_API_VERSION = os.getenv("AZURE_SEARCH_API_VERSION", "2025-09-01")

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
        "object_id": 437881,
        "hints": [
            "This painting was created by a Dutch artist.",
            "It shows a young woman holding a water pitcher.",
            "The artist is Johannes Vermeer."
        ]
    },
    {
        "object_id": 437980,
        "hints": [
            "This artwork was created by a Dutch painter.",
            "It shows tall cypress trees in a dramatic landscape.",
            "The artist is Vincent van Gogh."
        ]
    }
]

def fetch_met_artwork(object_id):
    url = f"{MET_API_BASE_URL}{object_id}"

    with urlopen(url) as response:
        return json.load(response)


def get_artwork_knowledge_by_id(object_id):
    if not SEARCH_SERVICE_NAME or not SEARCH_INDEX_NAME or not SEARCH_API_KEY:
        raise RuntimeError("Azure AI Search environment variables are missing.")

    document_url = (
        f"https://{SEARCH_SERVICE_NAME}.search.windows.net"
        f"/indexes/{SEARCH_INDEX_NAME}/docs/{object_id}"
        f"?api-version={SEARCH_API_VERSION}"
    )

    headers = {
        "api-key": SEARCH_API_KEY
    }

    response = requests.get(document_url, headers=headers, timeout=15)

    if response.status_code == 404:
        return None

    response.raise_for_status()
    return response.json()

@app.get("/api/puzzle")
def get_puzzle():
    selected = random.choice(ARTWORKS)

    met_artwork = fetch_met_artwork(selected["object_id"])
    knowledge = get_artwork_knowledge_by_id(selected["object_id"])

    if knowledge:
        answer = knowledge["title"]
        explanation = (
            f"{knowledge['title']} was created by {knowledge['artist']} "
            f"in {knowledge['objectDate']}. {knowledge['description']}"
        )
        source = knowledge["source"]
    else:
        answer = met_artwork["title"]
        explanation = (
            "The knowledge base did not return enough information for this artwork. "
            "This fallback uses The Met public collection record."
        )
        source = met_artwork["objectURL"]

    puzzle = {
        "id": met_artwork["objectID"],
        "title": "Museum Mystery",
        "image_url": met_artwork["primaryImageSmall"],
        "hints": selected["hints"],
        "answer": answer,
        "explanation": explanation,
        "source": source
    }

    return jsonify(puzzle)


if __name__ == "__main__":
    app.run(debug=True, port=5000)