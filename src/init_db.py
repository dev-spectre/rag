# src/init_db.py
from src.database import engine, Base, SessionLocal, APIKey
from src.config import settings

def initialize_database():
    print("Initializing database...")
    
    # Create tables
    Base.metadata.create_all(bind=engine)
    print("Tables created.")
    
    # Add the initial API key if it doesn't exist
    db = SessionLocal()
    try:
        existing_key = db.query(APIKey).filter(APIKey.key == settings.SERVICE_API_KEY).first()
        if not existing_key:
            new_key = APIKey(
                key=settings.SERVICE_API_KEY, 
                description="Default service API key"
            )
            db.add(new_key)
            db.commit()
            print("Default service API key has been added to the database.")
        else:
            print("Default service API key already exists.")
    finally:
        db.close()

if __name__ == "__main__":
    initialize_database()