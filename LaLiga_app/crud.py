from sqlmodel import Field, Session, SQLModel, create_engine, select
from .scrap import get_liga, get_player_stats, get_player_info
from .models import Player, Team, PlayerTeamLink
from .database import engine


def del_list_inplace(l, id_to_del):
    for i in sorted(id_to_del, reverse=True):
        del(l[i])
        
        
        
def get_session():
    with Session(engine) as session:
        yield session
        
        
def insert_player_stats(name:str, team_name:str ,session: Session):
    stats_df = get_player_stats(name)
    for row in stats_df.iterrows():
        d = dict(row[1])
        print(name)
        print(team_name)
        player = session.exec(select(Player).where(Player.nombre == name))
        team = session.exec(select(Team).where(Team.club == team_name))
        p = player.one()
        t = team.one()
        ptl = PlayerTeamLink( **d, player=p, team=t)
        print(f'trying to add {p.nombre}----{t.club} to the session')
        session.add(ptl)
        print(f'added {name}----{team_name} to the session')
    return 
    
def insert_team_player_tables():
    del_players = []
    with Session(engine) as session:
        team_info, players = get_liga()
        players_list = players['nombre']
        print('conseguidos el team info y los players')
        for team in team_info:
            t = Team(**team)
            print(f'trying to add {team["club"]} to the session')
            session.add(t)
            print(f'added {team["club"]} to the session')
    
        print('----------------------------TRYING TEAMS COMMIT----------------------------------------')
        session.commit()
        print('----------------------------TEAMS COMMIT DONE----------------------------------------')
    
    with Session(engine) as session:
        player_names = []
        for i in range(len(players['nombre'])):
            try:
                p = Player(**get_player_info(players_list[i]))
                player_names.append(p.nombre)
                #player_db = Player.from_orm(p)
                print(players['club'][i])
                print(f'trying to add {players_list[i]} to the session')
                session.add(p)
                print(f'added {players_list[i]} to the session')
                break
            except:
                print(f'----------Failed to add {players_list[i]} to the session------------')
                del_players.append(i)
                continue
        print('----------------------------TRYING PLAYERS COMMIT----------------------------------------')
        session.commit()
        print('----------------------------PLAYERS COMMIT DONE----------------------------------------')
    del_list_inplace(player_names,del_players)
        
    
    with Session(engine) as session:    
        for player in player_names: #Second for to insert the team - player - link
            insert_player_stats(player, players['club'][i], session)
        session.commit()
    print('-----------------------------Inserted Teams and players-----------------------------')



