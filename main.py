from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def hello_world():
    return {"message":"hello world, we are learning fastapi !"}

@app.get("/about")
def about():
    return {"message":"This is a simple FastAPI application."}