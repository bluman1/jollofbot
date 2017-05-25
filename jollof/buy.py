import os
import requests
import json
from pprint import pprint

from jollof.models import *

BUYER_ACCESS_TOKEN = os.environ.get('BUYER_ACCESS_TOKEN')
BLUMAN_ID = os.environ.get('BLUMAN_ID')

def buy_get_started_button():
    headers = {
        'Content-Type': 'application/json',
    }
    params = (
        ('access_token', BUYER_ACCESS_TOKEN),
    )
    data = '{"get_started":{"payload":"GET_STARTED"}}'
    response = requests.post('https://graph.facebook.com/v2.6/me/messenger_profile',
                  headers=headers, params=params, data=data)
    pprint(response.json())


def get_user_details(fbid):
    user_details_url = "https://graph.facebook.com/v2.6/%s"%fbid
    user_details_params = {'fields':'first_name,last_name,profile_pic', 'access_token':BUYER_ACCESS_TOKEN}
    user_details = requests.get(user_details_url, user_details_params).json()
    return user_details


def alert_me(fbid, alert_type):
    my_fbid = BLUMAN_ID
    if alert_type == 1:
        buyer = Buyer.objects.get(fbid=fbid)

        msg = 'New User - ' + buyer.first_name + ' ' + buyer.last_name + ' just became a Jollof Buyer. FBID = ' + str(fbid) + '.'
        headers = {
            'Content-Type': 'application/json',
        }
        params = (
            ('access_token', BUYER_ACCESS_TOKEN),
        )
        data = '{"recipient": {"id": "'+str(my_fbid)+'"},"message": {"text": "'+str(msg)+'"}}'
        pprint(str(data))
        response = requests.post('https://graph.facebook.com/v2.6/me/messages', headers=headers, params=params, data=data)
        pprint(response.json())
    else:
        msg = 'An error just occured with fbid - ' + str(fbid) + '. Type: ' + str(alert_type) + '.'
        headers = {
            'Content-Type': 'application/json',
        }
        params = (
            ('access_token', BUYER_ACCESS_TOKEN),
        )
        data = '{"recipient": {"id": "'+str(my_fbid)+'"},"message": {"text": "'+str(msg)+'"}}'
        pprint(str(data))
        response = requests.post('https://graph.facebook.com/v2.6/me/messages', headers=headers, params=params, data=data)
        pprint(response.json())


def text_message(fbid, msg):
    buyer = Buyer.objects.get(fbid=fbid)
    if '{{user_first_name}}' in msg:
        msg = msg.replace('{{user_first_name}}', buyer.first_name)
    print(msg)
    headers = {
        'Content-Type': 'application/json',
    }
    params = (
        ('access_token', BUYER_ACCESS_TOKEN),
    )
    data = '{"recipient": {"id": "'+str(fbid)+'"},"message": {"text": "'+str(msg)+'"}}'
    pprint(str(data))
    response = requests.post('https://graph.facebook.com/v2.6/me/messages', headers=headers, params=params, data=data)
    pprint(response.json())


def greet_buyer(fbid):
    msg = 'Hi {{user_first_name}}, I am JollofBot. I can help you find the nearest place where you can buy #NigerianJollof. You can either have it delivered to you right where you are or get directions to the best Jollof you\'ll ever have!'
    text_message(fbid, msg)
    headers = {
        'Content-Type': 'application/json',
    }
    params = (
        ('access_token', BUYER_ACCESS_TOKEN),
    )
    data = '''{
    "recipient":{
        "id":"USER_ID"
    },
    "message":{
        "attachment":{
        "type":"template",
        "payload":{
            "template_type":"button",
            "text":"What do you want to do, FIRST_NAME?",
            "buttons":[
            {
                "type":"postback",
                "title":"Find me Jollof!",
                "payload":"GET_LOCATION"
            },
            {
                "type":"postback",
                "title":"Find me more Jollof!!",
                "payload":"GET_LOCATION"
            },
            {
                "type":"postback",
                "title":"Chat with Jollof!",
                "payload":"TALK_TO_JOLLOF"
            }
            ]
        }
        }
    }
    }'''

    buyer = Buyer.objects.get(fbid=fbid)
    data = data.replace('FIRST_NAME', buyer.first_name)
    data = data.replace('USER_ID', fbid)
    pprint(str(data))
    response = requests.post('https://graph.facebook.com/v2.6/me/messages', headers=headers, params=params, data=data)
    pprint(response.json())
    return


def cancel_action(fbid, payload):
    buyer = Buyer.objects.get(fbid=fbid)
    buyer.current_state = 'DEFAULT'
    buyer.save()
    msg = 'I\'ve cancelled that action.'
    text_message(fbid, msg)


def request_location(fbid):
    headers = {
        'Content-Type': 'application/json',
    }
    params = (
        ('access_token', BUYER_ACCESS_TOKEN),
    )
    data = '{"recipient":{"id":"' + str(fbid) + '"},"message":{"text":"Please share your location with me.","quick_replies":[{"content_type":"location"},{"content_type":"text","title":"Cancel","payload":"CANCELLED"}]}}'
    pprint(data)
    response = requests.post('https://graph.facebook.com/v2.6/me/messages', headers=headers, params=params, data=data)
    print(response.json())


def get_buyer_location(fbid, payload, location_title=None, location_url=None, location_lat=None, location_long=None):
    if payload == 'CANCELLED':
        cancel_action(fbid, payload)
        return
    elif location_lat:
        # save location_lat and location_long
        buyer = Buyer.objects.get(fbid=fbid)
        buyer.longitude = float(location_long)
        buyer.latitude = float(location_lat)
        print('Lat: ' + str(float(location_lat)) + ' Long: ' + str(float(location_long)))
        buyer.current_state = 'DEFAULT'
        buyer.save()       
        text_message(fbid, 'you are at ' + str(location_title) + '.')
        text_message(fbid, 'Searching for nearby Jollof!')
        # Pass lat and long to function that will retrieve nearest sellers
        text_message(fbid, 'I do not know how to search yet. My creator is currently teaching me.')
        return
    request_location(fbid)
    buyer = Buyer.objects.get(fbid=fbid)
    buyer.current_state = 'GET_LOCATION'
    buyer.save()


def talk_to_jollof(fbid, text):
    if text == 'TALK_TO_JOLLOF':
        buyer = Buyer.objects.get(fbid=fbid)
        buyer.current_state = 'TALK_TO_JOLLOF'
        buyer.save()
        text_message(fbid, 'Hey {{user_first_name}}, what\'s up? :D')
        alert_me(fbid, 'Jollof chat initiated.')
        return
    alert_me(fbid, 'Jollof: ' + text)
    text_message(fbid, 'Sorry {{user_first_name}}, I do not know how to say a lot yet :(')
    greet_buyer(fbid)
    buyer = Buyer.objects.get(fbid=fbid)
    buyer.current_state = 'DEFAULT'
    buyer.save()
    return
