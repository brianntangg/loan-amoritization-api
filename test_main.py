import uuid
import pytest
from fastapi import HTTPException
from loan_calculations import generate_amortization_schedule, calculate_loan_summary
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_home():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Loan Amortization API"}


def test_create_user():
    # Creates a new user every time
    unique_email = f"testuser_{uuid.uuid4().hex[:6]}@example.com"

    user_data = {
        "name": "testuser",
        "email": unique_email
    }

    # Adds user to database
    response = client.post("/users/", json=user_data)
   
    # Tests if user was sucessfully added
    assert response.status_code == 201
    assert response.json()["name"] == "testuser"
    assert response.json()["email"] == unique_email

    # Cleanup: Delete user after test
    user_id = response.json().get("id")
    client.delete(f"/users/{user_id}")


def test_create_loan():
    loan_data = {
        "user_id": 1,
        "amount": 10000,
        "annual_interest_rate": 5.0,
        "loan_term_months": 12
    }

    # Adds loan to database
    response = client.post("/loans/", json=loan_data)
   
    # Tests if loan was sucessfully added
    assert response.status_code == 201
    assert response.json()["amount"] == 10000
    assert response.json()["annual_interest_rate"] == 5.0
    assert response.json()["loan_term_months"] == 12
   
    # Cleanup: Delete user after test
    loan_id = response.json().get("id")
    client.delete(f"/users/{loan_id}")


def test_fetch_loan_schedule():
    loan_data = {
        "user_id": 1,
        "amount": 10000,
        "annual_interest_rate": 5.0,
        "loan_term_months": 12
    }

    # Adds loan to database
    loan_response = client.post("/loans/", json=loan_data)

    # Fetch loan schedule
    loan_id = loan_response.json()["id"]
    schedule_response = client.get(f"/loans/{loan_id}/schedule")
    assert schedule_response.status_code == 200

    # Checks if loan term is 12 months
    schedule = schedule_response.json()
    assert len(schedule) == 12

    # Check if the first month contains the expected fields
    first_month = schedule[0]
    assert "month" in first_month
    assert "remaining_balance" in first_month
    assert "monthly_payment" in first_month

    # Cleanup: delete loan after test
    client.delete(f"/loans/{loan_id}")


def test_fetch_loan_summary():
    loan_data = {
        "user_id": 1,
        "amount": 10000,
        "annual_interest_rate": 5.0,
        "loan_term_months": 12
    }

    # Adds loan to database
    loan_response = client.post("/loans/", json=loan_data)

    # Fetch loan summary for month 6
    loan_id = loan_response.json()["id"]
    month = 6
    summary_response = client.get(f"/loans/{loan_id}/summary?month={month}")
    assert summary_response.status_code == 200, summary_response.text
   
    # Ensure expected fields are present
    summary = summary_response.json()
    assert "current_principal_balance" in summary
    assert "total_principal_paid" in summary
    assert "total_interest_paid" in summary

    # Ensure values are non-negative
    assert summary["current_principal_balance"] >= 0
    assert summary["total_principal_paid"] >= 0
    assert summary["total_interest_paid"] >= 0

    # Cleanup: delete loan after test
    client.delete(f"/loans/{loan_id}")


def test_fetch_user_loans():
    # Create a new user data
    unique_email = f"testuser_{uuid.uuid4().hex[:6]}@example.com"
    user_data = {"name": "testuser", "email": unique_email}

    # Adds user to database
    user_response = client.post("/users/", json=user_data)

    # Checks is user was successfully added
    assert user_response.status_code == 201

    # Create multiple loans for the user
    user_id = user_response.json()["id"]
    loan_data_1 = {
        "user_id": user_id,
        "amount": 5000,
        "annual_interest_rate": 4.5,
        "loan_term_months": 24
    }
    loan_data_2 = {
        "user_id": user_id,
        "amount": 10000,
        "annual_interest_rate": 6.0,
        "loan_term_months": 36
    }

    client.post("/loans/", json=loan_data_1)
    client.post("/loans/", json=loan_data_2)

    # Fetch all loans for the user
    loans_response = client.get(f"/loans/user/{user_id}")
    assert loans_response.status_code == 200

    loans = loans_response.json()
    assert isinstance(loans, list)
    assert len(loans) == 2  # Ensure two loans were retrieved

    # Ensure correct loan data
    assert loans[0]["amount"] == 5000
    assert loans[0]["annual_interest_rate"] == 4.5
    assert loans[0]["loan_term_months"] == 24

    assert loans[1]["amount"] == 10000
    assert loans[1]["annual_interest_rate"] == 6.0
    assert loans[1]["loan_term_months"] == 36

    # Cleanup: Delete loans and user
    for loan in loans:
        client.delete(f"/loans/{loan['id']}")
    client.delete(f"/users/{user_id}")


def test_share_loan():
    # Create two users
    user_1_email = f"userOne_{uuid.uuid4().hex[:6]}@example.com"
    user_2_email = f"userTwo_{uuid.uuid4().hex[:6]}@example.com"

    user_1_response = client.post("/users/", json={"name": "UserOne", "email": user_1_email})
    user_2_response = client.post("/users/", json={"name": "UserTwo", "email": user_2_email})

    user_1_id = user_1_response.json().get("id")
    user_2_id = user_2_response.json().get("id")

    # Create a loan for User 1
    loan_data = {
        "user_id": user_1_id,
        "amount": 5000,
        "annual_interest_rate": 4.5,
        "loan_term_months": 24
    }
    loan_response = client.post("/loans/", json=loan_data)

    # Try sharing the loan with User 2
    loan_id = loan_response.json().get("id")
    share_response = client.post(f"/loans/{loan_id}/share/{user_2_id}")
    assert share_response.status_code == 200
    assert "Loan" in share_response.json()["message"]

    # Cleanup to delete loan and users
    client.delete(f"/loans/{loan_id}")
    client.delete(f"/users/{user_1_id}")
    client.delete(f"/users/{user_2_id}")


def test_generate_amortization_schedule():
    amount = 1000
    interest_rate = 5.0
    term_months = 12

    schedule = generate_amortization_schedule(amount, interest_rate, term_months)

    assert len(schedule) == term_months
    assert schedule[0]["month"] == 1
    assert schedule[-1]["month"] == term_months
    assert schedule[-1]["remaining_balance"] == 0  # Loan should be fully paid off


def test_calculate_loan_summary():
    amount = 1000
    interest_rate = 5
    term_months = 12
    month = 6

    summary = calculate_loan_summary(amount, interest_rate, term_months, month)

    assert summary["month"] == month
    assert summary["current_principal_balance"] >= 0
    assert summary["total_principal_paid"] > 0
    assert summary["total_interest_paid"] > 0

    # Tests for invalid month (should raise HTTPException)
    with pytest.raises(HTTPException) as exc_info:
        calculate_loan_summary(amount, interest_rate, term_months, term_months + 1)

    assert exc_info.value.status_code == 400
    assert "Invalid month requested" in exc_info.value.detail


def test_invalid_user_name():
    # Invalid name: contains numbers
    invalid_user_data = {
        "name": "Invalid123",
        "email": f"invaliduser_{uuid.uuid4().hex[:6]}@example.com"
    }
    response = client.post("/users/", json=invalid_user_data)
    assert response.status_code == 422
    assert "name" in response.json()["detail"][0]["loc"]

    # Invalid name: contains special characters
    invalid_user_data["name"] = "@Invalid!"
    response = client.post("/users/", json=invalid_user_data)
    assert response.status_code == 422

    # Valid name: should pass
    invalid_user_data["name"] = "Valid Name"
    response = client.post("/users/", json=invalid_user_data)
    assert response.status_code == 201

    # Cleanup: delete created user
    user_id = response.json().get("id")
    client.delete(f"/users/{user_id}")


def test_invalid_empty_name_and_email():
    # Both fields empty test
    invalid_user_data = {"name": "", "email": ""}
    response = client.post("/users/", json=invalid_user_data)
    assert response.status_code == 422
    errors = response.json()["detail"]
    assert any("name" in error["loc"] for error in errors)
    assert any("email" in error["loc"] for error in errors)

    # Empty email test
    invalid_user_data["name"] = "Valid Name"
    response = client.post("/users/", json=invalid_user_data)
    assert response.status_code == 422

    # Empty name test
    invalid_user_data["name"] = ""
    invalid_user_data["email"] = "valid@example.com"
    response = client.post("/users/", json=invalid_user_data)
    assert response.status_code == 422
