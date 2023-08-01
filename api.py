import math
import time
from fastapi import FastAPI, Query
from fastapi.responses import RedirectResponse
from fastapi.openapi.utils import get_openapi
from typing import Literal
from ReinforcmentLearning import *

list_of_interests_available = [
    "Tech", "Food", "Entertainment", "Fashion", "Market", "Automotive",
    "Drink", "Fit", "Games"
]


def get_distance(x1, y1, x2, y2):
    return math.sqrt((x2 - x1)**2 + (y2 - y1)**2)


def get_path(start_id: int, goal_id: int, algorithm: str):
    

    total_distance = 0

    # get the vertices
    directory = "vertices.csv"
    _file = open(directory, "r", encoding="utf-8-sig")
    vertices_dict = {}
    for line in _file.readlines():
        line_split = line.split(",")
        vertices_dict[line_split[0]] = {
            "pos_x": float(line_split[3]),
            "pos_y": float(line_split[4])
        }

    # create the goal table
    directory = f"table_q/{algorithm}/table_q_{goal_id}.csv"
    _file = open(directory, "r", encoding="utf-8-sig")
    table = {}
    for line in _file.readlines():
        line_split = line.split(",")
        table[line_split[0]] = {
            "next_vertex": int(line_split[1]),
        }

    path = []
    current = start_id
    path.append(current)
    # path from start to goal
    while current != goal_id:
        distance = get_distance(
            vertices_dict[str(current)]["pos_x"],
            vertices_dict[str(current)]["pos_y"],
            vertices_dict[str(table[str(current)]["next_vertex"])]["pos_x"],
            vertices_dict[str(table[str(current)]["next_vertex"])]["pos_y"])
        current = int(table[str(current)]["next_vertex"])
        path.append(current)
        total_distance += distance

    return path, total_distance


def get_path_interest(start_id: int, goal_id: int, n_interests: int,
                          interests: list, algorithm: str):
    total_distance = 0

    vertices_dict = {}
    directory = "vertices.csv"
    _file = open(directory, "r", encoding="utf-8-sig")
    for line in _file.readlines():
        line_split = line.split(",")
        vertices_dict[line_split[0]] = {
            "category": line_split[2],
            "pos_x": float(line_split[3]),
            "pos_y": float(line_split[4])
        }

    interest_vertexes_dict = {}

    # Get all vertexes with the same category
    for vertex_id in vertices_dict:
        if vertex_id == start_id or vertex_id == goal_id:
            continue

        if vertices_dict[vertex_id]["category"].lower() in interests:
            interest_vertexes_dict[vertex_id] = vertices_dict[vertex_id]

    n_iterations = n_interests if n_interests < len(
        interest_vertexes_dict) else len(interest_vertexes_dict)

    path = []
    path.append(start_id)
    current = start_id

    # while list of interest vertexes is not empty
    for i in range(n_iterations):
        smaller_distance = 9999
        shortest_vertex = None

        # find the next shortest interest vertex
        for vertex_id in interest_vertexes_dict:
            distance = get_distance(vertices_dict[str(current)]["pos_x"],
                                    vertices_dict[str(current)]["pos_y"],
                                    vertices_dict[vertex_id]["pos_x"],
                                    vertices_dict[vertex_id]["pos_y"])
            if distance < smaller_distance:
                smaller_distance = distance
                shortest_vertex = vertex_id

        # while current vertex is not the interest vertex
        while current != int(shortest_vertex):
            directory = f"table_q/{algorithm}/table_q_{shortest_vertex}.csv"
            _file = open(directory, "r", encoding="utf-8-sig")
            for line in _file.readlines():
                line_split = line.split(",")
                if line_split[0] == str(current):
                    distance = get_distance(
                        vertices_dict[str(current)]["pos_x"],
                        vertices_dict[str(current)]["pos_y"],
                        vertices_dict[str(int(line_split[1]))]["pos_x"], # double conversion to avoid error
                        vertices_dict[str(int(line_split[1]))]["pos_y"])
                    current = int(line_split[1])
                    total_distance += distance
                    path.append(current)
                    break

        interest_vertexes_dict.pop(shortest_vertex)

    # append the goal table
    directory = f"table_q/{algorithm}/table_q_{goal_id}.csv"
    _file = open(directory, "r", encoding="utf-8-sig")
    table = {}
    for line in _file.readlines():
        line_split = line.split(",")
        table[line_split[0]] = {
            "next_vertex": int(line_split[1]),
        }

    # at the end, append the goal path
    while current != goal_id:
        distance = get_distance(
            vertices_dict[str(current)]["pos_x"],
            vertices_dict[str(current)]["pos_y"],
            vertices_dict[str(table[str(current)]["next_vertex"])]["pos_x"],
            vertices_dict[str(table[str(current)]["next_vertex"])]["pos_y"])
        current = int(table[str(current)]["next_vertex"])
        path.append(current)
        total_distance += distance

    return path, total_distance

# full_run(algorithm=QLearningAgent)

app = FastAPI(swagger_ui_parameters={"defaultModelsExpandDepth": -1})

@app.get("/path/{id_origin}/{id_target}/{n_interests}", tags=["Path"])
async def get_path_request(
    id_origin: int,
    id_target: int,
    n_interests: int,
    algorithm: Literal["QLearning", "Sarsa", "Astar", "Largura",
                       "Profundidade"] = "QLearning",
    interests: str | None = Query(
        None,
        description=
        "Uma lista de palavras separadas por vírgula. Interesses disponíveis: "
        + ", ".join(list_of_interests_available))):

    path = []

    # directly from start to goal
    if interests is None:
        path, total_distance = get_path(start_id=id_origin,
                                        goal_id=id_target,
                                        algorithm=algorithm.lower())

    # with interests
    else:
        interests = interests.split(",")
        interests = [interest.strip().lower() for interest in interests
                     ]  # remove spaces and convert to lowercase

        path, total_distance = get_path_interest(
            start_id=id_origin,
            goal_id=id_target,
            n_interests=n_interests,
            interests=interests,
            algorithm=algorithm.lower())

    return {"path": path, "total_distance": total_distance, "steps": len(path)}


@app.get("/", include_in_schema=False)
async def root():
    return RedirectResponse(url="/docs")


def config_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="Api for Bias Pathfinding",
        version="1.0.0",
        description=
        "Essa é uma api para encontrar caminhos com viés em ambientes indoor.",
        routes=app.routes,
    )

    app.openapi_schema = openapi_schema

    return app.openapi_schema


app.openapi = config_openapi

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="localhost", port=8000)
