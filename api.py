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

edges_dict = {}
# save all edges in a dict
_file = open("arestas.csv", "r", encoding="utf-8-sig")
for line in _file.readlines():
    line_split = line.split(",")
    edges_dict[line_split[0] + "-" + line_split[1]] = float(line_split[2])
    edges_dict[line_split[1] + "-" + line_split[0]] = float(line_split[2])

vertices_dict = {}
# save all vertexes in a dict
_file = open("vertices.csv", "r", encoding="utf-8-sig")
for line in _file.readlines():
    line_split = line.split(",")
    vertices_dict[line_split[0]] = {
        "name": line_split[1],
        "category": line_split[2],
        "pos_x": float(line_split[3]),
        "pos_y": float(line_split[4])
    }


def get_distance(x1, y1, x2, y2):
    return math.sqrt((x2 - x1)**2 + (y2 - y1)**2)


# get the path from search algorithms (BFS, DFS, A*) without interests
def get_path_search(start_id: int, goal_id: int, algorithm: str):
    # get path from start to goal
    directory = f"table_q/{algorithm}/table_q_{goal_id}.csv"
    _file = open(directory, "r", encoding="utf-8-sig")
    path = []
    for line in _file.readlines():
        line_split = line.split(",")
        if line_split[0] == str(start_id):
            path = [int(i) for i in line_split]
            break

    # calculate the total distance
    total_distance = 0
    for i in range(len(path) - 1):
        total_distance += float(edges_dict[str(path[i]) + "-" +
                                           str(path[i + 1])])

    return path, total_distance


# get the path from reinforcement learning algorithms (Q-Learning, SARSA) without interests
def get_path_rl(start_id: int, goal_id: int, algorithm: str):
    # get table from start to goal
    directory = f"table_q/{algorithm}/table_q_{goal_id}.csv"
    _file = open(directory, "r", encoding="utf-8-sig")
    table = {}
    for line in _file.readlines():
        line_split = line.split(",")
        table[line_split[0]] = {
            "next_vertex": int(line_split[1]),
        }

    # save the path and calculate the total distance
    current = start_id
    path = []
    path.append(current)
    total_distance = 0
    while current != goal_id:
        distance = edges_dict[str(current) + "-" +
                              str(table[str(current)]["next_vertex"])]
        current = int(table[str(current)]["next_vertex"])
        path.append(current)
        total_distance += distance

    return path, total_distance


def get_path_search_interest(start_id: int, goal_id: int, max_interests: int,
                             interests: list, algorithm: str):
    total_distance = 0

    interest_vertexes_dict = {}

    # Get all vertexes with the same category
    for vertex_id in vertices_dict:
        if vertex_id == start_id or vertex_id == goal_id:
            continue

        if vertices_dict[vertex_id]["category"].lower() in interests.lower():
            interest_vertexes_dict[vertex_id] = vertices_dict[vertex_id]

    n_iterations = max_interests if max_interests < len(
        interest_vertexes_dict) else len(interest_vertexes_dict)

    total_path = []
    path = []
    current = start_id

    # while list of interest vertexes is not empty
    while n_iterations > 0 and len(interest_vertexes_dict) > 0:
        smaller_distance = 99999999
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

        # go through the next shortest interest vertex
        directory = f"table_q/{algorithm}/table_q_{shortest_vertex}.csv"
        _file = open(directory, "r", encoding="utf-8-sig")
        for line in _file.readlines():
            line_split = line.split(",")
            if line_split[0] == str(current):
                path = [int(i) for i in line_split]  # append the path
                total_path += path
                total_path.pop()  # remove the last element
                current = path[-1]  # update the current vertex
                break

        # calculate the total distance
        for i in range(len(path) - 1):
            if vertices_dict[str(path[i])]["category"].lower() in interests:
                n_iterations -= 1  # decrement the number of iterations

            total_distance += float(edges_dict[str(path[i]) + "-" +
                                               str(path[i + 1])])
        interest_points.append(interest_vertexes_dict[shortest_vertex]["name"])
        interest_vertexes_dict.pop(shortest_vertex)
        n_iterations -= 1

    # append the goal table to the path
    directory = f"table_q/{algorithm}/table_q_{goal_id}.csv"
    _file = open(directory, "r", encoding="utf-8-sig")
    table = {}
    for line in _file.readlines():
        line_split = line.split(",")
        table[line_split[0]] = {
            "next_vertex": int(line_split[1]),
        }

    # at the end, append the goal path
    total_path.append(current)
    while current != goal_id:
        distance = edges_dict[str(current) + "-" +
                              str(table[str(current)]["next_vertex"])]
        current = int(table[str(current)]["next_vertex"])
        total_distance += distance
        total_path.append(current)

    return total_path, total_distance


def get_path_rl_interest(start_id: int, goal_id: int, max_interests: int,
                         interests: list, algorithm: str):
    total_distance = 0

    interest_vertexes_dict = {}

    # Get all vertexes with the same category
    for vertex_id in vertices_dict:
        if vertex_id == start_id or vertex_id == goal_id:
            continue
        if vertices_dict[vertex_id]["category"].lower() in interests:
            interest_vertexes_dict[vertex_id] = vertices_dict[vertex_id]

    n_iterations = max_interests if max_interests < len(
        interest_vertexes_dict) else len(interest_vertexes_dict)

    path = []
    current = start_id
    path.append(current)

    # while list of interest vertexes is not empty
    while n_iterations > 0 and len(interest_vertexes_dict) > 0:
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
                line_split = line.strip().split(",")
                if line_split[0] == str(current):
                    distance = float(edges_dict[str(current) + "-" +
                                                str(line_split[1])])
                    if vertices_dict[str(
                            line_split[1])]["category"].lower() in interests:
                        n_iterations -= 1
                    current = int(line_split[1])
                    total_distance += distance
                    path.append(current)
                    break

        n_iterations -= 1
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
        distance = edges_dict[str(current) + "-" +
                              str(table[str(current)]["next_vertex"])]
        current = int(table[str(current)]["next_vertex"])
        path.append(current)
        total_distance += distance

    return path, total_distance


# full_run(algorithm=QLearningAgent)
# full_run(algorithm=SarsaAgent)

app = FastAPI(swagger_ui_parameters={"defaultModelsExpandDepth": -1})


@app.get("/path/{id_origin}/{id_target}/{algorithm}", tags=["Path"])
async def get_path_request(
    id_origin: int,
    id_target: int,
    algorithm: Literal["QLearning", "Sarsa", "Astar", "Largura",
                       "Profundidade"] = "QLearning",
    max_interests: int = 0,
    interests: str | None = Query(
        None,
        description=
        "Uma lista de palavras separadas por vírgula. Interesses disponíveis: "
        + ", ".join(list_of_interests_available))):

    path = []

    if interests is not None:
        interests = interests.split(",")
        interests = [i.lower().strip() for i in interests]

    if algorithm.lower() in ["largura", "profundidade", "astar"]:
        if interests is None:
            path, total_distance = get_path_search(start_id=id_origin,
                                                   goal_id=id_target,
                                                   algorithm=algorithm.lower())
        else:
            path, total_distance = get_path_search_interest(
                start_id=id_origin,
                goal_id=id_target,
                max_interests=max_interests,
                interests=interests,
                algorithm=algorithm.lower())

    if algorithm.lower() in ["qlearning", "sarsa"]:
        if interests is None:
            path, total_distance = get_path_rl(start_id=id_origin,
                                               goal_id=id_target,
                                               algorithm=algorithm.lower())
        else:
            path, total_distance = get_path_rl_interest(
                start_id=id_origin,
                goal_id=id_target,
                max_interests=max_interests,
                interests=interests,
                algorithm=algorithm.lower())

    return {
        "path": path,
        "total_distance": total_distance,
        "steps": len(path) - 1
    }


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
