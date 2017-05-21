import os
import requests
import json
from pprint import pprint

BUYER_ACCESS_TOKEN = os.environ.get('BUYER_ACCESS_TOKEN')

def get_started_button():
    headers = {
        'Content-Type': 'application/json',
    }
    params = (
        ('access_token', BUYER_ACCESS_TOKEN),
    )
    data = '{"get_started":{"payload":"GET_STARTED_PAYLOAD"}}'
    response = requests.post('https://graph.facebook.com/v2.6/me/messenger_profile',
                  headers=headers, params=params, data=data)
    pprint(response.json())


def persistent_menu():
    headers = {
        'Content-Type': 'application/json',
    }
    params = (
        ('access_token', BUYER_ACCESS_TOKEN),
    )
    data = """{
        "persistent_menu":[
            {
                "locale":"default",
                "composer_input_disabled":false,
                "call_to_actions":[
                    {
                    "title":"Edit Details",
                    "type":"nested",
                    "call_to_actions":[
                        {
                            "title":"Farm Name",
                            "type":"postback",
                            "payload":"FARM_NAME_PAYLOAD"
                        },
                        {
                            "title":"Account Details",
                            "type":"postback",
                            "payload":"ACCOUNT_DETAILS_PAYLOAD"
                        },
                        {
                            "title":"Status & Phone Number",
                            "type":"postback",
                            "payload":"STATUS_PHONE_PAYLOAD"
                        },
                        {
                            "title":"Business Hours",
                            "type":"postback",
                            "payload":"BUSINESS_HOURS_PAYLOAD"
                        },
                        {
                            "title":"Location",
                            "type":"postback",
                            "payload":"LOCATION_PAYLOAD"
                        }
                    ]
                    },
                    {
                    "title":"Your Crops",
                    "type":"nested",
                    "call_to_actions":[
                        {
                            "title":"Add New Crop",
                            "type":"postback",
                            "payload":"ADD_NEW_CROP_PAYLOAD"
                        },
                        {
                            "title":"View My Crops",
                            "type":"postback",
                            "payload":"VIEW_YOUR_CROPS_PAYLOAD"
                        },
                        {
                            "title":"Delete a Crop",
                            "type":"postback",
                            "payload":"DELETE_CROP_PAYLOAD"
                        }
                    ]
                    },
                    {
                    "title":"Your Orders",
                    "type":"nested",
                    "call_to_actions":[
                        {
                            "title":"View All Orders",
                            "type":"postback",
                            "payload":"ALL_ORDERS_PAYLOAD"
                        },
                        {
                            "title":"View Accepted Orders",
                            "type":"postback",
                            "payload":"ACCEPTED_ORDERS_PAYLOAD"
                        },
                        {
                            "title":"View Delivered Orders",
                            "type":"postback",
                            "payload":"DELIVERED_ORDERS_PAYLOAD"
                        }
                    ]
                    }
                ]
            }
        ]
        }"""

    response = requests.post('https://graph.facebook.com/v2.6/me/messenger_profile',
                  headers=headers, params=params, data=data)
    pprint(response.json())