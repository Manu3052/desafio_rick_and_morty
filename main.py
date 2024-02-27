import concurrent.futures
import json
import urllib.request

import requests
from flask import Flask, Response, render_template, request

app = Flask(__name__)


@app.route("/episodes")
def episodes():
    page = request.args.get("page", 1, type=int)
    episodes, total_pages = get_episodes(page)
    return render_template(
        "episodes.html", episodes=episodes, current_page=page, total_pages=total_pages
    )


def get_episodes(page=1, page_size=20):
    url = f"https://rickandmortyapi.com/api/episode?page={page}&page_size={page_size}"
    response = requests.get(url)
    data = response.json()
    episodes = data["results"]
    pages_amount = data["info"]["pages"]
    if len(data) == 0:
        return Response(
            response="Não foi possível buscar os episódios. Por favor, contate a equipe de suporte.",
            status=500,
        )
    return episodes, pages_amount


@app.route("/episode/<int:id>")
def episode(id):
    episode = get_episode_by_id(id)

    character_urls = episode["characters"]
    character_data = get_character_data(character_urls)

    return render_template(
        "episode.html", episode=episode, character_data=character_data
    )


def get_episode_by_id(page=1, page_size=10):
    url = f"https://rickandmortyapi.com/api/episode/{id}"
    response = requests.get(url)
    episode_details = response.json()
    data = episode_details["episode"].split("E")

    episode_details["season"] = data[0][1:]
    episode_details["episode"] = data[1]
    if len(data) == 0:
        return Response(
            response="Não foi encontrado o episódio buscado. Por favor, tente novamente. ",
            status=400,
        )

    return episode_details


def get_character_data(character_urls):
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future_to_url = {
            executor.submit(get_character_data_single, url): url
            for url in character_urls
        }
        character_data = []
        for future in concurrent.futures.as_completed(future_to_url):
            character_url = future_to_url[future]
            try:
                character_info = future.result()
                character_data.append(character_info)
            except Exception as exc:
                print(f"A requisição para {character_url} falhou: {exc}")
                character_data.append(None)
    return character_data


def get_list_characters_page():
    url = "https://rickandmortyapi.com/api/character/"
    response = urllib.request.urlopen(url)
    data = response.read()
    characters_dict = json.loads(data)

    return characters_dict["results"]


def get_character_data_single(character_url):
    response = requests.get(character_url)
    if response.status_code == 200:
        character_data = response.json()
        return {"name": character_data["name"], "image": character_data["image"]}
    else:
        return None


@app.route("/locations")
def locations():
    page = request.args.get("pages", 1, type=int)
    locations, total_pages = get_locations(page)
    return render_template(
        "locations.html",
        locations=locations,
        current_page=page,
        total_pages=total_pages,
    )


def get_locations(page=1, page_size=20):
    url = f"https://rickandmortyapi.com/api/location?page={page}&page_size={page_size}"
    response = requests.get(url)
    data = response.json()
    locations = data["results"]
    return locations, data["info"]["pages"]


@app.route("/location/<int:id>")
def location(id):
    location = get_location_by_id(id)

    residents_urls = location["residents"]
    residents_data = get_character_data(residents_urls)

    return render_template(
        "location.html", location=location, residents_data=residents_data
    )


def get_location_by_id(id, page=1, page_size=10):
    url = f"https://rickandmortyapi.com/api/location/{id}"
    response = requests.get(url)
    location_details = response.json()

    return location_details


@app.route("/")
def pageInicial():
    response = get_list_characters_page()
    return render_template("characters.html", characters=response)
