from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base

class User(Base):
    # This defines the table name in our SQLite database
    __tablename__ = "users"

    # Define the columns for the user table. 'primary_key=True' makes this the unique ID.
    # 'index=True' speeds up database searches when looking up by this column.
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True) # unique=True prevents duplicate emails
    hashed_password = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Establish a One-to-Many relationship with the Prediction table.
    # This means one User can have many Predictions. 'back_populates' links it to the 'user' field in Prediction.
    predictions = relationship("Prediction", back_populates="user")

class Prediction(Base):
    # This defines the table name where all history records are saved
    __tablename__ = "predictions"

    # Core prediction record ID
    id = Column(Integer, primary_key=True, index=True)
    
    # ForeignKey links this prediction to a specific user in the 'users' table (One-to-Many)
    user_id = Column(Integer, ForeignKey("users.id"))
    
    # The two drugs being compared
    drug_a = Column(String)
    drug_b = Column(String)
    
    # Optional metadata that the user can provide
    indication = Column(String, nullable=True)
    substance = Column(String, nullable=True)
    
    # ML Output fields
    severity_label = Column(String) # e.g., DEATH RISK, HOSPITAL ADMISSION
    confidence_score = Column(Float) # Probability score from 0 to 1
    explanation = Column(String) # Text explanation from the explainer service
    
    # Clinical recommendations and SHAP feature drivers
    recommendation = Column(String, nullable=True)
    alternatives = Column(String, nullable=True) # List of safe substitutes
    risk_factors = Column(String, nullable=True) # E.g., CYP450 Inhibition
    risk_score = Column(Float, nullable=True) # Mapped 0-100 score for the UI gauge
    
    # Timestamp of when the prediction was made
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationship pointing back to the User who made this prediction
    user = relationship("User", back_populates="predictions")
