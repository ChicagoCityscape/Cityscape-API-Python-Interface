import requests
import json
import csv
import pandas as pd

address_list = 'sample.csv'
output_path = 'output.csv'

list1 = pd.read_csv(address_list)

def get_address_json_from_row(params):
    """establishes the parameters for the api calls. atm they are decalred individually becuase the api needs them in a certain order.
    this code can be compressed to sort the dict directly """
    # params = {k: '"{}"'.format(v) for k,v in row.iteritems()} #api requires double quotes to avoid null responses
    j = json.loads(json.dumps(row))
    address = j['address']
    city = j['city']
    state = j['state']
    params = {"state":state, "city": city, "address": address }
    response = requests.post('http://tod.chicagocityscape.com/tod/index.php?address=' + address + '&city=' + city + '&state=' + state)
    url = response.url
    return {"response": response.json(), "url": url}


def get_exact_match(potential_matches, address):
    """currently un-used becuase string-matching is probably a bad idea here"""
    for match in potential_matches:
        if match['address'] == address:
            return match
    return False



def get_closest_match(potential_matches):
    """currently un-used, returns the closest centroid without using pandas"""
    def get_centroid(x):
        return float(x['distance_to_centroid'])
    return min(potential_matches, key=get_centroid)
    # returns the closest whatever

def get_two_closest(potential_matches):
    """uses pandas to return only the two entries with the smallest distance to centroid"""
    matches = pd.DataFrame.from_dict(potential_matches) #load in dict, data types as object
    if len(matches) > 1:
        two_closest = matches.where(matches.distance_to_centroid.astype(float).nsmallest(2)) # cast distance to float, sort by that, use it in a where clause
        two_closest = two_closest[two_closest.distance_to_centroid.notnull() == True] # remove the null entries (where keeps the shape of the original data)
    else:
        two_closest = matches.where(matches.distance_to_centroid.astype(float).nsmallest(1)) # cast distance to float, sort by that, use it in a where clause
        two_closest = two_closest[two_closest.distance_to_centroid.notnull() == True] # remove the null entries (where keeps the shape of the original data)
    return two_closest

def get_null_response(potential_matches):
    matches = pd.DataFrame.from_records(potential_matches, index=['no_result'])
    null_response = matches
    return null_response

results = pd.DataFrame()
#open the address lists and read the rows as dictionaries
with open(address_list, 'rb') as f:
    in_csv1 = csv.DictReader(f)

    for row in in_csv1: #parse each row into an api call, return only the intersecting parcels, get the two closest, append these results to the master dataframe
        r = get_address_json_from_row(row)
        print len(r)
        urls = []
        #intersecting_parcels = r['response']['properties']['parcels_intersecting']
        intersecting_parcels = r['response']['properties']['parcels_intersecting'], r['url']
        
        urls.append(intersecting_parcels[1])
        print urls
        if intersecting_parcels[0] != None:
            print intersecting_parcels[0] != None
            print len(intersecting_parcels[0])
            two_closest = get_two_closest(intersecting_parcels[0])
            results = results.append(two_closest)
            results['url'] = intersecting_parcels[1]

        elif intersecting_parcels[0] == None:
            none = get_null_response(r['response']['properties']['request'])
            results = results.append(none)
            results['url'] = intersecting_parcels[1]

            #nulldict = {}
            #for i in results.columns:
            #    nulldict[i] = "no_results"
            #results = results.append(nulldict, ignore_index= True)
            #null.add(nulldict, axis='columns', level=None, fill_value= "no_results")
#pick specific columns
results[['requested_address', 'address', 'pin', 'distance_to_centroid', 'distance_to_edge', 'url']].to_csv(output_path, index_label= 'closest_rank')
#results.to_csv(output_path, index_label= 'closest_rank')
