# -*- coding: utf-8 -*-
import tingbot
from tingbot import (
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
import config
import ha_api
import mdi
    
# Initialize global variables
icon_font = mdi.icon_font

climate_entity_id = config.climate_entity_id

temp = 0.0
climate_temp = 0.0
climate_state = ''
climate_operation_mode = ''
climate_operation_list = []

climate_icon_heating = mdi.icon_defs['fire'] # fire (for heating)
climate_icon_ac = mdi.icon_defs['snowflake'] # snowflake (for cooling/AC)

# button defs
button_font_size = 64
button_touch_size = (button_font_size, button_font_size)

button_inc_text = mdi.icon_defs['plus-box-outline']
button_inc_xy = (300, 20)
button_inc_align = 'topright'
button_dec_text = mdi.icon_defs['minus-box-outline']
button_dec_xy = (230, 20)
button_dec_align = 'topright'

#response = get(url, headers=headers)
#print(response.text)
#j = json.loads(response.text)
#temp = j['attributes']['Temperature']
    
def get_climate_states(entity_id):
    # Call the API to get a climate thermostat state information
    global temp, climate_temp, climate_state, climate_operation_mode, climate_operation_list
    j = ha_api.get_entity_states(entity_id)
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
    curr_climate_temp = ha_api.get_climate_temp(entity_id)
    curr_climate_temp += increment
    data = {'entity_id':entity_id, 'temperature': curr_climate_temp}
    ha_api.post_service_action('climate', 'set_temperature', data)
    get_climate_states(entity_id)
    

@right_button.press
@touch(xy=button_inc_xy, size=button_touch_size, align=button_inc_align)
def inc_climate_temp(xy=None, action=None):
    # Increase the wanted temperature of the thermostat device
    if action == None or action == 'up':
        increment_climate_temp(+config.temp_increment_by)

        # Update UI straight away without waiting for next "every" call
        loop2()

@midright_button.press
@touch(xy=button_dec_xy, size=button_touch_size, align=button_dec_align)
def dec_climate_temp(xy=None, action=None):
    # Decrease the wanted temperature of the thermostat device
    if action == None or action == 'up':
        increment_climate_temp(-config.temp_increment_by)

        # Update UI straight away without waiting for next "every" call
        loop2()

@left_button.hold
def climate_turn_off():
    # Turn off the thermostat device
    data = {'entity_id':climate_entity_id}
    ha_api.post_service_action('climate', 'turn_off', data)
    get_climate_states(climate_entity_id)

    # Update UI straight away without waiting for next "every" call
    loop2()

@left_button.press
def climate_turn_on():
    # Turn on the thermostat device
    data = {'entity_id':climate_entity_id}
    ha_api.post_service_action('climate', 'turn_on', data)
    get_climate_states(climate_entity_id)

    # Update UI straight away without waiting for next "every" call
    loop2()
    

# Call the API to initialize the thermostat state information
get_climate_states(climate_entity_id)

# Setup the thermostat state icon
icon = climate_icon_ac # snowflake (for cooling/AC)
color_active = 'aqua' # active/on color (for cooling/AC)
color_idle = 'gray' # inactive/idle/off color
print(climate_operation_mode)
if 'heat' in climate_operation_list:
    icon = climate_icon_heating # fire (for heating)
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
    screen.text(button_inc_text, xy=button_inc_xy, align=button_inc_align, font_size=button_font_size, font=icon_font)
    # "minus-box-outline" (Decrease the thermostat temperature)
    screen.text(button_dec_text, xy=button_dec_xy, align=button_dec_align, font_size=button_font_size, font=icon_font)
 
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
