from fastapi import FastAPI
from routes import users, loans
import database

# Intializing FastAPI
app = FastAPI()

# Create database tables
database.Base.metadata.create_all(bind=database.engine)

# Include routes for handling users and loans
app.include_router(users.router)
app.include_router(loans.router)


@app.get("/")
def home():
    """
    Root endpoint to check if the API is running.

    Returns:
        dict: A simple message confirming that the API is functioning properly.
    """
    return {"message": "Loan Amortization API"}
