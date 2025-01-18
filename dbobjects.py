# Running this file creates the tables in the database

from sqlalchemy import create_engine, Column, Integer, String, Float, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import declarative_base
from dbconn import DB_URL

Base = declarative_base()

class Player(Base):
    __tablename__ = 'players'

    player_id = Column(Integer(), primary_key=True)
    player_firstname = Column(String(100), nullable=False)
    player_lastname = Column(String(100), nullable=False)
    player_pdga_id = Column(Integer())
    player_sda_id = Column(String(100)) 
    player_swisstour_license = Column(Boolean)
    player_city = Column(String(100))
    player_state = Column(String(100))
    player_country = Column(String(100))
    player_classification = Column(String(100))
    player_pdga_since = Column(DateTime())
    player_pdga_status = Column(String(100))
    player_pdga_expiry = Column(DateTime())
    player_official_status = Column(String(100))
    player_official_expiry = Column(DateTime())
    player_rating = Column(Integer())
    player_no_events = Column(Integer())
    player_no_wins = Column(Integer())
    player_earnings = Column(Float())

class Event(Base):
    __tablename__ = 'events'

    event_id = Column(Integer(), primary_key=True)
    event_name = Column(String(250),nullable=False)
    event_tier = Column(String(100))
    event_date = Column(DateTime())
    event_days = Column(Integer())
    event_city = Column(String(100))
    event_state = Column(String(100))
    event_country = Column(String(100))
    event_no_players = Column(Integer())
    event_purse = Column(Float())

class Tournament(Base):
    __tablename__ = 'tournaments'

    tournament_id = Column(Integer(), primary_key=True)
    player_id = Column(Integer(),ForeignKey(Player.player_id,ondelete='CASCADE'),nullable=False)
    event_id = Column(Integer(),ForeignKey(Event.event_id,ondelete='CASCADE'),nullable=False)
    tournament_division = Column(String(100))
    tournament_place = Column(Integer())
    tournament_swisstour_points = Column(Integer())
    tournament_rating = Column(Integer())
    tournament_prize = Column(Float())
    tournament_propagator = Column(Boolean())
    tournament_score = Column(Integer())

# Create the engine
engine = create_engine(DB_URL)
# Create the tables
Base.metadata.create_all(engine)