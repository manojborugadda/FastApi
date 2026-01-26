from fastapi import FastAPI,Path,HTTPException,Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel,Field, computed_field
import json
from typing import Annotated, Literal,Optional
app = FastAPI()


# creating schema of pydantic class
class Patient(BaseModel):
    id: Annotated[str, Field(..., description="Unique identifier for the patient", example="P001")]
    name: Annotated[str, Field(..., description="Full name of the patient", example="Novak Djokovic")]
    age: Annotated[int, Field(...,gt=0,le=120,description="Age of the patient must be between 0 and 120", example=36)]
    city: Annotated[str, Field(..., description="City of residence", example="Belgrade")]
    gender: Annotated[Literal["male", "female", "other"], Field(..., description="Gender of the patient", example="male")]
    height: Annotated[float, Field(...,gt=0,description="Height of the patient in meters", example=1.88)]
    weight: Annotated[float, Field(...,gt=0,description="Weight of the patient in kilograms", example=85.0)]


    @computed_field
    @property
    def bmi(self) -> float:
        return round(self.weight / (self.height ** 2), 2)
    

    @computed_field
    @property
    def verdict(self) -> str:
        if self.bmi < 18.5:
            return "Underweight"
        elif 18.5 <= self.bmi < 24.9:
            return "Normal"
        elif 25 <= self.bmi < 29.9:
            return "Overweight"
        else:
            return "Obese"
        

class PatientUpdate(BaseModel):
    name: Annotated[Optional[str], Field(None)]
    age: Annotated[Optional[int], Field(None,gt=0,le=120)]
    city: Annotated[Optional[str], Field(None)]
    gender: Annotated[Optional[Literal["male", "female", "other"]], Field(None)]
    height: Annotated[Optional[float], Field(None,gt=0)]
    weight: Annotated[Optional[float], Field(None,gt=0)]


# Load patient data from a JSON file
def load_data():
    with open("patients.json","r") as f:
        data = json.load(f)
    return data

# save or write data to the JSON file
def save_data(data):
    with open ("patients.json","w") as f:
        json.dump(data,f)


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


@app.post("/create")
def create_patient(patient: Patient): # the data will come in json format and pydantic will convert it to Patient class object (pydantic model)

    # Load existing data
    data = load_data() # it is in dict format

    # check if the patient id already exists
    if patient.id in data:
        raise HTTPException(status_code=400,detail="Patient with this ID already exists in the Database")

    # new patient add to the DB
    data[patient.id] = patient.model_dump(exclude=['id']) # convert pydantic object/model to dict

    # save the updated data back to the JSON file
    save_data(data)


    return JSONResponse(status_code=201,content={"message":"Patient record created successfully."})


@app.put("/update/{patient_id}")
def update_patient(patient_update: PatientUpdate, patient_id: str = Path(..., description="ID of the patient to update", example="P001")):
    data = load_data()

    if patient_id not in data:
        raise HTTPException(status_code=404,detail="Patient not found in the Database")
    
    existing_patient_data = data[patient_id] # existing data in dict format from the JSON patient.json file

    update_data = patient_update.model_dump(exclude_unset=True) # get only the fields that were provided in the update request body

    # update the existing data with new values
    for key, value in update_data.items():
        existing_patient_data[key] = value

    # create a new Patient pydantic object with updated data
    updated_patient = Patient(id=patient_id, **existing_patient_data)

    # update the data dict with the updated patient data without id as it is the key in the dict 
    data[patient_id] = updated_patient.model_dump(exclude=['id'])

    save_data(data) # save the updated data back to the JSON file

    return JSONResponse(status_code=200,content={"message":"Patient record updated successfully."})