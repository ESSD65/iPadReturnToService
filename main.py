import base64
import json
import os
import time

import requests

import BearerToken


if __name__ == '__main__':

    jamf_endpoint = None
    wifi_profile = None
    json_config = None
    target_mobile_device_groups = None

    is_first_run = False

    # Try to pull from existing configuration profile
    if os.path.exists('config.json'):
        with open('config.json', 'r') as config_file:
            try:
                json_config = json.load(config_file)
                wifi_profile = json_config.get('wifi_profile')
                jamf_endpoint = json_config.get('jamf_endpoint')
                target_mobile_device_groups = json_config.get('target_mobile_device_groups')
            except (json.decoder.JSONDecodeError, KeyError) as error:
                print(f"Failed to parse json: {str(error)}")
                is_first_run = True
                jamf_endpoint = None
                wifi_profile = None
                json_config = None
                target_mobile_device_groups = None

    # request endpoint, if absent
    if jamf_endpoint is None or len(jamf_endpoint) == 0:
        jamf_endpoint = input("Please enter your jamf endpoint, i.e. https://casper.YOURDOMAIN.com:8443\n")
        json_config['jamf_endpoint'] = jamf_endpoint
        is_first_run = True

    # request wifi profile, if absent
    if wifi_profile is None or len(wifi_profile) == 0:
        file_path = input("Please enter the path to your wireless configuration profile:\n")
        is_first_run = True

        with open(file_path, 'rb') as config_profile:
            contents = config_profile.read()
            wifi_profile = base64.b64encode(contents).decode('utf-8')
            json_config['wifi_profile'] = wifi_profile

    # request the target mobile device groups, if absent
    if target_mobile_device_groups is None or len(target_mobile_device_groups) == 0:
        is_first_run = True
        target_groups = input("Please enter the ID(s) of the target mobile device groups, separated with comma if "
                              "there are multiple:\n")
        target_mobile_device_groups = target_groups.replace(' ', '').split(",")
        json_config['target_mobile_device_groups'] = target_mobile_device_groups

    if wifi_profile is None or len(wifi_profile) == 0:
        exit("Unable to read WiFi profile")
    if not jamf_endpoint[-1] == "/":
        jamf_endpoint += "/"

    # build token and configure headers
    token = BearerToken.get_uapi_token(jamf_endpoint)
    if token is None:
        exit("Unable to get valid bearer token.")
    headers = {
        'Accept': 'application/json',
        'Content-type': 'application/json',
        'Authorization': 'Bearer ' + BearerToken.get_bearer_token()
    }

    # gather target devices
    target_devices = []
    for target_mobile_device_group in target_mobile_device_groups:
        print(f"Using target mobile device group: {target_mobile_device_group}")
        try:
            group = requests.get(jamf_endpoint + f"JSSResource/mobiledevicegroups/id/{target_mobile_device_group}",
                                 headers=headers)

            mobile_devices = group.json().get('mobile_device_group').get('mobile_devices')
            for mobile_device in mobile_devices:
                device_id = mobile_device.get('id')
                device_data = requests.get(jamf_endpoint + f"api/v2/mobile-devices/{device_id}", headers=headers)
                device_json = device_data.json()
                print("Adding device: " + device_json.get('name'))
                target_devices.append(device_json.get('managementId'))
                time.sleep(1)
        except:
            print("Failed to pull mobile device group")

    # eliminate duplicates
    target_devices = list(set(target_devices))

    # check if this is the first run.  if not, send commands
    if not is_first_run:
        for device in target_devices:
            data = {
                "commandData": {
                    "returnToService": {
                        "enabled": True,
                        "wifiProfileData": wifi_profile
                    },
                    "commandType": "ERASE_DEVICE"
                },
                "clientData": [
                    {
                        "managementId": device
                    }
                ]
            }
            request = requests.post(jamf_endpoint + "api/preview/mdm/commands", headers=headers, json=data)
            time.sleep(1)

    # Save the current configuration since we reached this point without any errors.
    with open('config.json', 'w') as config_file:
        json.dump(json_config, config_file)
