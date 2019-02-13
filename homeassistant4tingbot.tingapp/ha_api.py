from requests import get,post
import json
from config import (
    base_url,
    headers
)

# "api_get()" wrapper function
def api_get(path):
    # Calls the API to GET data from a path
    url = base_url + path
    response = get(url, headers=headers)
    print("\n")
    print(response.text)
    print("\n")
    j = json.loads(response.text)
    return j

# "api_post()" wrapper function
def api_post(path, data):
    # Calls the API to POST provided data to a path
    url = base_url + path
    response = post(url, headers=headers, data=json.dumps(data))
    j = json.loads(response.text)
    return j

def get_entity_states(entity_id):
    # Calls the API to get a device state information
    return api_get('states/' + entity_id)
    
def post_service_action(service_domain, service_type, data):
    # Calls the API to POST a service action with the provided data
    path = 'services/' + service_domain + '/' + service_type
    return api_post(path, data)

def get_curr_temp(entity_id):
    # Calls the API to get a thermometer sensor temperature from the
    # state information
    j = get_entity_states(entity_id)
    temp = j['attributes']['Temperature']
    return temp
    

def get_climate_temp(entity_id):
    # Call the API to get a climate thermostat temperature from the
    # state information
    j = get_entity_states(entity_id)
    temp = j['attributes']['temperature']
    return temp
    