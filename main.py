from fastapi import FastAPI,Path,HTTPException,Query
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

@app.get("/patient/{patient_id}")
def view_patient(patient_id:str = Path(...,description="id of the patient in the Database",example="P001")):
    data = load_data()
    if patient_id in data:
        return data[patient_id]
    raise HTTPException(status_code=404,detail="Patient not found in the Database")

@app.get("/sort")
def sort_patients(sort_by:str = Query(..., description="sort on the basis of height, weight or BMI"), order:str = Query("asc", description="sort in ASC or DESC order") ):
    valid_fields = ['height','weight','bmi']
    
    if sort_by not in valid_fields:
        raise HTTPException(status_code=400,detail=f'Invalid field select from {valid_fields}')
    
    if order not in ['asc', 'desc']:
        raise HTTPException(status_code=400,detail="Invalid select order between ASC or DESC")
    
    data = load_data()

    sort_order = False if order == 'asc' else True

    sorted_data = sorted(data.values(), key=lambda x : x.get(sort_by,0),reverse=sort_order)
    return sorted_data