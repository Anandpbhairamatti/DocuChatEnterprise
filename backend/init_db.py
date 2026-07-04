import sys
import os
from sqlalchemy.orm import Session

# Add the backend directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.db.base import Base
from app.db.session import engine, SessionLocal
from app.models.department import Department
from app.models.user import User
from app.core.security import get_password_hash

def init_db():
    print("Creating tables in database...")
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        # Seed departments if empty
        if db.query(Department).count() == 0:
            print("Seeding departments...")
            engineering = Department(name="Engineering", description="Engineering Team")
            hr = Department(name="HR", description="Human Resources")
            sales = Department(name="Sales", description="Sales & Marketing")
            
            db.add_all([engineering, hr, sales])
            db.commit()
            print("Departments seeded successfully.")
        
        # Seed admin user if empty
        if db.query(User).filter(User.role == "Admin").count() == 0:
            print("Seeding admin user...")
            eng_dept = db.query(Department).filter(Department.name == "Engineering").first()
            
            admin_user = User(
                email="admin@example.com",
                hashed_password=get_password_hash("AdminPassword123"),
                full_name="System Admin",
                role="Admin",
                department_id=eng_dept.id if eng_dept else None,
                is_active=True,
                force_password_change=False
            )
            
            db.add(admin_user)
            db.commit()
            print("Admin user seeded successfully!")
            print("Credentials: admin@example.com / AdminPassword123")
        else:
            print("Database already initialized and seeded.")
            
    except Exception as e:
        db.rollback()
        print(f"Error seeding database: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    init_db()
