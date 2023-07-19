from fastapi import FastAPI, Query
from fastapi.responses import RedirectResponse
from fastapi.openapi.utils import get_openapi
from typing import Literal
from ReinforcmentLearning import *

list_of_interests_available = [
    "Tech", "Food", "Entertainment", "Fashion", "Market", "Automotive",
    "Drink", "Fit", "Games"
]


def get_path(start_id, goal_id, algorithm):
    path = []

    path.append(start_id)
    while start_id != goal_id:
        directory = f"table_q/{algorithm}/table_q_{goal_id}.csv"
        _file = open(directory, "r", encoding="utf-8")
        for line in _file.readlines():
            line_split = line.split(",")
            if line_split[0] == str(start_id):
                start_id = int(line_split[1])
                path.append(start_id)
                break

        _file.close()

    return path


def get_path_interest(start_id: int, goal_id: int, categories: list,
                      algorithm: str):
    interest_vertexes = []
    total_distance = 0
    # Get all vertexes with the same category
    _file = open("vertices.csv", "r", encoding="utf-8-sig")
    for line in _file.readlines():
        line_split = line.split(",")
        print (line_split[2].lower(), categories)
        if str(line_split[2]).lower() in categories:
            interest_vertexes.append(int(line_split[0]))

    list_of_tables = []

    # Get all tables of the interest vertexes
    for vertex in interest_vertexes:
        directory = f"table_q/{algorithm}/table_q_{vertex}.csv"
        _file = open(directory, "r", encoding="utf-8-sig")
        table = []
        for line in _file:
            line = line.split(",")
            table.append(line)
        list_of_tables.append(table)

    path = []
    path.append(start_id)
    current = start_id

    # while list of interest vertexes is not empty
    while len(interest_vertexes) > 0:
        bigger_q = 0
        interest_index = 0
        for i in range(len(list_of_tables)):
            if float(list_of_tables[i][current][2]) > bigger_q:
                bigger_q = float(list_of_tables[i][current][2])
                interest_index = i

        # while current vertex is not the interest vertex
        while current != interest_vertexes[interest_index]:
            current = int(list_of_tables[interest_index][current][1])
            path.append(current)
            total_distance += float(
                list_of_tables[interest_index][current][2])

        list_of_tables.pop(interest_index)
        interest_vertexes.pop(interest_index)

    # append the goal table
    directory = f"table_q/{algorithm}/table_q_{goal_id}.csv"
    _file = open(directory, "r", encoding="utf-8-sig")
    table = []
    for line in _file:
        line = line.split(",")
        table.append(line)
    list_of_tables.append(table)

    # at the end, append the goal path
    while current != goal_id:
        current = int(list_of_tables[0][current][1])
        path.append(current)
        total_distance += float(list_of_tables[0][current][2])

    print("Path: ", path)
    print("Quantidade de passos: ", len(path))
    print(f"Distância percorrida em metros: {total_distance:.2f}")
    return path


# full_run(algorithm=QLearningAgent)

app = FastAPI(swagger_ui_parameters={"defaultModelsExpandDepth": -1})


@app.get("/path/{id_origin}/{id_target}", tags=["Path"])
async def get_path_request(
    id_origin: int,
    id_target: int,
    algorithm: Literal["QLearning", "Sarsa", "Astar", "BFS",
                       "DFS"] = "QLearning",
    interests: str | None = Query(
        None,
        description=
        "Uma lista de palavras separadas por vírgula. Interesses disponíveis: "
        + ", ".join(list_of_interests_available))):

    path = []
    if interests is None or algorithm.lower() in ["astar", "bfs", "dfs"]:
        path = get_path(start_id=id_origin,
                        goal_id=id_target,
                        algorithm=algorithm.lower())
    else:
        interests = interests.split(",")
        interests = [interest.strip().lower() for interest in interests]

        path = get_path_interest(start_id=id_origin,
                                 goal_id=id_target,
                                 categories=interests,
                                 algorithm=algorithm.lower())

    return {"path": path}


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
