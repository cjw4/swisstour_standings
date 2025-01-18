from sqlalchemy import create_engine, NullPool, and_, MetaData, Table, Column, Integer, String
from sqlalchemy.orm import sessionmaker, declarative_base
from dbconn import DB_URL
from dbobjects import Event, Player, Tournament
from dbscrape import pdga_event, pdga_player
import requests
import pandas as pd
import io
import numpy as np

# helper functions
def add_event(event_id:int):
    """
    Add an event to the database given the pdga number as event_id.
    Return the event data as a dictionary and the tournament data as a dataframe.
    """
    # create a connection to the database
    engine=create_engine(DB_URL,poolclass=NullPool)
    Session=sessionmaker(bind=engine)
    with Session() as session:
        # check to see if event is already in the databases
        db_events = session.query(Event).all()
        db_event_ids = [n.event_id for n in db_events]
        
        if event_id not in db_event_ids:
            event_data, tournament_df = pdga_event(event_id,event_only=False)
            new_event = Event(
                event_id=event_id,
                event_name=event_data['name'],
                event_tier=event_data['tier'],
                event_date=event_data['date'],
                event_days=event_data['days'],
                event_city=event_data['city'],
                event_state=event_data['state'],
                event_country=event_data['country'],
                event_no_players=event_data['players'],
                event_purse=event_data['purse'] 
            )
            session.add(new_event)
            session.commit()
        else:
            event_data = None
            tournament_df = None
            print('Event {} is already in the database.'.format(str(event_id)))

    return event_data, tournament_df

def add_tournament(event_id:int,pdga_id:int,tournament_df=None,player_name=None):
    """
    Add a tournament to the database given the event_id and pdga number (or player's name) as pdga_id.
    """
    # create a connection to the database
    engine=create_engine(DB_URL,poolclass=NullPool)
    Session=sessionmaker(bind=engine)
    with Session() as session:
        # if the player has a pdga number, use that to get the player_id, otherwise use the player name
        if pdga_id:
            # get the player_id based on the pdga number
            player_id = session.query(Player).filter(Player.player_pdga_id == pdga_id).all()[0].player_id
        else:
            # get the player_id based on the player name
            player_id = session.query(Player).filter(and_(Player.player_firstname == player_name.split()[0], 
                Player.player_lastname == player_name.split()[1])).first().player_id
            
        # check to see if the tournament is already in the database
        db_tournaments = session.query(Tournament).all()
        db_tournament_ids = [[n.player_id,n.event_id] for n in db_tournaments]
        if [player_id,event_id] not in db_tournament_ids:    
            # filter the tournament information for the individual player
            if pdga_id:
                tournament = tournament_df[tournament_df.pdga_number == pdga_id]
            else:
                tournament = tournament_df[tournament_df.name == player_name]
            new_tournament = Tournament(
                player_id=player_id,
                event_id=event_id,
                tournament_division=tournament.division.values[0],
                tournament_score=int(tournament.total.values[0]),
                tournament_place=int(tournament.place.values[0]),
                tournament_rating=int(tournament.rating.values[0]),
                tournament_prize=int(tournament.prize.values[0]),
                tournament_propagator=int(tournament.propagator.values[0])
            )
            session.add(new_tournament)
            session.commit()
        else:
            print('Player {} already has a tournament for event {} in the database.'.format(str(player_id),str(event_id)))

def add_player(pdga_id:int):
    """
    Add a player to the database given the pdga number as pdga_id.
    """
    # create a connection to the database
    engine=create_engine(DB_URL,poolclass=NullPool)
    Session=sessionmaker(bind=engine)
    with Session() as session:
        # check to see if player is already in database
        db_players = session.query(Player).all()
        db_pdga_ids = [n.player_pdga_id for n in db_players]
        if pdga_id not in db_pdga_ids:
            player_data = pdga_player(pdga_id)
            if player_data:
                new_player = Player(
                    player_pdga_id=player_data['pdga_number'],
                    player_firstname=player_data['firstname'],
                    player_lastname=player_data['lastname'],
                    player_city=player_data['city'],
                    player_state=player_data['state'], 
                    player_country=player_data['country'],
                    player_classification=player_data['classification'],
                    player_pdga_since=player_data['member_since'],
                    player_pdga_status=player_data['membership_status'],
                    player_pdga_expiry=player_data['membership_expiry'],
                    player_official_status=player_data['official_status'],
                    player_official_expiry=player_data['official_expiry'],
                    player_rating=player_data['current_rating'],
                    player_no_events=player_data['career_events'],
                    player_no_wins=player_data['career_wins'],
                    player_earnings=player_data['career_earnings']
                )
                session.add(new_player)
                session.commit()
        else:
            print('Player {} is already in the database'.format(str(pdga_id)))
        session.close()

def add_non_pdga_player(name:str):

    """
    Add a non pdga player to the database given the player's name.
    """
    # create a connection to the database
    engine=create_engine(DB_URL,poolclass=NullPool)
    Session=sessionmaker(bind=engine)
    with Session() as session:
        # check to see if player is already in database
        db_players = session.query(Player).all()
        db_names = [(n.player_firstname + ' ' + n.player_lastname) for n in db_players]
        if name not in db_names:
            new_player = Player(
                player_firstname=name.split()[0],
                player_lastname=name.split()[1]
            )
            session.add(new_player)
            session.commit()
        else:
            print('Player {} is already in the database'.format(name))

# calc_pts depreciated due to other calculation system
def calc_pts(n:int,k:int,pts_max:int):
    '''
    Function to calculate number of points for place (k) with n players and max number of points.
    '''
    # calculate the regression factor
    r_f = 20 - 1.61*np.sqrt(n)

    # calculate the minimum points
    if n < 9:
        pts_min = np.round((35*(30**(1-(n-1)/8)))/(30**(1-1/8)),0)
    else:
        pts_min = 1

    # calculate the points
    c = (r_f**(1-(k-1)/(n))-1)/(r_f-1)
    if k == 1:
        pts = pts_max
    elif k == n:
        pts = pts_min
    else:
        pts = round(pts_min + c*(pts_max-pts_min),1)
    
    return pts

def create_points_df(division:str,max_pts_dict:dict):
    '''
    Function to extract a table of all players and their respective points.
    '''
    # create a connection to the database
    engine=create_engine(DB_URL,poolclass=NullPool)
    Session=sessionmaker(bind=engine)
    session=Session()

    # get all table that contains everybody with swisstour_license = True, 
    # include columns player_id, player_firstname, player_lastname, player_swisstour_license
    players_w_license = session.query(Player.player_id,
                            Player.player_firstname,
                            Player.player_lastname,
                            Player.player_sda_id,
                            Player.player_swisstour_license).filter(
                                Player.player_swisstour_license == True).all()
    # get all the event ids and names
    events = session.query(Event).join(Tournament, Event.event_id == Tournament.event_id).filter(Tournament.tournament_division == division).all()
    event_info = [(event.event_id,event.event_name) for event in events]
    event_info_dict = dict(event_info)

    session.close()

    list_of_dicts = []
    # for each player create a dictionary with results
    for player in players_w_license:
        # get all tournaments for the player
        tournaments = session.query(Tournament).filter(Tournament.player_id == player.player_id).all()
        # get all the points for the player
        points = [(tournament.event_id, tournament.tournament_swisstour_points) 
                  for tournament in tournaments if tournament.tournament_division == division]
        points_dict = dict(points)
        # create a dictionary with the player and points
        if points_dict:
            dict_ = {"player": player.player_firstname + ' ' + player.player_lastname,
                    "sda_license": player.player_sda_id
                    }
            dict_.update(points_dict)
            list_of_dicts.append(dict_)
    
    def sum_points(row, max_pts_dict:dict):
        events_100_list = []
        events_200_list = []
        events_250_list = []
        for key, value in max_pts_dict.items():
            if value == 100:
                events_100_list.append(key)
            elif value == 200:
                events_200_list.append(key)
            elif value == 250:
                events_250_list.append(key)

        events_100_pts = row[row.index.isin(events_100_list)].sort_values(ascending=False).iloc[:3].sum()
        events_100_incl = row[row.index.isin(events_100_list)].sort_values(ascending=False).iloc[:3].index
        events_200_pts = row[row.index.isin(events_200_list)].sort_values(ascending=False).iloc[:2].sum()
        events_200_incl = row[row.index.isin(events_200_list)].sort_values(ascending=False).iloc[:2].index
        events_250_pts = row[row.index.isin(events_250_list)].sort_values(ascending=False).iloc[:1].sum()
        events_250_incl = row[row.index.isin(events_250_list)].sort_values(ascending=False).iloc[:1].index
        pts = events_100_pts + events_200_pts + events_250_pts
        events_incl = events_100_incl.values.tolist() + events_200_incl.values.tolist() + events_250_incl.values.tolist()
        return pts, events_incl
    
    # create a pandas dataframe from the list of dictionaries
    df = pd.DataFrame(list_of_dicts)
    df[['Total', 'events_incl']] = df.apply(lambda row : pd.Series(sum_points(row, max_pts_dict)), axis=1)

    # create indicator columns
    events = [event.event_id for event in events]
    for event in events:
        df[f'{event}_indicator'] = df.apply(lambda row : event in row['events_incl'], axis=1)

    df.rename(columns={**event_info_dict, **{f'{event}_indicator': f'{event_info_dict[event]}_indicator' for event in events}}, inplace=True)
    df.drop(columns=['events_incl'], inplace=True)
    
    df['Place'] = df['Total'].rank(ascending=False,method='min').astype(int)
    df = df.sort_values(by='Place',ascending=True)
    cols = ['Place']  + [col for col in df if col != 'Place']
    df = df[cols]
    return df

# functions
def populate_db_by_event(event_id:int):
    """
    Populate the database with the event, player, and tournament information for a given event.
    """
    _, tournament_df = add_event(event_id)

    for _,tournament in tournament_df.iterrows():
        if tournament['pdga_number'] != 0:
            add_player(tournament.pdga_number)
            add_tournament(event_id,tournament.pdga_number,tournament_df)
        else:
            add_non_pdga_player(tournament['name'])
            add_tournament(event_id,tournament.pdga_number,tournament_df,player_name=tournament['name'])

def add_sda_info():
    """
    For each player in the database, add their SDA information from the
    SDA excel table if applicable.
    """
    # read the sda excel table
    url = 'https://docs.google.com/spreadsheets/d/1oRw8G3JxLCsm8LjYfpfz8UXCcbRrk0zy/export?format=xlsx&ouid=110597889716666012884&rtpof=true&sd=true'
    response = requests.get(url)
    if response.status_code == 200:
        try:
            file = io.BytesIO(response.content)
            df = pd.read_excel(file, engine='openpyxl')
        except:
            print(f'Error reading the excel file: {url}')
            return
    else:
        print(f'Error downloading the excel file: {response.status_code}')
        return    
    file = io.BytesIO(response.content)

    sda_info = pd.read_excel(file, engine='openpyxl')
    sda_info = sda_info.applymap(lambda x: x.strip() if isinstance(x, str) else x)
    sda_info['PDGA'] = sda_info['PDGA'].fillna(0).astype(int)
    sda_pdga_ids = sda_info['PDGA'].tolist()
    sda_names = [n.Vorname + ' ' + n.Name for _,n in sda_info.iterrows()]

    # create a connection to the database
    engine=create_engine(DB_URL,poolclass=NullPool)
    Session=sessionmaker(bind=engine)
    with Session() as session:
        # get all players from the database
        all_players = session.query(Player).all()
        for player in all_players:
            if (player.player_pdga_id != None) & (player.player_pdga_id in sda_pdga_ids): 
                sda_player = sda_info[sda_info.PDGA == player.player_pdga_id]
            elif (player.player_firstname + ' ' + player.player_lastname) in sda_names:
                sda_player = sda_info[sda_info.Vorname + ' ' + sda_info.Name == player.player_firstname + ' ' + player.player_lastname]
            else:
                player.player_swisstour_license = False
                player.player_sda_id = None
                print(f'No SDA info available for {player.player_firstname} {player.player_lastname}.')
                session.commit()
                continue
            try:
                if sda_player.CH_Lizenz.values[0].lower() == 'ja':
                    tour_license = True
                else:
                    tour_license = False
            except:
                tour_license = False
            player.player_sda_id = sda_player['SDA'].values[0]
            player.player_swisstour_license = tour_license
            session.commit()
            print(f'Added SDA info for player {player.player_firstname} {player.player_lastname}.')

def calculate_swisstour_pts(max_pts_dict:dict):
    """
    Calculate the swisstour points for each event in the database.
    """
    # create connection to the database
    engine=create_engine(DB_URL, poolclass=NullPool)
    Session=sessionmaker(bind=engine)
    with Session() as session:
        # get all events from the database
        events = session.query(Event).all()
        for event in events:
            # create dictionary for assigning points to place
            pts_dict = {
                1: 100, 2: 90, 3: 81, 4: 73, 5: 66,
                6: 60, 7: 55, 8: 50, 9: 46, 10: 42,
                11: 38, 12: 35, 13: 32, 14: 29, 15: 26,
                16: 23, 17: 21, 18: 19, 19: 17, 20: 15,
                21: 13, 22: 11, 23: 10, 24: 9, 25: 8,
                26: 7, 27: 6, 28: 5,
            }
            event_id = event.event_id
            max_pts = max_pts_dict[event_id]
            # adjust the points based on the max points
            pts_dict = {k: v*(max_pts/100) for k, v in pts_dict.items()}

            # get all tournaments from the database corresponding to the selected event  
            tournaments = session.query(Tournament).filter(Tournament.event_id == event_id).all()
    
            # get all the divisions for particular event
            divisions = sorted(list(set([tournament.tournament_division for tournament in tournaments])))
            for division in divisions:
                # get all the tournaments filtered by event_id and division
                tournaments = session.query(Tournament).filter(and_(Tournament.event_id == event_id,Tournament.tournament_division == division)).all()
                n = len(tournaments)
                for tournament in tournaments:
                    if tournament.tournament_place in pts_dict:
                        pts = pts_dict[tournament.tournament_place]
                    else:
                        pts = min(list(pts_dict.values()))
                    if tournament.tournament_score != 999 or tournament.tournament_score != 888:
                        tournament.tournament_swisstour_points = int(pts)
                    else:
                        tournament.tournament_swisstour_points = 0 # do not give points to DNF tournaments  
                    # write the points to the database
                    session.commit()
                    print(f'Added swisstour points for event {event_id} and player {tournament.player_id}.')

def create_standings(event_order_and_pts:dict):
    event_order = [key for key in event_order_and_pts]
    # create connection to the database
    engine=create_engine(DB_URL, poolclass=NullPool)
    Session=sessionmaker(bind=engine)
    with Session() as session:
        # Create a table of rankings for each division
        divisions = session.query(Tournament.tournament_division).distinct().all()
        for division in divisions:
            division = division[0]
        
            # Join Event and Tournament tables and filter by division
            event_info = session.query(Tournament.event_id, Event.event_name).join(
                Tournament, Event.event_id == Tournament.event_id).join(
                Player, Tournament.player_id == Player.player_id
                ).filter(
                    Tournament.tournament_division == division,
                    Player.player_swisstour_license == True
                    ).distinct().all()
            
            # Create a mapping dictionary
            event_mapping = {event_id: event_name for event_id, event_name in event_info}
                        
            # Reorder the event_ids based on event_order
            ordered_event_names = [event_mapping[event_id] for event_id in event_order if event_id in event_mapping]

            points_df = create_points_df(division, event_order_and_pts)
            # Reorder the columns of points_df based on ordered_event_names
            additional_columns = [col for col in points_df.columns if col not in ordered_event_names]
            points_df = points_df[additional_columns + ordered_event_names]
            points_df.rename(columns={'sda_license': 'SDA License'}, inplace=True)
            
            # Replace NaN with None
            points_df = points_df.replace({pd.NA: None, np.nan: None})

            # Round the points to 1 decimal place
            # points_df = points_df.round(1)

            # Drop the standings table if it exists
            metadata = MetaData()
            metadata.reflect(bind=engine)
            if f'standings_{division}' in metadata.tables:
                rankings_table = Table(f'standings_{division}', metadata, autoload_with=engine)
                rankings_table.drop(engine)
            
            # Create the standings table dynamically
            Base = declarative_base()
            
            # Create the standings table
            attributes = {
                '__tablename__': f'standings_{division}',
                'standing_id': Column(Integer(), primary_key=True)       
            }
                
            column_names = points_df.columns
            for column_name in column_names:                
                if (column_name == 'Place'):
                    attributes[column_name] = Column(Integer())
                else:
                    attributes[column_name] = Column(String(100))
                    
            # Create the class dynamically
            Standing = type(f'Standing_{division}', (Base,), attributes)
            
            # Create the table in the database
            Base.metadata.create_all(engine)

            # Populate the standings table
            for row in points_df.iterrows():
                row_dict = row[1].to_dict()

                # Change values to "DNF" if their value is 0 and the column name contains "indicator"
                for key, value in row_dict.items():
                    if (value == 0) and ('indicator' not in key):
                        row_dict[key] = "DNF"
                        
                points = Standing(**row_dict)
                session.add(points)
            session.commit()