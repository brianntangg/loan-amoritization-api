from sqlalchemy import Column, Integer, Float, String, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class SharedLoan(Base):
    __tablename__ = "shared_loans"

    id = Column(Integer, primary_key=True, index=True)
    loan_id = Column(Integer, ForeignKey("loans.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    loan = relationship("Loan", back_populates="shared_users")
    user = relationship("User", back_populates="shared_loans")

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True)

    loans = relationship("Loan", back_populates="owner")
    shared_loans = relationship("SharedLoan", back_populates="user", cascade="all, delete")

class Loan(Base):
    __tablename__ = "loans"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    amount = Column(Float, nullable=False)
    annual_interest_rate = Column(Float, nullable=False)
    loan_term_months = Column(Integer, nullable=False)

    owner = relationship("User", back_populates="loans")
    shared_users = relationship("SharedLoan", back_populates="loan", cascade="all, delete")
