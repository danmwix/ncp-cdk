#!/usr/bin/env python
"""Initialize the database with all tables and seed data"""
from app import create_app, db
from app.models import DisabilityCategory, DisabilitySubcategory, User, Child
from app.forms import DISABILITY_CATEGORIES

app = create_app()

with app.app_context():
    # Create all tables
    print("Creating database tables...")
    db.create_all()
    
    # Verify tables exist
    inspector = db.inspect(db.engine)
    tables = inspector.get_table_names()
    print(f"\nTables created: {tables}")
    
    # Clear existing data
    print("\nClearing existing data...")
    DisabilitySubcategory.query.delete()
    DisabilityCategory.query.delete()
    db.session.commit()
    
    # Seed disability categories and subcategories
    print("Seeding disability categories and subcategories...")
    for category_name, category_data in DISABILITY_CATEGORIES.items():
        category = DisabilityCategory(
            name=category_name,
            code=category_data['code']
        )
        db.session.add(category)
        db.session.flush()
        
        for subcategory_name in category_data['subcategories']:
            subcategory = DisabilitySubcategory(
                name=subcategory_name,
                category=category
            )
            db.session.add(subcategory)
    
    db.session.commit()
    
    print("✅ Database initialized successfully!")
    print(f"✅ Created {DisabilityCategory.query.count()} disability categories")
    print(f"✅ Created {DisabilitySubcategory.query.count()} disability subcategories")
