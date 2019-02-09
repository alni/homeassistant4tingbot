# -*- coding: utf-8 -*-
import tingbot
from tingbot import (
    app,
    screen,
    right_button,
    midright_button,
    midleft_button,
    left_button,
    touch,
    every
)
from requests import get,post
import json
    
# setup code here
icon_font = 'MaterialDesign-Webfont/fonts/materialdesignicons-webfont.ttf'

# Please: Create a copy of "default_settings.json" with the name of
# "settings.json" (or "local_settings.json") containing user preferences
user_prefs = tingbot.app.settings
    
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
temp_increment_by = 0.5 # Default climate temperature increment rate
if 'climate_temp_increment_by' in user_prefs:
    # If a (optional) climate temperature increment rate is provided,
    # then use it instead of the default value
    temp_increment_by = user_prefs['climate_temp_increment_by']

# Initialize global variables
climate_temp = 0.0
climate_state = ''
climate_operation_mode = ''
climate_operation_list = []

#response = get(url, headers=headers)
#print(response.text)
#j = json.loads(response.text)
#temp = j['attributes']['Temperature']


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
    
def get_climate_states(entity_id):
    # Call the API to get a climate thermostat state information
    global temp, climate_temp, climate_state, climate_operation_mode, climate_operation_list
    j = get_entity_states(entity_id)
    climate_temp = j['attributes']['temperature']
    if 'current_temperature' in j['attributes']:
        temp = j['attributes']['current_temperature']
    climate_operation_mode = j['attributes']['operation_mode']
    climate_operation_list = j['attributes']['operation_list']
    climate_state = j['state']
    
def increment_climate_temp(increment):
    # Increment (+/-) the wanted temperature of the thermostat device
    global climate_temp
    entity_id = climate_entity_id
    curr_climate_temp = get_climate_temp(entity_id)
    curr_climate_temp += increment
    data = {'entity_id':entity_id, 'temperature': curr_climate_temp}
    post_service_action('climate', 'set_temperature', data)
    get_climate_states(entity_id)
    

@right_button.press
@touch(xy=(300, 20), size=(64,64), align='topright')
def inc_climate_temp(xy=None, action=None):
    # Increase the wanted temperature of the thermostat device
    if action == None or action == 'up':
        increment_climate_temp(+temp_increment_by)

        # Update UI straight away without waiting for next "every" call
        loop2()

@midright_button.press
@touch(xy=(230, 20), size=(64,64), align='topright')
def dec_climate_temp(xy=None, action=None):
    # Decrease the wanted temperature of the thermostat device
    if action == None or action == 'up':
        increment_climate_temp(-temp_increment_by)

        # Update UI straight away without waiting for next "every" call
        loop2()

@left_button.hold
def climate_turn_off():
    # Turn off the thermostat device
    data = {'entity_id':climate_entity_id}
    post_service_action('climate', 'turn_off', data)
    get_climate_states(climate_entity_id)

    # Update UI straight away without waiting for next "every" call
    loop2()

@left_button.press
def climate_turn_on():
    # Turn on the thermostat device
    data = {'entity_id':climate_entity_id}
    post_service_action('climate', 'turn_on', data)
    get_climate_states(climate_entity_id)

    # Update UI straight away without waiting for next "every" call
    loop2()
    

# Call the API to initialize the thermostat state information
get_climate_states(climate_entity_id)

# Setup the thermostat state icon
icon = u'\uF716' # snowflake (for cooling/AC)
color_active = 'aqua' # active/on color (for cooling/AC)
color_idle = 'gray' # inactive/idle/off color
print(climate_operation_mode)
if 'heat' in climate_operation_list:
    icon = u'\uF238' # fire (for heating)
    color_active = 'orange' # active/on color (for heating)

@every(seconds=30)
def loop():
    get_climate_states(climate_entity_id)
    
@every(seconds=1)
def loop2():
    # drawing code here
    screen.fill(color='black') # Use a black background
    # screen.text('Hello world!')

    # Draw the on-screen buttons
    # "plus-box-outline" (Increase the thermostat temperature)
    screen.text(u'\uF703', xy=(300, 20), align='topright', font_size=64, font=icon_font)
    # "minus-box-outline" (Decrease the thermostat temperature)
    screen.text(u'\uF6F1', xy=(230, 20), align='topright', font_size=64, font=icon_font)
 
    # Draw the info text in the center of the screen in the format of:
    # "[current temp] ([thermostat wanted temp] ; [thermostat state])"
    screen.text('{0} ({1} ; {2})'.format(temp, climate_temp, climate_state))

    # Prepare the thermostat state icon
    color = 'gray' # Initialize color as gray
    if climate_state == 'idle' or climate_state == 'off':
        # If the climate is idle or off, set the icon as inactive (idle
        # color)
        color = color_idle
    else:
        # Otherwise set the icon as active/on
        color = color_active
    
    # Draw the thermostat state icon
    screen.text(icon, xy=(20, 20),color=color, font=icon_font)
        

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
