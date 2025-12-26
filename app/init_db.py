from sqlalchemy.orm import Session
from sqlalchemy import text
from .database import SessionLocal, engine
from . import models, auth
import hashlib
import uuid

# Helper to hash keys
def hash_key(key: str) -> str:
    return hashlib.sha256(key.encode()).hexdigest()

def init_db():
    db = SessionLocal()
    try:
        # Create Indexes if they don't exist (using raw SQL for specific index types/clauses that might be verbose in SQLAlchemy Core)
        # Check if index exists usually requires inspecting system tables, but 'IF NOT EXISTS' handles it in Postgres.
        with engine.connect() as con:
            con.execute(text("CREATE INDEX IF NOT EXISTS idx_txn_venue_time ON transactions (venue_id, timestamp DESC);"))
            con.commit()
        print("Indexes created/verified.")

        # Check if we have users
        if not db.query(models.User).filter(models.User.email == "admin@example.com").first():
            print("Seeding admin user...")
            admin_user = models.User(
                email="admin@example.com",
                hashed_password=auth.get_password_hash("changeme")  # CHANGE IN PRODUCTION!
            )
            db.add(admin_user)
            db.commit()
            print("Admin user seeded.")

        # Check if we have venues
        existing_venues = db.query(models.Venue).count()
        if existing_venues > 0:
            print("Venues already seeded.")
            return

        print("Seeding venues...")
        
        # 5 Dummy bars in London, Ontario
        # Coordinates approx for London, ON: 42.9849 N, 81.2453 W
        venues_list = [
            {"id": "00000000-0000-0000-0000-000000000001", "name": "Joe Kool's", "location_lat": 42.9849, "location_lon": -81.2453, "capacity": 150, "owner_api_key_hash": hash_key("key1"), "secret_key_hash": "secret_joe"},
            {"id": "00000000-0000-0000-0000-000000000002", "name": "Barney's", "location_lat": 42.9855, "location_lon": -81.2460, "capacity": 200, "owner_api_key_hash": hash_key("key2"), "secret_key_hash": "secret_barney"},
            {"id": "00000000-0000-0000-0000-000000000003", "name": "Molly Bloom's", "location_lat": 42.9830, "location_lon": -81.2500, "capacity": 120, "owner_api_key_hash": hash_key("key3"), "secret_key_hash": "secret_molly"},
            {"id": "00000000-0000-0000-0000-000000000004", "name": "The Ceeps", "location_lat": 42.9860, "location_lon": -81.2480, "capacity": 300, "owner_api_key_hash": hash_key("key4"), "secret_key_hash": "secret_ceeps"},
            {"id": "00000000-0000-0000-0000-000000000005", "name": "Toboggan Brewing Co.", "location_lat": 42.9840, "location_lon": -81.2470, "capacity": 180, "owner_api_key_hash": hash_key("key5"), "secret_key_hash": "secret_toboggan"}
        ]

        for v_data in venues_list:
            venue = models.Venue(**v_data)
            db.add(venue)
        
        db.commit()
        print("Seeding complete: 5 venues added.")

    except Exception as e:
        print(f"Error seeding DB: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    init_db()

