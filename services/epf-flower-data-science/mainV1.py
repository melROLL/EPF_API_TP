import uvicorn
from google.cloud import firestore
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi import HTTPException, Depends
from src.app import get_application

# Initialize Firestore client
db = firestore.Client()

# Create Firestore collection if it doesn't exist
parameters_collection = db.collection("parameters")
if not parameters_collection.get():
    # Create document with default parameters
    default_parameters = {
        "n_estimators": 100,
        "criterion": "gini"
    }
    parameters_collection.add(default_parameters)

app = get_application()


# Dependency to get the current parameters
def get_current_parameters():
    try:
        # Retrieve parameters from Firestore
        parameters_document = parameters_collection.get()[0].to_dict()
        return parameters_document
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve parameters. Error: {str(e)}")


@app.get("/get-parameters", response_class=JSONResponse)
async def get_parameters(current_parameters: dict = Depends(get_current_parameters)):
    return current_parameters


@app.put("/update-parameters", response_class=JSONResponse)
async def update_parameters(new_parameters: dict):
    try:
        # Update parameters in Firestore
        current_parameters = parameters_collection.get()[0]
        current_parameters.reference.update(new_parameters)

        return {"message": "Parameters updated successfully"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update parameters. Error: {str(e)}")


@app.post("/add-parameters", response_class=JSONResponse)
async def add_parameters(new_parameters: dict):
    try:
        # Add new parameters to Firestore
        parameters_collection.add(new_parameters)

        return {"message": "Parameters added successfully"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to add parameters. Error: {str(e)}")


if __name__ == "__main__":
    uvicorn.run("main:app", debug=True, reload=True, port=8080)

