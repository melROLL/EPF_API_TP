from fastapi import APIRouter
import pandas as pd

router = APIRouter()

@router.get("/process-iris-dataset")
async def process_iris_dataset():
    # Specify the path to the Iris dataset file
    dataset_path = "services\epf-flower-data-science\src\api\routes\data\Iris.csv"

    try:
        # Load the dataset into a Pandas DataFrame
        df = pd.read_csv(dataset_path)

        # Perform processing on the dataset (example: drop columns)
        # Modify this part based on your specific processing needs
        processed_df = df.drop(columns=['SomeColumnToDrop'])

        # Convert the processed DataFrame to JSON
        processed_df_json = processed_df.to_json(orient="records")

        return processed_df_json

    except FileNotFoundError:
        return {"error": "Iris dataset file not found."}
