from fastapi import FastAPI
import json
app = FastAPI()

# Load patient data from a JSON file
def load_data():
    with open("patients.json","r") as f:
        data = json.load(f)
    return data


@app.get("/")
def hello_world():
    return {"message":"Patient Management System API !"}

@app.get("/about")
def about():
    return {"message":"A fully functional API to manage your patient records."}

@app.get("/view_patients")
def view_patients():
    data = load_data()
    return data