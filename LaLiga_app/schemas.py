from typing import List, Optional
from sqlmodel import Field, Session, SQLModel, create_engine, select
from .models import Team, Player, PlayerTeamLink

class Team_stats(SQLModel):
    name: str 
    partidos: int
    ganados: int
    empates: int
    perdidos: int
    gfavor: int
    gcontra: int
    puntos: int
    

class Read_Player(SQLModel):
    nombre: str 
    birthdate: str
    altura: str
    posicion: str
    teams: Optional[List[str]] = []
    
    
class Read_Team(SQLModel):
    posicion: int
    club: str
    partidos: int
    ganados: int
    empates: int
    perdidos: int
    goles: str
    diferencia: int
    puntos: int
    jugadores: int
    edad_media: str
    extranjeros: int
    internacionales: int
    estadio: str
    asientos: str
    balance: str
    players: Optional[List[str]] = []