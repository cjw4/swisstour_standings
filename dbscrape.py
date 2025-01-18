import requests
from bs4 import BeautifulSoup
from termcolor import colored
import pandas as pd
import datetime 

# helper functions
def parse_info(metadata_soup,class_name:str,name:str,var_type:type=str) -> str:
    """
    Parse the metadata for tournaments and players.
    """
    html = metadata_soup.find(class_=class_name)
    if html:
        data = html.text.split(':')[1][1:]
    else:
        if var_type == str:
            data = 'none'
        elif var_type == int:
            data = 0
        print(name + ' has no ' + class_name + ' listed.')
    return data

def location_parts(location:str) -> str:
    """
    Extract the parts of a location: city, state, and country.
    """
    location_separated = location.split(',')
    city = location_separated[0]
    if len(location_separated) > 2:
        state = location_separated[1][1:]           
    else:
        state = ''
    country = location_separated[-1][1:]
    return city,state,country 

def convert_date(date:str):
    """
    Turn the date string into a python datetime object.
    """
    start_date = date.split()[0]
    end_date = date.split()[-1]
    if start_date==end_date:
        days = 1
        start_date = datetime.datetime.strptime(end_date,'%d-%b-%Y')
    else:
        end_date = datetime.datetime.strptime(end_date,'%d-%b-%Y')
        try:
            # test the case where the tournament spans across two years
            start_date = datetime.datetime.strptime(start_date,'%d-%b-%Y')
        except:
            # normal case that both start and end happen in the same year
            start_date = start_date + '-' + str(end_date.year)
            start_date = datetime.datetime.strptime(start_date,'%d-%b-%Y')
        days = (end_date - start_date).days+1
    return start_date, days

def separate_status(string:str):
    """
    Split a string into status and expiry date.
    """
    status = string.split()[0]
    date_string = string.split()[-1][:-1]
    try:
        date = datetime.datetime.strptime(date_string,'%d-%b-%Y')
    except:
        date = '2099-01-01T00:00:00'
    return status, date

# main functions
def pdga_event(event_number:int,event_only:bool = False) -> pd.core.frame.DataFrame:
    """
    Scrapes the event metadata from the the pdga website, given the event number.
    Returns a dictionary of event metadata and a pandas dataframe of tournaments.
    """
    print(colored('Scraping event {} from pdga website.'.format(str(event_number)),'red'))
    # load the html of the event
    web_address = 'https://www.pdga.com/tour/event/' + str(event_number)
    page = requests.get(web_address)
    soup = BeautifulSoup(page.content, 'html.parser')

    # parse the html for the event metadata and save to dictionary 
    event_data = {}
    event_data['name'] = soup.title.text.split('|')[0][:-1]
    tier = soup.find(class_='pane-tournament-event-info').find(class_='pane-content').find('h4').text
    event_data['tier'] = tier
    tournament_metadata = soup.find(class_='event-info')
    date = parse_info(tournament_metadata,'tournament-date',event_data['name'])
    event_data['date'],event_data['days'] = convert_date(date)
    city,state,country = location_parts(parse_info(tournament_metadata,'tournament-location',event_data['name']))
    event_data['city'] = city
    event_data['state'] = state
    event_data['country'] = country
    event_data['director'] = parse_info(tournament_metadata,'tournament-director',event_data['name'])
    event_data['website'] = parse_info(tournament_metadata,'tournament-website',event_data['name'])

    status_metadata = soup.find(class_='summary').find(class_='odd')
    try:
        event_data['players'] = int(status_metadata.find(class_='players').text)
    except:
        event_data['players'] = 0
        print(event_data['Name'] + ' has not listed number of players.')
    try:
        event_data['purse'] = float(status_metadata.find(class_='purse').text.replace('$','').replace(',',''))
    except:
        event_data['purse'] = float(0)
        print(event_data['name'] + ' has no purse.')

    if not event_only:
        # parse the html for the tournaments, the results tables for each division are in a div containers with class 'table-container'
        results = soup.find(class_='leaderboard')
        # organize the tournaments into a list of dictionaries
        all_tournaments = []
        # parse through all divisions (categories)
        categories = results.find_all('details')
        idx = 0
        finished = False
        while not finished:
            try:
                category = categories[idx]
                idx += 1
                # extract the division
                division = category.find(class_='division').text.split()[0]
                # the table is broken into two classes for odd and even placement
                tournaments_odd = category.find_all(class_='odd')
                tournaments_even = category.find_all(class_='even')
                # combine the two lists for full results
                tournaments = [None]*(len(tournaments_odd)+len(tournaments_even))
                tournaments[::2] = tournaments_odd
                tournaments[1::2] = tournaments_even
                for tournament in tournaments:
                    tournament_dict = {}
                    # player
                    name = tournament.find(class_='player').text
                    tournament_dict['name'] = name
                    try:
                        pdga_number = int(tournament.find(class_='pdga-number').text)
                    except:
                        pdga_number = 0
                    tournament_dict['pdga_number'] = pdga_number
                    # division
                    tournament_dict['division'] = division
                    # total
                    try:
                        total_score = int(tournament.find(class_='total').text)
                    except:
                        total_score = 999
                    tournament_dict['total'] = total_score
                    # place
                    place = int(tournament.find(class_='place').text)
                    tournament_dict['place'] = place
                    # player rating
                    try:
                        player_rating = int(tournament.find(class_='player-rating').text)
                    except:
                        player_rating = 0
                    tournament_dict['rating'] = player_rating
                    # propagator
                    if tournament.find(class_='propagator'):
                        tournament_propagator = True
                    else:
                        tournament_propagator = False
                    tournament_dict['propagator'] = tournament_propagator
                    # rounds
                    found_rounds = tournament.find_all(class_='round')
                    rounds = []
                    for round in found_rounds:
                        rounds.append(round.text)
                    tournament_dict['rounds'] = rounds
                    # round ratings
                    found_ratings = tournament.find_all(class_='round-rating')
                    ratings = []
                    for rating in found_ratings:
                        ratings.append(rating.text)
                    tournament_dict['ratings'] = ratings   
                    try:
                        prize = float(tournament.find(class_='prize').text.replace('$','').replace(',',''))
                    except:
                        prize = 0
                    tournament_dict['prize'] = prize
                    # append player and round information to leaderboard
                    all_tournaments.append(tournament_dict)
            except:
                finished = True

        # create a dataframe
        tournaments_df = pd.DataFrame(all_tournaments)
    else:
        tournaments_df = pd.DataFrame()
    return event_data, tournaments_df

def pdga_player(pdga_number:int) -> dict:
    """
    Scrapes the pdga player's data, given the players pdga number.
    """
    print(colored('Scraping player info from player ({}) at pdga website.'.format(pdga_number),'red'))
    web_address = 'https://www.pdga.com/player/' + str(pdga_number) + '/details'
    page = requests.get(web_address)
    soup = BeautifulSoup(page.content, 'html.parser')

    # parse the player metadata
    player_data = {}
    try:
        title = soup.find(class_='pane-page-title').text.split('#')
    except:
        title = soup.find(class_='page-title').text.split('#')
    player_data['name'] = title[0].strip()    
    player_data['firstname'] = title[0].strip().split(' ')[0]
    player_data['lastname'] = title[0].strip().split(' ')[-1]
    player_data['pdga_number'] = title[1].strip()
    player_metadata = soup.find(class_='player-info')
    location = player_metadata.find('a',href=True).text
    city,state,country=location_parts(location)
    player_data['city'] = city
    player_data['state'] = state
    player_data['country'] = country
    player_data['classification'] = parse_info(player_metadata,'classification',player_data['name'])
    player_data['member_since'] = datetime.datetime.strptime(parse_info(player_metadata,'join-date',player_data['name']),'%Y')
    membership_status = parse_info(player_metadata,'membership-status',player_data['name'])
    status, date = separate_status(membership_status)
    player_data['membership_status'] = status
    player_data['membership_expiry'] = date
    official_status = parse_info(player_metadata,'official',player_data['name'])
    try:
        status, date = separate_status(official_status)
    except:
        status = ''
        date = datetime.datetime(1900,1,1)
    player_data['official_status'] = status
    player_data['official_expiry'] = date
    try:
        player_data['current_rating'] = int(parse_info(player_metadata,'current-rating',player_data['name']).split()[0])
    except:
        player_data['current_rating'] = 0
    player_data['career_events'] = int(parse_info(player_metadata,'career-events',player_data['name'],var_type=int))
    player_data['career_wins'] = int(parse_info(player_metadata,'career-wins',player_data['name'],var_type=int))
    try:
        player_data['career_earnings'] = float(parse_info(player_metadata,'career-earnings',player_data['name']).replace('$','').replace(',',''))
    except:
        player_data['career_earnings'] = float(0)

    return player_data