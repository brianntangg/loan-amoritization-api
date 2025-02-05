# Loan Amortization API

## Overview
The **Loan Amortization API** is a RESTful web service built with **FastAPI** that allows users to create loans, generate amortization schedules, and track loan summaries. The API also supports loan sharing between users.

## Features
- **User Management**
  - Create and fetch users.
- **Loan Management**
  - Create and fetch loans.
  - Fetch loan summaries for a specific month.
  - Fetch all loans for a specific user
  - Share loans with other users.
- **Automated Testing**
  - Comprehensive test suite using **pytest**.

## Technologies Used
- **FastAPI** - API framework for high-performance applications.
- **SQLAlchemy** - ORM for database management.
- **SQLite/PostgreSQL** - Database for storing users and loans.
- **Pydantic** - Data validation and serialization.
- **Pytest** - Automated testing framework.

## Installation
### Prerequisites
- Python 3.8+
- `pip` (Python package manager)
- `virtualenv` (recommended)

### Setup Instructions
1. **Clone the repository**
   ```bash
   git clone https://github.com/brianntangg/Greystone-Labs-Backend-Challenge.git
   cd Greystone-Labs-Backend-Challenge
   ```

2. **Create a virtual environment and activate it**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On macOS/Linux
   venv\Scripts\activate  # On Windows
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up the database**
   ```bash
   python main.py  # Initializes the database
   ```

5. **Run the API server**
   ```bash
   uvicorn main:app --reload
   ```

6. **Access the API**
   - Open your browser and visit: [http://127.0.0.1:8000]

## API Endpoints
### User Endpoints
| Method | Endpoint          | Description         |
|--------|------------------|---------------------|
| POST   | `/users/`        | Create a new user  |
| GET    | `/users/{user_id}`    | Retrieve a user by ID  |

### Loan Endpoints
| Method | Endpoint                  | Description          |
|--------|--------------------------|----------------------|
| POST   | `/loans/`                | Create a new loan  |
| GET    | `/loans/{loan_id}`            | Retrieve a loan by ID |
| GET    | `/loans/{loan_id}/schedule`   | Retrieve amortization schedule for a loan |
| GET    | `/loans/{loan_id}/summary` | Retrieve loan summary for a specific month |
| GET    | `/loans/user/{user_id}` | Retrieve all loans for a user |
| POST   | `/loans/{loan_id}/share/{user_id}` | Share a loan with another user |

## Testing
Run the test suite using **pytest**:
```bash
pytest test_main.py 
```

## Example Usage
### Creating a User
**Request:**
```json
POST /users/
{
    "name": "John Doe",
    "email": "john@example.com"
}
```

**Response:**
```json
{
    "id": 1,
    "name": "John Doe",
    "email": "john@example.com"
}
```

### Creating a Loan
**Request:**
```json
POST /loans/
{
    "user_id": 1,
    "amount": 10000,
    "annual_interest_rate": 5.0,
    "loan_term_months": 12
}
```

**Response:**
```json
{
    "id": 1,
    "user_id": 1,
    "amount": 10000,
    "annual_interest_rate": 5.0,
    "loan_term_months": 12
}
```

### Fetching Loan Schedule
**Request:**
```http
GET /loans/1/schedule
```

**Response:**
```json
[
    {"month": 1, "remaining_balance": 9167.12, "monthly_payment": 856.07},
    {"month": 2, "remaining_balance": 8330.43, "monthly_payment": 856.07},
    ...
]
```
