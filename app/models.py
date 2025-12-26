from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid
import datetime
from .database import Base

class Venue(Base):
    __tablename__ = "venues"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    # Storing location as a string "lat,lon" as requested, or we can do separate fields.
    # The prompt asked for "location (lat/lon)". I will use two float columns for better querying usually,
    # but to be strict with the schema description "location" I will define it as a string but docstring it.
    # However, meaningful geo usage requires lat/lon separation or PostGIS.
    # Let's verify standard interpretations. "location (lat/lon)" usually suggests the 'concept' of location is stored via lat/lon.
    # I'll implement 'location_lat' and 'location_lon' to be safe and clean.
    # Actually, let's keep it simple and readable.
    location_lat = Column(Float, nullable=False)
    location_lon = Column(Float, nullable=False)
    capacity = Column(Integer, nullable=False)
    owner_api_key_hash = Column(String, nullable=False)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    secret_key_hash = Column(String, nullable=False) # Renamed from secret_key to indicate hashing

    transactions = relationship("Transaction", back_populates="venue")
    owner = relationship("User", back_populates="venues")

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    
    # Optional: Link user to specific venues if one-to-many
    venues = relationship("Venue", back_populates="owner")
    
class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    venue_id = Column(UUID(as_uuid=True), ForeignKey("venues.id"), nullable=False)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    quantity = Column(Integer, nullable=False)

    venue = relationship("Venue", back_populates="transactions")
