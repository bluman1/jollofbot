import os
import requests
import json
import geopy.distance
from pprint import pprint

from jollof.models import *


class Sell():

    SELLER_ACCESS_TOKEN = os.environ.get('SELLER_ACCESS_TOKEN')
    BLUMAN_ID = os.environ.get('BLUMAN_ID')
    NEAREST_KM = 1

    def __init__(self):
        pass

    
    def get_started_button(self):
        headers = {
            'Content-Type': 'application/json',
        }
        params = (
            ('access_token', self.SELLER_ACCESS_TOKEN),
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
            ('access_token', self.SELLER_ACCESS_TOKEN),
        )
        data = """{
            "persistent_menu":[
                {
                    "locale":"default",
                    "composer_input_disabled":false,
                    "call_to_actions":[
                        {
                        "title":"Jollof Orders",
                        "type":"nested",
                        "call_to_actions":[
                            {
                                "title":"Pending Deliv. Orders",
                                "type":"postback",
                                "payload":"JOLLOF_PENDING_DELIVERIES"
                            },
                            {
                                "title":"Pending Reservations",
                                "type":"postback",
                                "payload":"JOLLOF_PENDING_RESERVATIONS"
                            },
                            {
                                "title":"Accepted Deliv. Orders",
                                "type":"postback",
                                "payload":"JOLLOF_ACCEPTED_DELIVERIES"
                            },
                            {
                                "title":"Accepted Reservations",
                                "type":"postback",
                                "payload":"JOLLOF_ACCEPTED_RESERVATIONS"
                            }
                        ]
                        },
                        {
                        "title":"Delicacy Orders",
                        "type":"nested",
                        "call_to_actions":[
                            {
                                "title":"Pending Deliv. Orders",
                                "type":"postback",
                                "payload":"DELICACY_PENDING_DELIVERIES"
                            },
                            {
                                "title":"Pending Reservations",
                                "type":"postback",
                                "payload":"DELICACY_PENDING_RESERVATIONS"
                            },
                            {
                                "title":"Accepted Deliv. Orders",
                                "type":"postback",
                                "payload":"DELICACY_ACCEPTED_DELIVERIES"
                            },
                            {
                                "title":"Accepted Reservations",
                                "type":"postback",
                                "payload":"DELICACY_ACCEPTED_RESERVATIONS"
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


    def get_user_details(self, fbid):
        user_details_url = "https://graph.facebook.com/v2.6/%s"%fbid
        user_details_params = {'fields':'first_name,last_name,profile_pic', 'access_token':self.SELLER_ACCESS_TOKEN}
        user_details = requests.get(user_details_url, user_details_params).json()
        return user_details
    
    
    def text_message(self, fbid, msg):
        msg = ''
        try:
            seller = Seller.objects.get(fbid=fbid)
            if '{{user_first_name}}' in msg:
                msg = msg.replace('{{user_first_name}}', seller.first_name)
        except Seller.DoesNotExist:
            msg = msg.replace('{{user_first_name}}', 'Jollof Creator')
        print(msg)
        headers = {
            'Content-Type': 'application/json',
        }
        params = (
            ('access_token', self.SELLER_ACCESS_TOKEN),
        )
        data = '{"recipient": {"id": "'+str(fbid)+'"},"message": {"text": "'+str(msg)+'"}}'
        pprint(str(data))
        response = requests.post('https://graph.facebook.com/v2.6/me/messages', headers=headers, params=params, data=data)
        pprint(response.json())
    

    def cancel_action(self, fbid, payload):
        seller = Seller.objects.get(fbid=fbid)
        seller.current_state = 'DEFAULT'
        seller.save()
        msg = 'I\'ve cancelled that action.'
        self.text_message(fbid, msg)
    

    def request_location(self, fbid):
        headers = {
            'Content-Type': 'application/json',
        }
        params = (
            ('access_token', self.BUYER_ACCESS_TOKEN),
        )
        data = '{"recipient":{"id":"' + str(fbid) + '"},"message":{"text":"Please share your location with me.","quick_replies":[{"content_type":"location"},{"content_type":"text","title":"Cancel","payload":"CANCELLED"}]}}'
        pprint(data)
        response = requests.post('https://graph.facebook.com/v2.6/me/messages', headers=headers, params=params, data=data)
        print(response.json())


    def process_code(self, fbid, jollof_code):
        try:
            seller = Seller.objects.get(code=jollof_code)
            seller.fbid = fbid
            seller.current_state = 'VENDOR_LOCATION'
            seller.save()
            msg = 'Nice having you here ' + seller.restaurant + ' :)'
            self.text_message(fbid, msg)
            self.request_location(fbid)
            return
        except Seller.DoesNotExist:
            msg = 'Sorry, the Jollof code you entered is incorrect. Please double check and enter again.'
            self.text_message(fbid, msg)
            return
    

    def save_location(self, fbid, payload, location_title=None, location_url=None, location_lat=None, location_long=None):
        if payload == 'CANCELLED':
            self.cancel_action(fbid, payload)
        elif location_lat:
            # save location_lat and location_long
            seller = Seller.objects.get(fbid=fbid)
            seller.longitude = float(location_long)
            seller.latitude = float(location_lat)
            print('Lat: ' + str(float(location_lat)) + ' Long: ' + str(float(location_long)))
            seller.current_state = 'DEFAULT'
            seller.save()       
            self.text_message(fbid, 'Great! Now you can receive order and reservation updates!')
            self.text_message(fbid, 'Please use the menu option to view pending and accepted orders/reservations.')
        return
