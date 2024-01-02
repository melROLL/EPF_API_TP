import uvicorn
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2AuthorizationCodeBearer
from google.cloud import firestore
from firebase_admin import auth, credentials, initialize_app
from fastapi_limiter import FastAPILimiter
from fastapi_limiter.depends import RateLimiter
from pydantic import BaseModel
from starlette.responses import JSONResponse


# Initialize Firestore client
db = firestore.Client()


## MODIFY HERE: DontGiveTheSecretInformationToClement
# Initialize Firebase Admin SDK 
cred = credentials.Certificate("apiepf-firebase-adminsdk-axcvn-74308a4ed6.json")
initialize_app(cred)
# initialize_app(cred, {'projectId': 'apiepf',})  
# initialize_app(cred, {'projectId': 'apiepf', 'databaseURL': 'https://apiepf.firebaseio.com'})

# Create Firestore collection if it doesn't exist
# Create Firestore collection if it doesn't exist
parameters_collection = db.collection("parameters")
if not parameters_collection.get():
    # Create document with default parameters
    default_parameters = {
        "n_estimators": 100,
        "criterion": "gini"
    }
    parameters_collection.document("parameters").set(default_parameters)

# Create Firestore collection for users
users_collection = db.collection("users")

# Configure FastAPI application without API version and prefix but it works
# app = FastAPI()


# Configure FastAPI application with API version and prefix
app = FastAPI(
    title="EPF_API",
    description="API for EPF project this is the description made by Melvyn",
    version="1.0",
    openapi_url="/v1/openapi.json",  # Provide the correct version in the URL
    docs_url="/v1/docs",  # Provide the correct version in the URL
    redoc_url="/v1/redoc",  # Provide the correct version in the URL
)



# Firebase Authentication
oauth2_scheme = OAuth2AuthorizationCodeBearer(tokenUrl="token")


async def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        decoded_token = auth.verify_id_token(token)
        uid = decoded_token['uid']
        user = auth.get_user(uid)
        return user
    except auth.AuthError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Authentication failed: {str(e)}"
        )


# model for parameters response
class Parameters(BaseModel):
    n_estimators: int
    criterion: str



# Endpoint to retrieve parameters from Firestore with rate limiting and API versioning
@app.get("/v1/get-parameters", response_model=Parameters, dependencies=[Depends(get_current_user), RateLimiter(times=5, minutes=1)])
async def get_parameters():
    try:
        parameters_document = parameters_collection.document("parameters").get().to_dict()
        if not parameters_document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Parameters not found",
            )
        return parameters_document

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve parameters. Error: {str(e)}"
        )

# Step 20: Custom error handler for 404 errors
async def not_found_error_handler(request, exc):
    return JSONResponse(
        status_code=404,
        content={"message": "Error 404 Resource not found"},
    )
    


# Endpoint to update parameters in Firestore
@app.put("/update-parameters", response_model=dict, dependencies=[Depends(get_current_user)])
async def update_parameters(new_parameters: Parameters):
    try:
        # Update parameters in Firestore
        parameters_collection.document("parameters").update(new_parameters.dict())

        return {"message": "Parameters updated successfully"}

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update parameters. Error: {str(e)}"
        )


# Endpoint to add parameters to Firestore
@app.post("/add-parameters", response_model=dict, dependencies=[Depends(get_current_user)])
async def add_parameters(new_parameters: Parameters):
    try:
        # Add new parameters to Firestore
        parameters_collection.document("parameters").set(new_parameters.dict())

        return {"message": "Parameters added successfully"}

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to add parameters. Error: {str(e)}"
        )


# models for user registration and login
class UserRegistration(BaseModel):
    email: str
    password: str


class UserLogin(BaseModel):
    email: str
    password: str


# Endpoint to register a new user
@app.post("/register", response_model=dict)
async def register_user(user_data: UserRegistration):
    try:
        # Create user in Firebase Authentication
        new_user = auth.create_user(
            email=user_data.email,
            password=user_data.password
        )

        # Add user to Firestore collection
        users_collection.document(new_user.uid).set({"email": user_data.email})

        return {"message": "User registered successfully"}

    except auth.AuthError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"User registration failed: {str(e)}"
        )
        

# Endpoint to log in a user and return an authentication token
@app.post("/login", response_model=dict)
async def login_user(user_data: UserLogin):
    try:
        # Sign in user and get authentication token
        user = auth.sign_in_with_email_and_password(user_data.email, user_data.password)

        return {"message": "User logged in successfully", "token": user['idToken']}

    except auth.AuthError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Login failed: {str(e)}"
        )

# Endpoint to log out a user
@app.post("/logout", response_model=dict, dependencies=[Depends(get_current_user)])
async def logout_user():
    return {"message": "User logged out successfully"}

# Endpoint to list users (accessible only to admin users)
@app.get("/list-users", response_model=list, dependencies=[Depends(get_current_user)])
async def list_users(current_user: dict = Depends(get_current_user)):
    # Check if the user is an admin
    if 'admin' in current_user['customClaims'] and current_user['customClaims']['admin']:
        # List users from Firestore collection
        users = users_collection.stream()
        return [{"uid": user.id, **user.to_dict()} for user in users]
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied. Only admin users can list users."
        )

## DDOS Atack security with FastAPI Limiter
# Configure rate limiting settings
FastAPILimiter.init_app(app, redis_url="redis://localhost", enabled=True)


# Run the FastAPI application
if __name__ == "__main__":
    uvicorn.run("main:app", debug=True, reload=True, port=8080)