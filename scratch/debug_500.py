import sys
import os

# Add the backend to path
sys.path.append(os.path.abspath("backend"))

from app.db.database import SessionLocal
from app.services.prediction_service import prediction_service
from app.schemas.prediction import PredictionCreate

db = SessionLocal()
try:
    req = PredictionCreate(
        drug_a="Warfarin",
        drug_b="Fluconazole",
        indication="Testing",
        substance="Tablet"
    )
    result = prediction_service.process_prediction(db, req, user_id=1)
    print("Success!")
    print(result)
except Exception as e:
    import traceback
    print("Error detected:")
    traceback.print_exc()
finally:
    db.close()
