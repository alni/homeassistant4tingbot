# -*- coding: utf-8 -*-
import tingbot
from tingbot import *
from requests import get,post
import json
    
# setup code here

# Please: Create a copy of "user_prefs.example.json" with the name of
# "user_prefs.json" with user preferences
with open('user_prefs.json') as f:
    user_prefs = json.load(f)
    
# Important: Create a copy of "secrets.example.json" with the name of
# "secrets.json" and provide a valid access token within that file
with open('secrets.json') as f:
    secrets = json.load(f)

climate_entity_id = user_prefs['climate_entity_id']
base_url = user_prefs['server_address'] + '/api/'
#'http://192.168.0.60:8123/api/'
headers = {
    'Authorization': 'Bearer ' + secrets['access_token'],
    'content-type': 'application/json',
}

temp = 0.0
temp_increment_by = 0.5
if 'climate_temp_increment_by' in user_prefs:
    temp_increment_by = user_prefs['climate_temp_increment_by']

climate_temp = 0.0
climate_state = ''
climate_operation_mode = ''

#response = get(url, headers=headers)
#print(response.text)
#j = json.loads(response.text)
#temp = j['attributes']['Temperature']


# TODO: Add "api_get()" wrapper function
# TODO: Add "api_post()" wrapper function

def get_entity_states(entity_id):
    url = base_url + 'states/' + entity_id
    response = get(url, headers=headers)
    print("\n")
    print(response.text)
    print("\n")
    j = json.loads(response.text)
    return j
    
def post_service_action(service_domain, service_type, data):
    url = base_url + 'services/' + service_domain + '/' + service_type
    response = post(url, headers=headers, data=json.dumps(data))
    j = json.loads(response.text)
    return j

def get_curr_temp(entity_id):
    j = get_entity_states(entity_id)
    temp = j['attributes']['Temperature']
    return temp
    

def get_climate_temp(entity_id):
    j = get_entity_states(entity_id)
    temp = j['attributes']['temperature']
    return temp
    
def get_climate_states(entity_id):
    global temp, climate_temp, climate_state, climate_operation_mode
    j = get_entity_states(entity_id)
    climate_temp = j['attributes']['temperature']
    if 'current_temperature' in j['attributes']:
        temp = j['attributes']['current_temperature']
    climate_operation_mode = j['attributes']['operation_mode']
    climate_state = j['state']
    
def increment_climate_temp(increment):
    global climate_temp
    entity_id = climate_entity_id
    curr_climate_temp = get_climate_temp(entity_id)
    curr_climate_temp += increment
    data = {'entity_id':entity_id, 'temperature': curr_climate_temp}
    post_service_action('climate', 'set_temperature', data)
    get_climate_states(entity_id)
    

@right_button.press
def inc_climate_temp():
    increment_climate_temp(+temp_increment_by)

@midright_button.press
def dec_climate_temp():
    increment_climate_temp(-temp_increment_by)
    
    
get_climate_states(climate_entity_id)

icon = u'\uF716' # snowflake (for cooling/AC)
color_active = 'aqua' # for cooling/AC
color_idle = 'gray'
print(climate_operation_mode)
if climate_operation_mode == 'heat':
    icon = u'\uF238'
    color_active = 'orange'

@every(seconds=30)
def loop():
    get_climate_states(climate_entity_id)
    


@every(seconds=5)
def loop2():
    # drawing code here
    screen.fill(color='black')
    # screen.text('Hello world!')
    screen.text(str(temp) + ' (' + str(climate_temp) + ' ; ' + climate_state + ')')
    color = 'gray'
    if climate_state == 'idle':
        color = color_idle
    else:
        color = color_active
        
    screen.text(icon, xy=(20, 20),color=color, font='materialdesignicons-webfont.ttf')
        

state = {
    'previous_xy': None
}

screen.fill(color='black')

# TODO: Use Mid Left Button for something else than clearing the screen
@midleft_button.hold
def clear_screen():
    screen.fill(color='black')

# TODO: Use Touch screen for something useful other than just drawing 
@touch()
def on_touch(xy, action):
    if state['previous_xy']:
        screen.line(
            state['previous_xy'],
            xy,
            width=5,
            color='blue')

    if action == 'up':
        state['previous_xy'] = None
    else:
        state['previous_xy'] = xy


tingbot.run()
