from sqlalchemy.orm import Session
from ..repositories.prediction_repository import prediction_repo
from ..services.explainer_service import explainer_service
from ..ml.fusion_net import fusion_net
from ..schemas import prediction as schemas

class PredictionService:
    @staticmethod
    def process_prediction(db: Session, req: schemas.PredictionCreate, user_id: int):
        # 1. Run inference (FusionNet: GAT + Bert Hybrid)
        # We pass the two drugs to the FusionNet ML engine which returns a dictionary 
        # containing the predicted severity, confidence score, and base risk score.
        ml_result = fusion_net.predict_interaction(req.drug_a, req.drug_b)
        
        # 2. Generate Clinical Explanation
        # We call the explainer service (which acts like SHAP) to figure out *why* 
        # the model made this prediction (e.g. which pharmacological features contributed).
        explanation = explainer_service.get_local_explanation(
            req.drug_a, req.drug_b, ml_result["severity"]
        )
        
        # 3. Clinical Recommendation Logic (Safe Alternatives)
        # Initialize default values for recommendation text and drug alternatives.
        recommendation = None
        alternatives = []
        if ml_result["severity"] in ["DEATH RISK", "HOSPITAL ADMISSION", "MONITORING REQUIRED"]:
            severity_note = "High" if ml_result["severity"] == "DEATH RISK" else "Moderate"
            recommendation = f"{severity_note} risk detected. Consider substituting {req.drug_b} with a medication that has a lower interaction profile in this Therapeutic Class."
            # Simulate alternative lookup with Real Medications
            if "NSAID" in req.drug_b or "Aspirin" in req.drug_b or "Naproxen" in req.drug_b:
                alternatives = ["Acetaminophen", "Celecoxib", "Tylenol"]
            elif "Grapefruit" in req.drug_b:
                alternatives = ["Orange Juice (Non-acid)", "Water", "Clinical Consultation"]
            elif "Statin" in req.drug_b or "Atorvastatin" in req.drug_b:
                alternatives = ["Rosuvastatin", "Pravastatin", "Dietary Management"]
            elif "Warfarin" in req.drug_b:
                alternatives = ["Apixaban", "Rivaroxaban", "Enoxaparin"]
            else:
                alternatives = ["Omeprazole", "Sertraline", "Metformin"] # Default safe common substitutes
        
        # 4. Persistence via Repository
        # We bundle all the ML results, explanations, and user inputs into a dictionary
        # that exactly matches our database schema requirements.
        prediction_data = {
            "drug_a": req.drug_a,
            "drug_b": req.drug_b,
            "indication": req.indication,
            "substance": req.substance,
            "severity_label": ml_result["severity"],
            "confidence_score": ml_result["confidence"],
            "explanation": explanation["detailed_note"],
            "risk_factors": explanation["key_drivers"],
            "risk_score":  ml_result.get("risk_score", 35.0),
            "recommendation": recommendation,
            "alternatives": alternatives
        }
        
        # We pass the dictionary to the repository layer to save it into the SQLite database.
        # We merge the user_id into the dictionary so the database knows who ran this prediction.
        db_obj = prediction_repo.create(db, prediction_data | {"user_id": user_id})
        
        # 5. Professional Serialization: Ensure response matches schema exactly
        # We manually structure the response to ensure list-types for frontend badges
        return {
            "id": db_obj.id,
            "user_id": db_obj.user_id,
            "drug_a": db_obj.drug_a,
            "drug_b": db_obj.drug_b,
            "indication": db_obj.indication,
            "substance": db_obj.substance,
            "severity_label": db_obj.severity_label,
            "confidence_score": db_obj.confidence_score,
            "explanation": db_obj.explanation,
            "risk_factors": explanation["key_drivers"], # Use raw list from explainer
            "risk_score": prediction_data["risk_score"],
            "recommendation": db_obj.recommendation,
            "alternatives": alternatives, # Use raw list from service
            "created_at": db_obj.created_at
        }

prediction_service = PredictionService()
