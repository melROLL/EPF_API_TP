import json

# Read model parameters from the JSON file
with open("src/config/model_parameters.json", "r") as file:
    model_parameters = json.load(file)

# Extract parameters
n_estimators = model_parameters["parameters"]["n_estimators"]
max_depth = model_parameters["parameters"]["max_depth"]
min_samples_split = model_parameters["parameters"]["min_samples_split"]
min_samples_leaf = model_parameters["parameters"]["min_samples_leaf"]
bootstrap = model_parameters["parameters"]["bootstrap"]

# Use the parameters in your model initialization
model = RandomForestClassifier(
    n_estimators=n_estimators,
    max_depth=max_depth,
    min_samples_split=min_samples_split,
    min_samples_leaf=min_samples_leaf,
    bootstrap=bootstrap
)
