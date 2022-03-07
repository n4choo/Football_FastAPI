from sqlmodel import SQLModel, create_engine
from .scrap import get_liga, get_player_stats, get_player_info
from .models import Player, Team, PlayerTeamLink


SQLALCHEMY_DATABASE_URL = "sqlite:///database.db"
# SQLALCHEMY_DATABASE_URL = "postgresql://user:password@postgresserver/db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

