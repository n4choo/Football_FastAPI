from typing import List

from fastapi import Depends, FastAPI, HTTPException, Query
from .database import create_db_and_tables, engine
from .crud import get_session, insert_player_stats, insert_team_player_tables
from sqlmodel import Field, Session, SQLModel, create_engine, select
from .models import Player, PlayerTeamLink, Team
from .schemas import Read_Player, Read_Team

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36',
}




app = FastAPI()

@app.on_event("startup")
def on_startup():
    create_db_and_tables()
    print('created db and tables')
    insert_team_player_tables()
    

@app.get("/")
def hello():
    return {"Hello to this FastAPI project"}


@app.get("/players/")
def read_players(session:Session = Depends(get_session)):
    players = session.exec(select(Player)).all()
    return players

@app.get("/players/{player_id}", response_model=Read_Player)
def read_players_by_id(*, session:Session = Depends(get_session), player_id:int):
    player = session.get(Player, player_id)
    player = Read_Player(**dict(player))
    tpls = session.exec(select(PlayerTeamLink).where(PlayerTeamLink.player_id==player_id))
    for tpl in tpls:
        player.teams.append(tpl.club)
    if not player:
        raise HTTPException(status_code=404, detail="Player not found")
    return player


@app.get("/teams/")
def read_teams(session:Session = Depends(get_session)):
    teams = session.exec(select(Team)).all()
    return teams


@app.get("/teams/{team_id}", response_model=Read_Team)
def read_teams_by_id(*, session:Session = Depends(get_session), team_id:int):
    team = session.get(Team, team_id)
    team = Read_Team(**dict(team))
    tpls = session.exec(select(PlayerTeamLink).where(PlayerTeamLink.team_id==team_id))
    for tpl in tpls:
        team.players.append(tpl.nombre_jugador)
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    return team

@app.get("/stats/")
def read_stats(*, session:Session = Depends(get_session)):
    stats = session.exec(select(PlayerTeamLink)).all()
    if not stats:
        raise HTTPException(status_code=404, detail="Stats not found")
    return stats


'''
@app.get("/heroes/{hero_id}", response_model=HeroRead)
def read_hero(*, session: Session = Depends(get_session), hero_id: int):
    hero = session.get(Hero, hero_id)
    if not hero:
        raise HTTPException(status_code=404, detail="Hero not found")
    return hero


@app.patch("/heroes/{hero_id}", response_model=HeroRead)
def update_hero(
    *, session: Session = Depends(get_session), hero_id: int, hero: HeroUpdate
):
    db_hero = session.get(Hero, hero_id)
    if not db_hero:
        raise HTTPException(status_code=404, detail="Hero not found")
    hero_data = hero.dict(exclude_unset=True)
    for key, value in hero_data.items():
        setattr(db_hero, key, value)
    session.add(db_hero)
    session.commit()
    session.refresh(db_hero)
    return db_hero


@app.delete("/heroes/{hero_id}")
def delete_hero(*, session: Session = Depends(get_session), hero_id: int):

    hero = session.get(Hero, hero_id)
    if not hero:
        raise HTTPException(status_code=404, detail="Hero not found")
    session.delete(hero)
    session.commit()
    return {"ok": True}

'''

