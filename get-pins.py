import requests
import json
import csv
import pandas as pd

address_list = 'sample_using_query.csv'
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
    return {"response": response.json(), "url": url, "requested_address": params['address']}

def get_query_json_from_row(params):
    """establishes the parameters for the api calls. this one just sends the query """
    params = {k: '{}'.format(v) for k,v in row.iteritems()} #api requires double quotes to avoid null responses
    j = json.loads(json.dumps(row))
    print params
    response = requests.post('http://tod.chicagocityscape.com/tod/index.php?query=' + str(params['query']))
    url = response.url
    return {"response": response.json(), "url": url, "requested_address": params['query'], "id": params['id']}

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

    for idx, row in enumerate(in_csv1): #parse each row into an api call, return only the intersecting parcels, get the two closest, append these results to the master dataframe
        r = get_query_json_from_row(row)

        intersecting_parcels = r['response']['properties']['parcels_intersecting'], r['url'], r['id']
        print "requested is: ", r['requested_address']
        print "for row", idx, "prepped url is: " ,intersecting_parcels[1], 'unique id is:', intersecting_parcels[2]
        print "length of intersecting_parcels", len(intersecting_parcels[0])
        if intersecting_parcels[0]:
            print "intersecting_parcels not empty!"
            print r['response']['properties']['request']['city']
            print "number of intersecting_parcels matches", len(intersecting_parcels[0])
            two_closest = get_two_closest(intersecting_parcels[0])
            two_closest['url'] = intersecting_parcels[1]
            two_closest['city'] = r['response']['properties']['request']['city']
            two_closest['id'] = intersecting_parcels[2]
            two_closest['requested_address'] = r['requested_address']
            results = results.append(two_closest)
            #results['url'] = intersecting_parcels[1]
        else:
            print "intersecting_parcels is empty, print nulls for this row!"
            none = get_null_response(r['response']['properties']['request'])
            #swap address_columns
            none['requested_address'] = r['requested_address']
            print "null request addy" , none['requested_address']
            none['address'] = 'no_result'
            none['url'] = intersecting_parcels[1]
            two_closest['city'] = r['response']['properties']['request']['city']
            none['id'] = intersecting_parcels[2]
            results = results.append(none)

print results['city']
#pick specific columns, write to csv
results.rename(columns={'address': 'returned_address'}, inplace=True)
results[['id', 'requested_address', 'returned_address', 'city', 'pin', 'distance_to_centroid', 'distance_to_edge', 'url']].to_csv(output_path, index_label= 'closest_rank')
#results.to_csv(output_path, index_label= 'closest_rank')
