from app import create_app, db
from app.models import DisabilityCategory

app = create_app()

with app.app_context():
    disabilities = [
        ("Visual Impairment", "VI"),
        ("Hearing Impairment", "HI"),
        ("Deafblindness", "DB"),
        ("Physical Disabilities", "PD"),
        ("Intellectual Disabilities", "ID"),
        ("Learning Disabilities", "LD"),
        ("Autism Spectrum Disorders", "ASD"),
        ("Emotional and Behavioural Difficulties", "EBD"),
        ("Communication Disorders", "CD"),
        ("Multiple Disabilities", "MD"),
        ("Gifted and Talented", "GT")
    ]
    
    for name, code in disabilities:
        if not DisabilityCategory.query.filter_by(code=code).first():
            db.session.add(DisabilityCategory(name=name, code=code))
    
    db.session.commit()
    print("✅ Disability categories seeded successfully!")