from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import models, schemas, database, services

router = APIRouter(prefix="/loans", tags=["Loans"])


@router.post("/", response_model=schemas.LoanResponse, status_code=201)
def create_loan(loan: schemas.LoanCreate, db: Session = Depends(database.get_db)):
    db_loan = models.Loan(**loan.model_dump())
    db.add(db_loan)
    db.commit()
    db.refresh(db_loan)
    return db_loan


@router.post("/{loan_id}/share/{user_id}", status_code=200)
def share_loan(loan_id: int, user_id: int, db: Session = Depends(database.get_db)):
    # Check if loan exists
    loan = db.query(models.Loan).filter(models.Loan.id == loan_id).first()
    if not loan:
        raise HTTPException(status_code=404, detail="Loan not found")

    # Check if user exists
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Check if loan is already shared with this user
    existing_share = db.query(models.SharedLoan).filter(
        models.SharedLoan.loan_id == loan_id,
        models.SharedLoan.user_id == user_id
    ).first()

    if existing_share:
        raise HTTPException(status_code=400, detail="Loan already shared with this user")

    # Share the loan
    shared_loan = models.SharedLoan(loan_id=loan_id, user_id=user_id)
    db.add(shared_loan)
    db.commit()
    
    return {"message": f"Loan {loan_id} shared with user {user_id}"}


@router.get("/{loan_id}", response_model=schemas.LoanResponse)
def get_loan(loan_id: int, db: Session = Depends(database.get_db)):
    loan = db.query(models.Loan).filter(models.Loan.id == loan_id).first()
    if not loan:
        raise HTTPException(status_code=404, detail="Loan not found")
    return loan


@router.get("/{loan_id}/schedule")
def get_loan_schedule(loan_id: int, db: Session = Depends(database.get_db)):
    loan = db.query(models.Loan).filter(models.Loan.id == loan_id).first()
    if not loan:
        raise HTTPException(status_code=404, detail="Loan not found")
    return services.generate_amortization_schedule(loan.amount, loan.annual_interest_rate, loan.loan_term_months)


@router.get("/{loan_id}/summary")
def get_loan_summary(loan_id: int, month: int, db: Session = Depends(database.get_db)):
    loan = db.query(models.Loan).filter(models.Loan.id == loan_id).first()
    if not loan:
        raise HTTPException(status_code=404, detail="Loan not found")
    return services.calculate_loan_summary(loan.amount, loan.annual_interest_rate, loan.loan_term_months, month)


@router.get("/user/{user_id}", response_model=list[schemas.LoanResponse])
def get_user_loans(user_id: int, db: Session = Depends(database.get_db)):
    # Fetch loans owned by the user
    user_loans = db.query(models.Loan).filter(models.Loan.user_id == user_id).all()

    # Fetch loans shared with the user
    shared_loans = db.query(models.Loan).join(models.SharedLoan).filter(models.SharedLoan.user_id == user_id).all()
    
    if not user_loans or shared_loans:
        raise HTTPException(status_code=404, detail="No loans found for this user")
    return user_loans + shared_loans
