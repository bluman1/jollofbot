import os
import re
import requests
import json
import random
from pprint import pprint
import googlemaps
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.http.response import HttpResponse
from django.http import JsonResponse
from django.http import QueryDict
from django.shortcuts import render
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.core.mail import send_mail
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status

from jollof.models import *
from jollof.buy import *
from jollof.buy_states import *
from jollof.sell import *

BUYER_ACCESS_TOKEN = os.environ.get('BUYER_ACCESS_TOKEN')
SELLER_ACCESS_TOKEN = os.environ.get('SELLER_ACCESS_TOKEN')

BUYER_CHALLENGE = os.environ.get('BUYER_CHALLENGE')
SELLER_CHALLENGE = os.environ.get('SELLER_CHALLENGE')

# Create your views here.

def show_landing(request):
    return HttpResponse()


@csrf_exempt
def buyer_subscribe(request):
    if request.method == 'GET':
        response = requests.post(
            'https://graph.facebook.com/v2.6/me/subscribed_apps?access_token=' + BUYER_ACCESS_TOKEN)
        pprint(response.json())
        return HttpResponse()


@csrf_exempt
def buyer_prep(request):
    buy_get_started_button()
    return HttpResponse()

buyer_payloads = {
    'CANCELLED': cancel_action,
    'GET_LOCATION': get_buyer_location,
    'TALK_TO_JOLLOF': talk_to_jollof,

}

@csrf_exempt
def buyer_webhook(request):
    if request.method == 'GET':
        if request.GET['hub.verify_token'] == BUYER_CHALLENGE:
            return HttpResponse(request.GET['hub.challenge'])
        else:
            return HttpResponse('Error, invalid token')
    elif request.method == 'POST':
        # Converts the text payload into a python dictionary
        incoming_message = json.loads(request.body.decode('utf-8'))
        # Facebook recommends going through every entry since they might send
        # multiple messages in a single call during high load
        for entry in incoming_message['entry']:
            for message in entry['messaging']:
                # Check to make sure the received call is a message call
                # This might be delivery, optin, postback for other events
                pprint(message)
                fbid = message['sender']['id']
                buyer = None
                try:
                    buyer = Buyer.objects.get(fbid=fbid)
                except:
                    user_details = get_user_details(fbid)
                    buyer = Buyer(fbid=fbid, first_name=user_details['first_name'], last_name=user_details['last_name'])
                    buyer.save()
                if 'message' in message:
                    if 'quick_reply' in message['message']:
                        print('QR Received.')
                        qr_payload = message['message']['quick_reply']['payload']
                        buyer = Buyer.objects.get(fbid=fbid)
                        current_state = buyer.current_state
                        next_state_status = is_buyer_next_state(current_state, qr_payload)
                        if next_state_status:
                            try:
                                buyer_payloads[current_state](fbid, qr_payload)
                            except Exception as e:
                                print(str(e))
                                alert_me(fbid, 'Lost state for QR. Current status: ' + current_state + '. QR: ' + qr_payload)
                        else:
                            msg = 'I didn\'t quite get that, {{user_first_name}}. Say Jollof!'
                            text_message(fbid, msg)
                            buyer.current_state = 'DEFAULT'
                            buyer.save()
                            alert_me(fbid, 'Couldn\'t find the next state for the current_state. QR received.')
                        return HttpResponse()
                    elif 'text' in message['message']:
                        print('Text Message Recieved')
                        random_greeting = ['hello', 'hi', 'hey', 'what\'s up?', 'what\'s up', 'wasap']
                        buyer = Buyer.objects.get(fbid=fbid)
                        current_state = buyer.current_state
                        received_text = message['message']['text'].lower()
                        if current_state == 'DEFAULT':
                            print('Buyer in default state')
                            if received_text in random_greeting:
                                print('Random greeting State: ' + current_state)
                                msg = 'Hi {{user_first_name}}! Nothing is better than #NigerianJollof !!!'
                                # msg = str(msg.encode('utf-8'))
                                text_message(fbid, msg)         
                                return HttpResponse()
                            else:
                                print('Not a random greeting. State: ' + current_state)
                                if message['message']['text'].lower() == 'jollof':
                                    greet_buyer(fbid)
                                    return HttpResponse()
                                elif  message['message']['text'].lower() == 'jollof!':
                                    greet_buyer(fbid)
                                    return HttpResponse()
                                elif message['message']['text'].lower() == 'help':
                                    greet_buyer(fbid)
                                    return HttpResponse()
                                elif message['message']['text'].lower() == 'what can you do':
                                    greet_buyer(fbid)
                                    return HttpResponse()
                                elif message['message']['text'].lower() == 'what can you do?':
                                    greet_buyer(fbid)
                                    return HttpResponse()
                                msg = 'I didn\'t quite get that, {{user_first_name}}. Jollof is life!'
                                # msg = str(msg.encode('utf-8'))
                                text_message(fbid, msg)
                                farmer.current_state = 'DEFAULT'
                                farmer.save()
                                alert_me(fbid, 'jollof buyer is sending a text we don\'t understand yet from the DEFAULT state. Text: ' + str(received_text) + '.')
                                return HttpResponse()
                        elif current_state == 'TALK_TO_JOLLOF':
                            print('Not default  State: ' + current_state)
                            talk_to_jollof(fbid, received_text)
                        else:
                            alert_me(fbid, 'jollof buyer is sending a text we don\'t understand yet from an empty state. Text: ' + str(received_text) + '.')
                            text_message(fbid, 'I am but the greatest jollof in the world.')
                            buyer.current_state = 'DEFAULT'
                            buyer.save()
                        return HttpResponse()
                    elif 'attachments' in message['message']:
                        print('Attachment Recieved')
                        for attachment in message['message']['attachments']:
                            if attachment['type'] == 'location':
                                print('Location Received')
                                buyer = Buyer.objects.get(fbid=fbid)
                                current_state = buyer.current_state
                                print('loc, current_state: ' + current_state)
                                location_title = attachment['title']
                                location_url = attachment['url']
                                location_lat = attachment['payload']['coordinates']['lat'] # This is a float, not a str
                                location_long = attachment['payload']['coordinates']['long'] # This is a float, not a str
                                try:
                                    buyer_payloads[current_state](fbid, current_state, location_title, location_url, location_lat, location_long)
                                except Exception as e:
                                    print('Exception\n' + str(e))
                                    alert_me(fbid, 'Failed to get location.')
                                    buyer.current_state = 'DEFAULT'
                                    buyer.save()
                        return HttpResponse()
                elif 'postback' in message:
                    payload = message['postback']['payload']
                    if payload == 'GET_STARTED':
                        buyer.current_state = 'DEFAULT'
                        buyer.save()
                        greet_buyer(fbid)
                        return HttpResponse()
                    else:
                        current_state = buyer.current_state
                        if current_state == 'DEFAULT':
                            try:
                                buyer_payloads[payload](fbid, payload)
                            except Exception as e:
                                print(str(e))
                                alert_me(fbid, 'Postback recieved from default state but no next state.')
                                buyer.current_state = 'DEFAULT'
                                buyer.save()
                        return HttpResponse()



###################################################################################################


@csrf_exempt
def seller_subscribe(request):
    if request.method == 'GET':
        response = requests.post(
            'https://graph.facebook.com/v2.6/me/subscribed_apps?access_token=' + SELLER_ACCESS_TOKEN)
        pprint(response.json())
        return HttpResponse()


@csrf_exempt
def seller_prep(request):
    sell_get_started_button()
    # c2c_persistent_menu()
    return HttpResponse()


@csrf_exempt
def seller_webhook(request):
    if request.method == 'GET':
        if request.GET['hub.verify_token'] == SELLER_CHALLENGE:
            return HttpResponse(request.GET['hub.challenge'])
        else:
            return HttpResponse('Error, invalid token')
    elif request.method == 'POST':
        # Converts the text payload into a python dictionary
        incoming_message = json.loads(request.body.decode('utf-8'))