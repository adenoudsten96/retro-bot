from dataclasses import dataclass
from datetime import datetime
from dateutil import tz
from typing import List, Tuple
import requests
import csv
import math
import json
import arrow

# Define dataclasses
# This class corresponds to Droptimizer (DPS) rows
@dataclass
class SimRow:
    boss: str
    item: str
    slot: str
    dps_diff: int

# Class to pass to Google Sheets
@dataclass
class SimResult:
    player: str
    sim_date: datetime
    raidbots_url: str
    results: List[SimRow]

# Load WoW bosses and items using a file
# TODO: get dynamically from raidbots, using caching
sanctum_j = open('instances.json')
sanctum = json.load(sanctum_j)
sanctum_j.close()
items_j = open('equippable-items.json', encoding='utf8')
items = json.load(items_j)
items_j.close()

def boss_lookup(id) -> str:
    '''
    This function looks up a boss name by ID

    Returns: a string with the boss name
    '''
    for i in sanctum[14]['encounters']:
        if i['id'] == id:
            return i['name']

def item_lookup(id) -> str:
    '''
    This function looks up an item name by ID

    Returns: a string with the item name
    '''
    for i in items:
        if i['id'] == id:
            return i['name']

def get_droptimizer_csv(raidbots_url) -> csv.reader:
    '''
    This functions downloads the CSV file from a Droptimizer link
    '''
    raidbots_csv: str = requests.get(raidbots_url + '/data.csv').content.decode('utf8')
    raidbots_csv: List = raidbots_csv.splitlines()
    reader = csv.reader(raidbots_csv, delimiter=',')
    return reader

def generate_droptimizer_rows(raidbots_csv) -> List[SimRow]:
    '''
    This functions generates the Raidbots Droptimizer rows from a Raidbots CSV file

    Returns: a list of Droptimizer rows
    '''
    line_count: int = 0
    droptimizer_rows: List[SimRow] = []
    for row in raidbots_csv:
        
        # Get the BASE DPS from the second row of the CSV 
        if line_count == 1:
            base_dps: str = row[1]
        
        # Start generating droptimizer rows, from the third row onward
        if line_count >= 2:

            # Assign the relevant variables from the row positions
            dps_mean:  str = row[1]
            boss_name: str = boss_lookup(int(row[0].split("/")[1]))
            item_name: str = item_lookup(int(row[0].split("/")[3]))
            item_slot: str = row[0].split("/")[5]

            # Calculate the DPS difference by subtracting the MEAN DPS from the BASE DPS, and round the number up
            dps_diff = math.ceil((float(dps_mean) - float(base_dps)))

            # If the dps difference is negative the item is a downgrade and we can ignore it
            if dps_diff <= 0:
                continue

            # Add this row to the results
            sr = SimRow(item=item_name, dps_diff=dps_diff, boss=boss_name, slot=item_slot)
            droptimizer_rows.append(sr)
        
        # Increment line count
        line_count += 1
    
    # Sort the results by DPS difference, descending
    droptimizer_rows.sort(key=lambda x: x.dps_diff, reverse=True)
    return droptimizer_rows

def get_droptimizer_metadata(raidbots_url: str) -> Tuple:
    '''
    This function gets the time and player name and from the Droptimizer result
    '''
    raidbots_json = requests.get(raidbots_url + '/data.json').json()
    sim_date: str = raidbots_json['simbot']['date']
    sim_player: str = raidbots_json['simbot']['player']
    sim_date = arrow.get(float(sim_date)).format()
    return (sim_date, sim_player)

def main():

    # Raidbots URL, get this from Retro bot
    raidbots_url: str = "https://www.raidbots.com/reports/rrBWGcCKc6zPq69jKvdtJU"

    # Get the droptimizer csv and rows
    dr_csv: csv.reader = get_droptimizer_csv(raidbots_url=raidbots_url)
    dr_rows: List[SimRow] = generate_droptimizer_rows(raidbots_csv=dr_csv)

    # Get the sim info
    sim_info: Tuple = get_droptimizer_metadata(raidbots_url=raidbots_url)

    # Create the SimResult object to pass to Google Sheets
    sim_result: SimResult = SimResult(player=sim_info[1], sim_date=sim_info[0], raidbots_url=raidbots_url, results=dr_rows)

    print('Player:', sim_result.player.capitalize())
    print('Droptimizer date:', sim_result.sim_date)
    print('Raidbots URL:', sim_result.raidbots_url)
    print('Results:', sim_result.results)

main()