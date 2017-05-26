import os
import requests
import json
import geopy.distance
from pprint import pprint

from jollof.models import *

SELLER_ACCESS_TOKEN = os.environ.get('SELLER_ACCESS_TOKEN')
BLUMAN_ID = os.environ.get('BLUMAN_ID')
NEAREST_KM = 1

class Sell():

    def __init__(self):
        pass

    
    def get_started_button(self):
        headers = {
            'Content-Type': 'application/json',
        }
        params = (
            ('access_token', SELLER_ACCESS_TOKEN),
        )
        data = '{"get_started":{"payload":"GET_STARTED"}}'
        response = requests.post('https://graph.facebook.com/v2.6/me/messenger_profile',
                    headers=headers, params=params, data=data)
        pprint(response.json())


    def persistent_menu(self):
        headers = {
            'Content-Type': 'application/json',
        }
        params = (
            ('access_token', SELLER_ACCESS_TOKEN),
        )
        data = """{
            "persistent_menu":[
                {
                    "locale":"default",
                    "composer_input_disabled":false,
                    "call_to_actions":[
                        {
                        "title":"Vendor Details",
                        "type":"nested",
                        "call_to_actions":[
                            {
                                "title":"Vendor Name",
                                "type":"postback",
                                "payload":"VENDOR_NAME"
                            },
                            {
                                "title":"Vendor Location",
                                "type":"postback",
                                "payload":"VENDOR_LOCATION"
                            }
                        ]
                        },
                        {
                        "title":"Jollof Details",
                        "type":"nested",
                        "call_to_actions":[
                            {
                                "title":"Jollof Image",
                                "type":"postback",
                                "payload":"JOLLOF_IMAGE"
                            },
                            {
                                "title":"Jollof Price",
                                "type":"postback",
                                "payload":"JOLLOF_PRICE"
                            },
                            {
                                "title":"Jollof Description",
                                "type":"postback",
                                "payload":"JOLLOF_DESCRIPTION"
                            },
                            {
                                "title":"Jollof Delivery",
                                "type":"postback",
                                "payload":"JOLLOF_DELIVERY"
                            }
                        ]
                        },
                        {
                        "title":"Analytics",
                        "type":"nested",
                        "call_to_actions":[
                            {
                                "title":"Times Searched",
                                "type":"postback",
                                "payload":"TIMES_SEARCHED"
                            },
                            {
                                "title":"Times Ordered",
                                "type":"postback",
                                "payload":"TIMES_ORDERED"
                            },
                            {
                                "title":"Got Directions",
                                "type":"postback",
                                "payload":"GOT_DIRECTIONS"
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
