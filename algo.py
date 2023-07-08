from fastapi import FastAPI, Query
from fastapi.responses import RedirectResponse
from fastapi.openapi.utils import get_openapi
from pydantic import BaseModel
from typing import Literal
from ReinforcmentLearning import *

full_run(QLearningAgent)
app = FastAPI()



@app.get("/path/{id_origin}/{id_target}", tags=["Path"])
async def get_path_request( id_origin: int, id_target: int, 
                            algorithm: Literal["QLearning", "Sarsa"] = "QLearning",
                            interests: str | None = Query(
                                None,
                                description="Uma lista de palavras separadas por vírgula. Interesses disponíveis: "
                                + ", ".join(list_of_interests_available))):

    if algorithm == "QLearning":
        algorithm = QLearningAgent
    elif algorithm == "Sarsa":
        algorithm = SarsaAgent
    else:
        return {"error": "Invalid algorithm"}
    

    path = get_path(start_id=id_origin,
                    goal_id=id_target,
                    interest_categories=interests,
                    Algorithm=algorithm)

    return {"path": [vertex.id for vertex in path]}


@app.get("/", include_in_schema=False)
async def root():
    return RedirectResponse(url="/docs")

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="Api for Bias Pathfinding",
        version="1.0.0",
        description=
        "Essa é uma api para encontrar caminhos com viés em ambientes indoor.",
        routes=app.routes,
    )
    openapi_schema["info"]["x-logo"] = {
        "url": "https://fastapi.tiangolo.com/img/logo-margin/logo-teal.png"
    }
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="localhost", port=8000)
