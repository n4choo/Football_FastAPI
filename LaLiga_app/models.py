from turtle import position
from typing import List, Optional

from sqlmodel import Field, Relationship, SQLModel


class PlayerTeamLink(SQLModel, table=True):
    team_id: Optional[int] = Field(
        default=None, foreign_key="team.id", primary_key=True
    )
    player_id: Optional[int] = Field(
        default=None, foreign_key="player.id", primary_key=True
    )
    
    temporada: Optional[str]
    competicion: Optional[str] 
    club: Optional[str]
    partidos: Optional[str]
    equipo: Optional[str]
    partidos_equipo: Optional[str] 
    partidos_jugados: Optional[str]	
    goles: Optional[str]
    asistencias: Optional[str]
    goles_en_propia: Optional[str]
    entradas_desde_banquillo: Optional[str]	
    sustituciones: Optional[str]	
    amarillas: Optional[str]
    dobles_amarillas: Optional[str]	
    rojas: Optional[str]
    penaltis_Anotados: Optional[str]	
    minutos_por_gol: Optional[str]	
    minutos_jugados: Optional[str]	
    nombre_jugador: Optional[str]
    partidos_imbatido: Optional[str]
    goles_en_contra: Optional[str]
    
    team: "Team" = Relationship(back_populates="player_links")
    player: "Player" = Relationship(back_populates="team_links")

class Team(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
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
    
    player_links: List[PlayerTeamLink] = Relationship(back_populates="team")


class Player(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    nombre: str = Field(index=True)
    birthdate: str
    altura: str
    posicion: str
    
    team_links: List[PlayerTeamLink] = Relationship(back_populates="player")