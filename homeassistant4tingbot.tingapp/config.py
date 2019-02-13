import json
import tingbot

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

temp_increment_by = 0.5 # Default climate temperature increment rate
if 'climate_temp_increment_by' in user_prefs:
    # If a (optional) climate temperature increment rate is provided,
    # then use it instead of the default value
    temp_increment_by = user_prefs['climate_temp_increment_by']
