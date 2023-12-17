from fastapi import APIRouter
import pandas as pd
from sklearn.model_selection import train_test_split
from fastapi import APIRouter
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from joblib import dump

dataset_path = "services\epf-flower-data-science\src\api\routes\data\Iris.csv"

router = APIRouter()

@router.get("/split-iris-dataset")
async def split_iris_dataset():
    dataset_path = "services\epf-flower-data-science\src\api\routes\data\Iris.csv"
    
    try:
        # Load the dataset into a Pandas DataFrame
        df = pd.read_csv(dataset_path)

        # Assuming the target column is 'species'
        X = df.drop(columns=['species'])
        y = df['species']

        # Split the dataset into train and test sets
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

        # Convert the train and test sets to JSON
        train_set = pd.concat([X_train, y_train], axis=1).to_json(orient="records")
        test_set = pd.concat([X_test, y_test], axis=1).to_json(orient="records")

        return {"train_set": train_set, "test_set": test_set}

    except FileNotFoundError:
        return {"error": "Iris dataset file not found."}
 
 
#step 11   
router.post("/train-classification-model")
async def train_classification_model(processed_data: pd.DataFrame):
    try:
        # Assuming the target column is 'species'
        X = processed_data.drop(columns=['species'])
        y = processed_data['species']

        # Initialize the classification model (adjust parameters)
        model = RandomForestClassifier(n_estimators=100, max_depth=None, random_state=42)

        # Train the model
        model.fit(X, y)

        # Save the trained model
        model_path = "src/models/classification_model.joblib"
        dump(model, model_path)

        return {"message": "Model trained and saved successfully."}

    except Exception as e:
        return {"error": f"Failed to train the model. Error: {str(e)}"}
    
#step 12
from fastapi import APIRouter
import pandas as pd
from joblib import load

router = APIRouter()

@router.post("/predict-with-model")
async def predict_with_model(features: pd.DataFrame):
    try:
        # Load the trained model
        model_path = "src/models/classification_model.joblib"
        model = load(model_path)

        # Make predictions
        predictions = model.predict(features)

        # Convert predictions to JSON
        predictions_json = pd.DataFrame(predictions, columns=['prediction']).to_json(orient="records")

        return predictions_json

    except Exception as e:
        return {"error": f"Failed to make predictions. Error: {str(e)}"}

