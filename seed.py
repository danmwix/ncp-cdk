from app import create_app, db
from app.models import DisabilityCategory, DisabilitySubcategory
from app.forms import DISABILITY_CATEGORIES

app = create_app()

with app.app_context():
    # Clear existing data
    DisabilitySubcategory.query.delete()
    DisabilityCategory.query.delete()
    db.session.commit()
    
    # Create categories and subcategories
    for category_name, category_data in DISABILITY_CATEGORIES.items():
        category = DisabilityCategory(
            name=category_name,
            code=category_data['code']
        )
        db.session.add(category)
        db.session.flush()  # Get the category ID
        
        # Create subcategories
        for subcategory_name in category_data['subcategories']:
            subcategory = DisabilitySubcategory(
                name=subcategory_name,
                category=category
            )
            db.session.add(subcategory)
    
    db.session.commit()
    print("✅ Disability categories and subcategories seeded successfully!")