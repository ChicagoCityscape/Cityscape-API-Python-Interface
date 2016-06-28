import requests
import json
import csv

address_list = 'sample.csv'

def get_address_json_from_row(params):
    # params = {k: '"{}"'.format(v) for k,v in row.iteritems()} #api requires double quotes to avoid null responses
    j = json.loads(json.dumps(row))
    address = j['address']
    city = j['city']
    state = j['state']
    params = {"state":state, "city": city, "address": address }
    response = requests.post('http://tod.chicagocityscape.com/tod/index.php?address=' + address + '&city=' + city + '&state=' + state)
    print response.url
    return response.json()

def get_exact_match(potential_matches, address):
    for match in potential_matches:
        if match['address'] == address:
            return match
    return False

def get_closest_match(potential_matches):
    def get_centroid(x):
        return float(x['distance_to_centroid'])
    return min(potential_matches, key=get_centroid)
    # returns the closest whatever

with open(address_list, 'rb') as f:
    in_csv1 = csv.DictReader(f)
    for row in in_csv1:
        r = get_address_json_from_row(row)
        intersecting_parcels = r['properties']['parcels_intersecting']
        address = row['address']
        print intersecting_parcels[0]['pin']
		
        # exact_match = get_exact_match(intersecting_parcels, address)
        # exact_match = False
        #if exact_match:
        #    print exact_match
        #else:
        #    print get_closest_match(intersecting_parcels)