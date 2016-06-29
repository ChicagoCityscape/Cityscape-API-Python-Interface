import requests
import json
import csv
import pandas as pd

address_list = 'sample.csv'
output_path = 'output.csv'

"""establishes the parameters for the api calls. atm they are decalred individually becuase the api needs them in a certain order.
this code can be compressed to sort the dict directly """

def get_address_json_from_row(params):
    # params = {k: '"{}"'.format(v) for k,v in row.iteritems()} #api requires double quotes to avoid null responses
    j = json.loads(json.dumps(row))
    address = j['address']
    city = j['city']
    state = j['state']
    params = {"state":state, "city": city, "address": address }
    response = requests.post('http://tod.chicagocityscape.com/tod/index.php?address=' + address + '&city=' + city + '&state=' + state)
    url = response.url
    return {"response": response.json(), "url": url}

"""currently un-used becuase string-matching is probably a bad idea here"""
def get_exact_match(potential_matches, address):
    for match in potential_matches:
        if match['address'] == address:
            return match
    return False

"""currently un-used, returns the closest centroid without using pandas"""

def get_closest_match(potential_matches):
    def get_centroid(x):
        return float(x['distance_to_centroid'])
    return min(potential_matches, key=get_centroid)
    # returns the closest whatever

"""uses pandas to return only the two entries with the smallest distance to centroid"""

def get_two_closest(potential_matches):
    two_closest = pd.DataFrame.from_dict(potential_matches, dtype=float).nsmallest(2, 'distance_to_centroid')
    return two_closest


#declare empy pandas df to store all results
results = pd.DataFrame()
#open the address lists and read the rows as dictionaries
with open(address_list, 'rb') as f:
    in_csv1 = csv.DictReader(f)
    for row in in_csv1: #parse each row into an api call, return only the intersecting parcels, get the two closest, append these results to the master dataframe
        r = get_address_json_from_row(row)
        #intersecting_parcels = r['response']['properties']['parcels_intersecting']
        intersecting_parcels = r['response']['properties']['parcels_intersecting'], r['url']
        two_closest = get_two_closest(intersecting_parcels[0])
        print r['url']
        results = results.append(two_closest)
        results['url'] = r['url']
#pick specific columns
results[['requested_address', 'address', 'pin', 'distance_to_centroid', 'distance_to_edge', 'url']].to_csv(output_path, index_label= 'closest_rank')
