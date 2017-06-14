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
from jollof.buy import Buy
from jollof.buy_states import *
from jollof.sell_states import *
from jollof.sell import Sell

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
    buy = Buy()
    buy.get_started_button()
    return HttpResponse()

buy_payload = Buy()
buyer_payloads = {
    'CANCELLED': buy_payload.cancel_action,
    'GET_LOCATION_JOLLOF': buy_payload.get_jollof_location,
    'GET_LOCATION_DELICACY': buy_payload.get_delicacy_location,
    'TALK_TO_JOLLOF': buy_payload.talk_to_jollof,
    'ORDER_JOLLOF': buy_payload.order_jollof,
    'JOLLOF_RESERVATION': buy_payload.make_jollof_reservation,
    'DELICACY_RESERVATION': buy_payload.make_delicacy_reservation,
    'ORDER_DELICACY': buy_payload.order_delicacy,
    'VIEW_DELICACY_SELLERS': buy_payload.view_delicacy_sellers,

}

@csrf_exempt
def buyer_webhook(request):
    if request.method == 'GET':
        if request.GET['hub.verify_token'] == BUYER_CHALLENGE:
            return HttpResponse(request.GET['hub.challenge'])
        else:
            return HttpResponse('Error, invalid token')
    elif request.method == 'POST':
        buy = Buy()
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
                    user_details = buy.get_user_details(fbid)
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
                                buy.alert_me(fbid, 'Lost state for QR. Current status: ' + current_state + '. QR: ' + qr_payload)
                        else:
                            msg = 'I didn\'t quite get that, {{user_first_name}}. Say Jollof!'
                            buy.text_message(fbid, msg)
                            buyer.current_state = 'DEFAULT'
                            buyer.save()
                            buy.alert_me(fbid, 'Couldn\'t find the next state for the current_state. QR received.')
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
                                msg = 'Hi {{user_first_name}}! Nothing is better than Nigerian Jollof! Say Jollof! anytime to know what I can do :D'
                                # msg = str(msg.encode('utf-8'))
                                buy.text_message(fbid, msg)         
                                return HttpResponse()
                            else:
                                print('Not a random greeting. State: ' + current_state)
                                if message['message']['text'].lower() == 'jollof':
                                    buy.greet_buyer(fbid)
                                    return HttpResponse()
                                elif  message['message']['text'].lower() == 'jollof!':
                                    buy.greet_buyer(fbid)
                                    return HttpResponse()
                                elif message['message']['text'].lower() == 'help':
                                    buy.greet_buyer(fbid)
                                    return HttpResponse()
                                elif message['message']['text'].lower() == 'what can you do':
                                    buy.greet_buyer(fbid)
                                    return HttpResponse()
                                elif message['message']['text'].lower() == 'what can you do?':
                                    buy.greet_buyer(fbid)
                                    return HttpResponse()
                                elif message['message']['text'].lower() == 'status':
                                    buy.order_status(fbid)
                                    return HttpResponse()
                                elif message['message']['text'].lower() == 'cancel':
                                    buy.cancel_order(fbid)
                                    return HttpResponse()
                                msg = 'I didn\'t quite get that, {{user_first_name}}. Jollof is life!'
                                # msg = str(msg.encode('utf-8'))
                                buy.text_message(fbid, msg)
                                buyer.current_state = 'DEFAULT'
                                buyer.save()
                                buy.alert_me(fbid, 'Jollof buyer is sending a text we don\'t understand yet from the DEFAULT state. Text: ' + str(received_text) + '.')
                                return HttpResponse()
                        elif current_state == 'TALK_TO_JOLLOF':
                            print('Not default  State: ' + current_state)
                            buy.talk_to_jollof(fbid, received_text)
                        else:
                            buy.alert_me(fbid, 'jollof buyer is sending a text we don\'t understand yet from an empty state. Text: ' + str(received_text) + '.')
                            buy.text_message(fbid, 'I am but the greatest jollof in the world.')
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
                                    buy.alert_me(fbid, 'Failed to get location.')
                                    buyer.current_state = 'DEFAULT'
                                    buyer.save()
                        return HttpResponse()
                elif 'postback' in message:
                    payload = message['postback']['payload']
                    if payload == 'GET_STARTED':
                        buyer.current_state = 'DEFAULT'
                        buyer.save()
                        buy.greet_buyer(fbid)
                        return HttpResponse()
                    else:
                        current_state = buyer.current_state
                        if current_state == 'DEFAULT':
                            temp_payload = payload
                            generic_payloads = ['ORDER_JOLLOF', 'ORDER_DELICACY', 'VIEW_DELICACY_SELLERS']
                            for generic in generic_payloads:
                                if generic in payload:
                                    payload = generic
                                    next_state_status = is_buyer_next_state(payload, payload)
                                    if next_state_status:
                                        try:
                                            buyer_payloads[payload](fbid, temp_payload)
                                            return HttpResponse()
                                        except Exception as e:
                                            buyer.current_state = 'DEFAULT'
                                            buyer.save()
                                            print('Exception\n' + str(e))
                                            alert_me(fbid, 'Failed Button payload.  current_state: ' + current_state + '. temp_payload: ' + temp_payload + '. payload: ' + payload)
                                        return HttpResponse()
                                    else:
                                        msg = 'Sorry, {{user_first_name}}. Please try saying jollof!.'
                                        text_message(fbid, msg)
                                        buyer.current_state = 'DEFAULT'
                                        buyer.save()
                                        alert_me(fbid, 'Mixed up. Can not find the next state out of the generic states for current_state: ' + current_state + '. payload: ' + payload)
                                        return HttpResponse()
                            try:
                                buyer_payloads[payload](fbid, payload)
                            except Exception as e:
                                print(str(e))
                                buy.alert_me(fbid, 'Postback recieved from default state but no next state.')
                                buyer.current_state = 'DEFAULT'
                                buyer.save()
                        else:
                            if payload in ['GET_LOCATION_JOLLOF', 'GET_LOCATION_DELICACY', 'TALK_TO_JOLLOF']:
                                try:
                                    buyer_payloads[payload](fbid, payload)
                                except Exception as e:
                                    print(str(e))
                                    buy.alert_me(fbid, 'Postback recieved from ' + current_state + ' tried to do basic function.')
                                    buyer.current_state = 'DEFAULT'
                                    buyer.save()
                            else:
                                temp_payload = payload
                                generic_payloads = ['ORDER_JOLLOF', 'VIEW_DELICACY_SELLERS']
                                for generic in generic_payloads:
                                    if generic in payload:
                                        payload = generic
                                        next_state_status = is_buyer_next_state(current_state, payload)
                                        if next_state_status:
                                            try:
                                                buyer_payloads[current_state](fbid, temp_payload)
                                                return HttpResponse()
                                            except Exception as e:
                                                buyer.current_state = 'DEFAULT'
                                                buyer.save()
                                                print('Exception\n' + str(e))
                                                msg = 'Failed Button payload. current_state: ' + current_state + '. temp_payload: ' + temp_payload + '. payload: ' + payload
                                                alert_me(fbid, msg)
                                            return HttpResponse()
                                        else:
                                            msg = 'Sorry, {{user_first_name}}. Please try saying jollof!.'
                                            text_message(fbid, msg)
                                            buyer.current_state = 'DEFAULT'
                                            buyer.save()
                                            alert_me(fbid, 'Mixed up. Can not find the next state out of the generic states for current_state: ' + current_state + '. payload: ' + payload)
                                            return HttpResponse()
                                next_state_status = is_buyer_next_state(current_state, payload)
                                if next_state_status:
                                    # perform function for next state == payload
                                    try:
                                        buyer_payloads[payload](fbid, payload) # this function is in charge of setting the new state.
                                    except Exception as e:
                                        print('Exception\n' + str(e))
                                        alert_me(fbid, 'Can not find the current_state in other payload: ' + current_state + '. payload: ' + payload)
                                    return HttpResponse()
                                else:
                                    msg = 'Sorry, {{user_first_name}}. Please try saying jollof!'
                                    text_message(fbid, msg)
                                    buyer.current_state = 'DEFAULT'
                                    buyer.save()
                                    alert_me(fbid, 'Mixed up. Can not find the next state for current_state: ' + current_state + '. payload: ' + payload)
                                    return HttpResponse()
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
    sell = Sell()
    sell.get_started_button()
    sell.persistent_menu()
    return HttpResponse()


sell_payload = Sell()
seller_payloads = {
    'CANCELLED': sell_payload.cancel_action,
    'VENDOR_LOCATION': sell_payload.save_location,
}
@csrf_exempt
def seller_webhook(request):
    if request.method == 'GET':
        if request.GET['hub.verify_token'] == SELLER_CHALLENGE:
            return HttpResponse(request.GET['hub.challenge'])
        else:
            return HttpResponse('Error, invalid token')
    elif request.method == 'POST':
        sell = Sell()
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
                seller = None
                connected = False
                try:
                    seller = Seller.objects.get(fbid=fbid)
                    connected = True
                except Seller.DoesNotExist:
                    pass
                if 'message' in message:
                    if 'quick_reply' in message['message']:
                        print('QR Received.')
                    elif 'text' in message['message']:
                        print('Text Message Recieved')
                        if connected is False:
                            print('received jollofcode')
                            sell.process_code(fbid, message['message']['text'])
                            return HttpResponse()
                        random_greeting = ['hello', 'hi', 'hey', 'what\'s up?', 'what\'s up', 'wasap']
                        received_text = message['message']['text'].lower()
                        seller = Seller.objects.get(fbid=fbid)
                        current_state = seller.current_state
                        if current_state == 'DEFAULT':
                            print('Buselleryer in default state')
                            if received_text in random_greeting:
                                print('Random greeting State: ' + current_state)
                                msg = 'Hi {{user_first_name}}! You are doing a great job!'
                                sell.text_message(fbid, msg)        
                            else:
                                print('Not a random greeting. State: ' + current_state)
                                sell.text_message(fbid, 'You sell the greatest jollof in the world.')
                                seller.current_state = 'DEFAULT'
                                seller.save()
                        else:
                            sell.text_message(fbid, 'You sell the greatest jollof in the world.')
                            seller.current_state = 'DEFAULT'
                            seller.save()
                        return HttpResponse()
                    elif 'attachments' in message['message']:
                        print('Attachment Recieved')
                        for attachment in message['message']['attachments']:
                            if attachment['type'] == 'location':
                                print('Location Received')
                                seller = Seller.objects.get(fbid=fbid)
                                current_state = seller.current_state
                                print('loc, current_state: ' + current_state)
                                location_title = attachment['title']
                                location_url = attachment['url']
                                location_lat = attachment['payload']['coordinates']['lat'] # This is a float, not a str
                                location_long = attachment['payload']['coordinates']['long'] # This is a float, not a str
                                try:
                                    seller_payloads[current_state](fbid, current_state, location_title, location_url, location_lat, location_long)
                                except Exception as e:
                                    print('Exception\n' + str(e))
                                    sell.alert_me(fbid, 'Failed to get location.')
                                    seller.current_state = 'DEFAULT'
                                    seller.save()
                        return HttpResponse()
                elif 'postback' in message:
                    payload = message['postback']['payload']
                    if payload == 'GET_STARTED':
                        #should ask for code here,
                        msg =  'Hi {{user_first_name}}, please enter the jollof code provided by my creator.'
                        sell.text_message(fbid, msg)
                        return HttpResponse()
                    else:
                        current_state = buyer.current_state
                        if current_state == 'DEFAULT':
                            pass
                        else:
                            temp_payload = payload
                            generic_payloads = ['ORDER_JOLLOF', 'VIEW_DELICACY_SELLERS']
                            for generic in generic_payloads:
                                if generic in payload:
                                    payload = generic
                                    next_state_status = is_seller_next_state(current_state, payload)
                                    if next_state_status:
                                        try:
                                            seller_payloads[current_state](fbid, temp_payload)
                                            return HttpResponse()
                                        except Exception as e:
                                            seller.current_state = 'DEFAULT'
                                            seller.save()
                                            print('Exception\n' + str(e))
                                            msg = 'Failed Button payload. current_state: ' + current_state + '. temp_payload: ' + temp_payload + '. payload: ' + payload
                                            alert_me(fbid, msg)
                                        return HttpResponse()
                                    else:
                                        msg = 'Sorry, {{user_first_name}}. Please try saying jollof!.'
                                        text_message(fbid, msg)
                                        seller.current_state = 'DEFAULT'
                                        seller.save()
                                        alert_me(fbid, 'Mixed up. Can not find the next state out of the generic states for current_state: ' + current_state + '. payload: ' + payload)
                                        return HttpResponse()
                            next_state_status = is_seller_next_state(current_state, payload)
                            if next_state_status:
                                # perform function for next state == payload
                                try:
                                    seller_payloads[payload](fbid, payload) # this function is in charge of setting the new state.
                                except Exception as e:
                                    print('Exception\n' + str(e))
                                    alert_me(fbid, 'Can not find the current_state in other payload: ' + current_state + '. payload: ' + payload)
                                return HttpResponse()
                            else:
                                msg = 'Sorry, {{user_first_name}}. Please try saying jollof!'
                                text_message(fbid, msg)
                                seller.current_state = 'DEFAULT'
                                seller.save()
                                alert_me(fbid, 'Mixed up. Can not find the next state for current_state: ' + current_state + '. payload: ' + payload)
                                return HttpResponse()
                        return HttpResponse()


def show_signup(request):
    if request.method == 'GET':
        if request.user.is_authenticated:
            return HttpResponseRedirect('/dash/')
        return render(request, 'signup.html', {})
    elif request.method == 'POST':
        email = request.POST.get('email')
        username = request.POST.get('username')
        rest_name = request.POST.get('rest_name')
        password2 = request.POST.get('pwd_again')
        password = request.POST.get('password')
        if len(password) < 6:
            return render(request, 'signup.html', {'merror': 'Enter a password longer than that.'})
        if password != password2:
            return render(request, 'signup.html', {'merror': 'Enter matching passwords.'})
        try:
            Seller.objects.get(email=email)
            return render(request, 'signup.html', {'merror': 'User already exists.'})
        except Seller.DoesNotExist:
            pass
        try:
            Seller.objects.get(username=username)
            return render(request, 'signup.html', {'merror': 'User already exists.'})
        except Seller.DoesNotExist:
            pass
        print('DEBUG: Signup ' + email + '\t' + password)
        user = None
        try:
            user = Seller.objects.create_user(username, email, password)
            user.restaurant = rest_name
            user.save()
        except Exception as e:
            print(str(e))
            return render(request, 'signup.html', {'merror': 'User already exists.'})
        try:
            user = Seller.objects.get(email=email)
            buy_obj = Buy()
            code = buy_obj.generate_jollof_code()
            user.code = code
            user.save()
            print('CODE: ' + code)
        except:
            # The below should never run.
            print('Duplicate Jollof code. Regenerate.')
        auth_user = authenticate(username=username, password=password)
        seller = Seller.objects.get(username=username)
        if auth_user is not None:
            login(request, auth_user)
            return HttpResponseRedirect('/dash/')
        else:
            """return invalid login here"""
            return render(request, 'signup.html', {'merror': 'Please go to login page.'})                

def show_login(request):
    if request.method == 'GET':
        if request.user.is_authenticated:
            return HttpResponseRedirect('/dash/')
        return render(request, 'login.html', {})
    elif request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return HttpResponseRedirect('/dash/')
        else:
            """return invalid login here"""
            return render(request, 'login.html', {'merror': 'Please try again.'})


@login_required
def show_logout(request, username):
    if request.method == 'GET':
        logout(request)
        return HttpResponseRedirect('/')


@login_required    
def show_dash(request):
    if request.method == 'GET':
        if request.user.is_authenticated:
            seller = Seller.objects.get(pk=request.user.pk)
            jollof_code = seller.code
            restaurant_name = seller.restaurant
            c = {'user': request.user, 'jollof_code': jollof_code, 'username': seller.username, 'restaurant_name': restaurant_name}
            pprint(c)
            return render(request, 'dash.html', c)
        return HttpResponseRedirect('/')
