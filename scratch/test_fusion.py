import sys
sys.path.insert(0, 'backend')
from app.ml.fusion_net import fusion_net

tests = [
    ('WARFARIN', 'ASPIRIN'),
    ('METFORMIN', 'LISINOPRIL'),
    ('SIMVASTATIN', 'DILTIAZEM'),
    ('ACETAMINOPHEN', 'IBUPROFEN'),
    ('UNKNOWNDRUG1', 'UNKNOWNDRUG2'),
]

print("Drug A           | Drug B           | Source          | Severity               | Conf  | Risk")
print("-" * 105)
for a, b in tests:
    r = fusion_net.predict_interaction(a, b)
    src   = r["source"]
    sev   = r["severity"]
    conf  = r["confidence"]
    risk  = r["risk_score"]
    rep   = r.get("faers_reports", 0)
    print(f"{a:<17}| {b:<17}| {src:<16}| {sev:<23}| {conf:<6}| {risk}  (reports={rep})")
