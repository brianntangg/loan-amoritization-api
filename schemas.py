from pydantic import BaseModel, EmailStr, Field

class UserCreate(BaseModel):
    name: str = Field(min_length=3, max_length=35, pattern=r"^[a-zA-Z\s]+$")
    email: EmailStr = Field(min_length=1)

class LoanCreate(BaseModel):
    user_id: int
    amount: float
    annual_interest_rate: float
    loan_term_months: int

class LoanResponse(BaseModel):
    id: int
    user_id: int
    amount: float
    annual_interest_rate: float
    loan_term_months: int

    class Config:
        from_attributes = True

class UserResponse(UserCreate):
    id: int

    class Config:
        from_attributes = True
