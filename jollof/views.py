import os
import re
import requests
import json
import random
from pprint import pprint
import googlemaps
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.password_validation import validate_password
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
from jollof.forms import *
from jollof.buy import Buy
from jollof.buy_states import *
from jollof.sell_states import *
from jollof.sell import Sell
from jollof.deliver_states import *
from jollof.deliver import Deliver

BUYER_ACCESS_TOKEN = os.environ.get('BUYER_ACCESS_TOKEN')
SELLER_ACCESS_TOKEN = os.environ.get('SELLER_ACCESS_TOKEN')
DELIVER_ACCESS_TOKEN = os.environ.get('DELIVER_ACCESS_TOKEN')

BUYER_CHALLENGE = os.environ.get('BUYER_CHALLENGE')
SELLER_CHALLENGE = os.environ.get('SELLER_CHALLENGE')
DELIVER_CHALLENGE = os.environ.get('DELIVER_CHALLENGE')

# Create your views here.

def show_landing(request):
    if request.method == 'GET':
        return render(request, 'bot.html')


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
    'REQUEST_PHONE': buy_payload.request_phone,
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
                        random_greeting = ['hello', 'hi', 'hey', 'what\'s up?','what\'s up', 'wasap']
                        buyer = Buyer.objects.get(fbid=fbid)
                        current_state = buyer.current_state
                        received_text = message['message']['text'].lower()
                        
                        if current_state == 'DEFAULT':
                            print('Buyer in default state')
                            if received_text in random_greeting:
                                print('Random greeting State: ' + current_state)
                                msg = 'Hi {{user_first_name}}! Nothing is better than Nigerian Jollof! Say Jollof! anytime to know what I can do 👊'
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
                                elif fbid == buy.BLUMAN_ID:
                                    buy.talk_to_jollof(fbid, received_text)
                                    return HttpResponse()
                                msg = 'So you wanna slide into my DM uhn? Just say Jollof! and tap on "Chat with Jollof"'
                                buy.text_message(fbid, msg)
                                buyer.current_state = 'DEFAULT'
                                buyer.save()                    
                                buy.alert_me(fbid, '\nID: ' + str(buyer.pk) + '. Name: ' + buyer.first_name + ' ' + buyer.last_name + ' Chat Not Initiated. Text: ' + str(received_text) + '.')
                                return HttpResponse()
                        elif current_state == 'TALK_TO_JOLLOF':
                            print('Not default  State: ' + current_state)
                            buy.talk_to_jollof(fbid, received_text)
                        elif current_state == 'REQUEST_PHONE':
                            print('Not default  State: ' + current_state)
                            buy.request_phone(fbid, received_text)
                        else:
                            buy.alert_me(fbid, '\nID: ' + str(buyer.pk) + '. Name: ' + buyer.first_name + ' ' + buyer.last_name + ' Empty State Msg. Text: ' + str(received_text) + '.')
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
                        buyer.current_state = 'REQUEST_PHONE'
                        buyer.save()
                        msg = 'Hey {{user_first_name}}, we finally meet 😁 But first, please share your phone number with me to get this party started 🙏'
                        buy.text_message(fbid, msg)
                        return HttpResponse()
                    else:
                        current_state = buyer.current_state
                        if current_state == 'DEFAULT':
                            temp_payload = payload
                            generic_payloads = ['ORDER_JOLLOF', 'ORDER_DELICACY', 'VIEW_DELICACY_SELLERS', 'JOLLOF_RESERVATION', 'DELICACY_RESERVATION']
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
                                            buy.alert_me(fbid, 'Failed Button payload.  current_state: ' + current_state + '. temp_payload: ' + temp_payload + '. payload: ' + payload)
                                        return HttpResponse()
                                    else:
                                        msg = 'Sorry, {{user_first_name}}. Please try saying jollof!.'
                                        text_message(fbid, msg)
                                        buyer.current_state = 'DEFAULT'
                                        buyer.save()
                                        buy.alert_me(fbid, 'Mixed up. Can not find the next state out of the generic states for current_state: ' + current_state + '. payload: ' + payload)
                                        return HttpResponse()
                            try:
                                buyer_payloads[payload](fbid, payload)
                            except Exception as e:
                                print(str(e))
                                buy.alert_me(fbid, 'Postback recieved from default state but no next state.')
                                buyer.current_state = 'DEFAULT'
                                buyer.save()
                            return HttpResponse()
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
                                                buy.alert_me(fbid, msg)
                                            return HttpResponse()
                                        else:
                                            msg = 'Sorry, {{user_first_name}}. Please try saying jollof!.'
                                            text_message(fbid, msg)
                                            buyer.current_state = 'DEFAULT'
                                            buyer.save()
                                            buy.alert_me(fbid, 'Mixed up. Can not find the next state out of the generic states for current_state: ' + current_state + '. payload: ' + payload)
                                            return HttpResponse()
                                next_state_status = is_buyer_next_state(current_state, payload)
                                if next_state_status:
                                    # perform function for next state == payload
                                    try:
                                        buyer_payloads[payload](fbid, payload) # this function is in charge of setting the new state.
                                    except Exception as e:
                                        print('Exception\n' + str(e))
                                        buy.alert_me(fbid, 'Can not find the current_state in other payload: ' + current_state + '. payload: ' + payload)
                                    return HttpResponse()
                                else:
                                    msg = 'Sorry, {{user_first_name}}. Please try saying jollof!'
                                    text_message(fbid, msg)
                                    buyer.current_state = 'DEFAULT'
                                    buyer.save()
                                    buy.alert_me(fbid, 'Mixed up. Can not find the next state for current_state: ' + current_state + '. payload: ' + payload)
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
    'JOLLOF_PENDING_DELIVERIES': sell_payload.jollof_pending_deliveries,
    'JOLLOF_PENDING_RESERVATIONS': sell_payload.jollof_pending_reservations,
    'JOLLOF_ACCEPTED_DELIVERIES': sell_payload.jollof_accepted_deliveries,
    'JOLLOF_ACCEPTED_RESERVATIONS': sell_payload.jollof_accepted_reservations,

    'DELICACY_PENDING_DELIVERIES': sell_payload.delicacy_pending_deliveries,
    'DELICACY_PENDING_RESERVATIONS': sell_payload.delicacy_pending_reservations,
    'DELICACY_ACCEPTED_DELIVERIES': sell_payload.delicacy_accepted_deliveries,
    'DELICACY_ACCEPTED_RESERVATIONS': sell_payload.delicacy_accepted_reservations,
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
                            print('Seller in default state')
                            if received_text in random_greeting:
                                print('Random greeting State: ' + current_state)
                                msg = 'Hi {{user_first_name}}! You are doing a great job!'
                                sell.text_message(fbid, msg)        
                            else:
                                if received_text.lower() == 'location':
                                    seller.current_state = 'VENDOR_LOCATION'
                                    seller.save()
                                    sell.request_location(fbid)
                                else:
                                    print('Not a random greeting. State: ' + current_state)
                                    sell.text_message(fbid, 'You sell the greatest jollof in the world!')
                                    seller.current_state = 'DEFAULT'
                                    seller.save()
                        else:
                            sell.text_message(fbid, 'You sell the greatest jollof in the world!')
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
                        #should ask for code here, or welcome seller back
                        if connected:
                            msg = 'Welcome back! I hope your jollof has been top notch.'
                            sell.text_message(fbid, msg)
                        else:
                            msg =  'Hi {{user_first_name}}, please enter the jollof code shown on your dashboard.'
                            sell.text_message(fbid, msg)
                        return HttpResponse()
                    else:
                        current_state = seller.current_state
                        if current_state != 'DEFAULT':
                            # menu click most probably
                            try:
                                menu_payloads[payload](fbid, payload)
                            except Exception as e:
                                print('Exception\n' + str(e))
                                alert_me(fbid, 'I can\'t seem to find the menu payload. payload: ' + payload)
                            return HttpResponse()
                        elif current_state == 'DEFAULT':
                            temp_payload = payload
                            generic_payloads = ['JOLLOF_PENDING_DELIVERIES', 'JOLLOF_PENDING_RESERVATIONS', 'JOLLOF_ACCEPTED_DELIVERIES', 'JOLLOF_ACCEPTED_RESERVATIONS', 'DELICACY_PENDING_DELIVERIES', 'DELICACY_PENDING_RESERVATIONS', 'DELICACY_ACCEPTED_DELIVERIES', 'DELICACY_ACCEPTED_RESERVATIONS']
                            for generic in generic_payloads:
                                if generic in payload:
                                    payload = generic
                                    next_state_status = is_seller_next_state(generic, payload)
                                    if next_state_status:
                                        try:
                                            seller_payloads[generic](fbid, temp_payload)
                                            return HttpResponse()
                                        except Exception as e:
                                            seller.current_state = 'DEFAULT'
                                            seller.save()
                                            print('Exception\n' + str(e))
                                            msg = 'Failed Button payload. current_state: ' + current_state + '. temp_payload: ' + temp_payload + '. payload: ' + payload
                                            # sell.alert_me(fbid, msg)
                                        return HttpResponse()
                                    else:
                                        msg = 'Sorry {{user_first_name}}, something must have happened to my brain.'
                                        sell.text_message(fbid, msg)
                                        seller.current_state = 'DEFAULT'
                                        seller.save()
                                        # sell.alert_me(fbid, 'Mixed up. Can not find the next state out of the generic states for current_state: ' + current_state + '. payload: ' + payload)
                                        return HttpResponse()
                            next_state_status = is_seller_next_state(current_state, payload)
                            if next_state_status:
                                # perform function for next state == payload
                                try:
                                    seller_payloads[payload](fbid, payload) # this function is in charge of setting the new state.
                                except Exception as e:
                                    print('Exception\n' + str(e))
                                    # sell.alert_me(fbid, 'Can not find the current_state in other payload: ' + current_state + '. payload: ' + payload)
                                return HttpResponse()
                            else:
                                msg = 'Sorry, {{user_first_name}}. Please try saying jollof!'
                                sell.text_message(fbid, msg)
                                seller.current_state = 'DEFAULT'
                                seller.save()
                                # sell.alert_me(fbid, 'Mixed up. Can not find the next state for current_state: ' + current_state + '. payload: ' + payload)
                                return HttpResponse()
                        return HttpResponse()


################################################################################


@csrf_exempt
def deliver_subscribe(request):
    if request.method == 'GET':
        response = requests.post(
            'https://graph.facebook.com/v2.6/me/subscribed_apps?access_token=' + DELIVER_ACCESS_TOKEN)
        pprint(response.json())
        return HttpResponse()


@csrf_exempt
def deliver_prep(request):
    deliver = Deliver()
    deliver.get_started_button()
    deliver.persistent_menu()
    return HttpResponse()


def create_fake_flash(request, flash_name):
    if request.method == 'GET':
        valid = True
        code = None
        try:
            flash = Flash.objects.get(fbid=flash_name)
            return HttpResponse(request, 'flash_code.html', {'flash_code': 'Flash group Already Exists.' }) 
        except Flash.DoesNotExist:
            pass
        while valid:
            code = 'FLASH-' + ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(3))
            try:
                flash = Flash.objects.get(flash_code=code)
                pprint(code + ' already exists.')
            except Flash.DoesNotExist:
                valid = False
        pprint('FLASHCDOE: ' + code)
        flash = Flash(fbid=flash_name, flash_code=code, first_name='Master', last_name='Slave', phone_number='0')
        flash.save()
        pprint('Master Flash Created')
        return render(request, 'flash_code.html', {'flash_code': code })


deliver_payload = Deliver()
deliver_payloads = {
    'CANCELLED': deliver_payload.cancel_action,
    'FLASH_LOCATION': deliver_payload.save_location,
    'REQUEST_PHONE': deliver_payload.request_phone,

    'PENDING_ORDERS': deliver_payload.pending_orders,
    'ACCEPT_PENDING_JOLLOF': deliver_payload.accept_pending_jollof,
    'ACCEPT_PENDING_DELICACY': deliver_payload.accept_pending_delicacy,
    
    'TO_PICKUP': deliver_payload.to_pickup,
    'PICKED_UP_JOLLOF': deliver_payload.picked_up_jollof,
    'PICKED_UP_DELICACY': deliver_payload.picked_up_delicacy,

    'TO_DROPOFF': deliver_payload.to_dropoff,
    'DROPPED_OFF_JOLLOF': deliver_payload.dropped_off_jollof,
    'DROPPED_OFF_DELICACY': deliver_payload.dropped_off_delicacy,


}


@csrf_exempt
def deliver_webhook(request):
    if request.method == 'GET':
        if request.GET['hub.verify_token'] == DELIVER_CHALLENGE:
            return HttpResponse(request.GET['hub.challenge'])
        else:
            return HttpResponse('Error, invalid token')
    elif request.method == 'POST':
        deliver = Deliver()
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
                flash = None
                connected = False
                try:
                    flash = Flash.objects.get(fbid=fbid)
                    connected = True
                except Flash.DoesNotExist:
                    # why are we depending on this alone? The first message is a postback which creates the user.
                    pass
                if 'message' in message:
                    if 'quick_reply' in message['message']:
                        pprint('QR Received.')
                    elif 'text' in message['message']:
                        print('Text Message Recieved')
                        if connected is False:
                            pprint('received flashcode')
                            deliver.process_code(fbid, message['message']['text'])
                            return HttpResponse()
                        random_greeting = ['hello', 'hi', 'hey', 'what\'s up?', 'what\'s up', 'wasap']
                        received_text = message['message']['text'].lower()
                        current_state = flash.current_state
                        if current_state == 'DEFAULT':
                            print('Flash in default state')
                            if received_text in random_greeting:
                                pprint('Random greeting State: ' + current_state)
                                msg = 'Hi {{user_first_name}}! You are doing a great job!'
                                deliver.text_message(fbid, msg)
                            elif received_text.lower() == 'busy':
                                flash.available = False
                                flash.save()
                                msg = 'I have set your status as busy. While you are busy, you will not be able to receive new order notifications. Remember to send available when you are ... available again.'
                                deliver.text_message(fbid, msg)   
                            elif received_text.lower() == 'available':
                                flash.available = True
                                flash.save()
                                msg = 'I have set your status as available. You can now receive new order notifications. Remember to send location to update your... location.'
                                deliver.text_message(fbid, msg)     
                            else:
                                if received_text.lower() == 'location':
                                    flash.current_state = 'FLASH_LOCATION'
                                    flash.save()
                                    deliver.request_location(fbid)
                                else:
                                    print('Not a random greeting. State: ' + current_state)
                                    deliver.text_message(fbid, 'You deliver the greatest jollof in the world!')
                                    flash.current_state = 'DEFAULT'
                                    flash.save()
                        elif current_state == 'REQUEST_PHONE':
                            print('Not default  State: ' + current_state)
                            deliver.request_phone(fbid, received_text)
                        else:
                            deliver.text_message(fbid, 'You deliver the greatest jollof in the world!')
                            flash.current_state = 'DEFAULT'
                            flash.save()
                        return HttpResponse()
                    elif 'attachments' in message['message']:
                        print('Attachment Recieved')
                        for attachment in message['message']['attachments']:
                            if attachment['type'] == 'location':
                                print('Location Received')
                                flash = Flash.objects.get(fbid=fbid)
                                current_state = flash.current_state
                                print('loc, current_state: ' + current_state)
                                location_title = attachment['title']
                                location_url = attachment['url']
                                location_lat = attachment['payload']['coordinates']['lat'] # This is a float, not a str
                                location_long = attachment['payload']['coordinates']['long'] # This is a float, not a str
                                try:
                                    deliver_payloads[current_state](fbid, current_state, location_title, location_url, location_lat, location_long)
                                except Exception as e:
                                    print('Exception\n' + str(e))
                                    deliver.alert_me(fbid, 'Failed to get location.')
                                    flash.current_state = 'DEFAULT'
                                    flash.save()
                        return HttpResponse()
                elif 'postback' in message:
                    payload = message['postback']['payload']
                    if payload == 'GET_STARTED':
                        if connected:
                            msg = 'Welcome back! I hope you have been delivering on time.'
                            deliver.text_message(fbid, msg)
                        else:
                            msg =  'Hi {{user_first_name}}, please enter the flash code shared with you.'
                            deliver.text_message(fbid, msg)
                        return HttpResponse()
                    else:
                        current_state = flash.current_state                
                        temp_payload = payload
                        generic_payloads = ['PENDING_ORDERS', 'ACCEPT_PENDING_JOLLOF', 'ACCEPT_PENDING_DELICACY', 'TO_PICKUP', 'PICKED_UP_JOLLOF', 'PICKED_UP_DELICACY', 'TO_DROPOFF', 'DROPPED_OFF_JOLLOF', 'DROPPED_OFF_DELICACY']
                        for generic in generic_payloads:
                            if generic in payload:
                                payload = generic
                                next_state_status = is_deliver_next_state(current_state, payload)
                                if next_state_status:
                                    try:
                                        deliver_payloads[payload](fbid, temp_payload)
                                        return HttpResponse()
                                    except Exception as e:
                                        flash.current_state = 'DEFAULT'
                                        buyer.save()
                                        pprint('Exception\n' + str(e))
                                        deliver.alert_me(fbid, 'Failed Button payload.  current_state: ' + current_state + '. temp_payload: ' + temp_payload + '. payload: ' + payload)
                                    return HttpResponse()
                                else:
                                    msg = 'Sorry, {{user_first_name}}. Please try saying jollof!.'
                                    deliver.text_message(fbid, msg)
                                    flash.current_state = 'DEFAULT'
                                    flash.save()
                                    deliver.alert_me(fbid, 'Mixed up. Can not find the next state out of the generic states for current_state: ' + current_state + '. payload: ' + payload)
                                    return HttpResponse()
                        try:
                            deliver_payloads[payload](fbid, payload)
                        except Exception as e:
                            print(str(e))
                            deliver.alert_me(fbid, 'Postback recieved from ' + current_state + ' state but no next state.')
                            flash.current_state = 'DEFAULT'
                            flash.save()
                        return HttpResponse()

sell = Sell()
def show_signup(request):
    if request.method == 'GET':
        if request.user.is_authenticated:
            return HttpResponseRedirect('/vendor/overview/')
        user_type = request.GET.get('t')
        return render(request, 'signup.html', {'user_type': user_type })
    elif request.method == 'POST':
        email = request.POST.get('email')
        username = request.POST.get('username')
        rest_name = request.POST.get('rest_name')
        password2 = request.POST.get('pwd_again')
        password = request.POST.get('password')
        if bool(re.search(r'\d', username)):
            return render(request, 'signup.html', {'merror': 'Username must contain alphabets only.'})
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
        try:
            validate_password(password)
        except ValidationError  as ve:
            return render(request, 'signup.html', {'merror': ve })
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
            user = Seller.objects.get(username=username)
            buy_obj = Buy()
            code = buy_obj.generate_jollof_code()
            print('Gen Code: ' + code)
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
            return HttpResponseRedirect('/vendor/profile/')
        else:
            """return invalid login here"""
            return render(request, 'signup.html', {'merror': 'Please go to login page.'})                

def show_login(request):
    if request.method == 'GET':
        if request.user.is_authenticated:
            return HttpResponseRedirect('/vendor/overview/')
        return render(request, 'login.html', {})
    elif request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return HttpResponseRedirect('/vendor/overview/')
        else:
            """return invalid login here"""
            return render(request, 'login.html', {'merror': 'Please try again.'})


@login_required
def show_logout(request):
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


@login_required
def show_vendor(request):
    if request.method == 'GET':
        return HttpResponseRedirect('/vendor/overview/')


@login_required 
def show_overview(request):
    if request.method == 'GET':
        seller = Seller.objects.get(pk=request.user.pk)
        jollof_code = seller.code
        pending_delicacies = DelicacyOrder.objects.filter(delicacy_seller=seller).filter(order_type=2).filter(status=0)
        pending_jollof = JollofOrder.objects.filter(jollof_seller=seller).filter(order_type=2).filter(status=0)
        pending_deliveries = pending_delicacies.count() + pending_jollof.count()

        pending_delicacies = DelicacyOrder.objects.filter(delicacy_seller=seller).filter(order_type=1).filter(status=0)
        pending_jollof = JollofOrder.objects.filter(jollof_seller=seller).filter(order_type=1).filter(status=0)
        pending_reservations = pending_delicacies.count() + pending_jollof.count()

        accepted_delicacies = DelicacyOrder.objects.filter(delicacy_seller=seller).filter(order_type=2).filter(status=0)
        accepted_jollof = JollofOrder.objects.filter(jollof_seller=seller).filter(order_type=2).filter(status=1)
        accepted_deliveries = accepted_delicacies.count() + accepted_jollof.count()

        accepted_delicacies = DelicacyOrder.objects.filter(delicacy_seller=seller).filter(order_type=1).filter(status=1)
        accepted_jollof = JollofOrder.objects.filter(jollof_seller=seller).filter(order_type=1).filter(status=1)
        accepted_reservations = accepted_delicacies.count() + accepted_jollof.count()
        c = {'user': request.user, 'pending_deliveries': pending_deliveries, 'pending_reservations': pending_reservations, 'accepted_deliveries': accepted_deliveries, 'accepted_reservations': accepted_reservations, 'jollof_code': jollof_code }
        pprint(c)
        return render(request, 'overview.html', c)


@login_required 
def show_profile(request):
    if request.method == 'GET':
        c = {}
        seller = Seller.objects.get(pk=request.user.pk)
        jollof_code = seller.code
        restaurant_name = seller.restaurant
        email = seller.email
        username = seller.username
        first_name = seller.first_name
        last_name = seller.last_name
        phone_number = seller.phone_number
        available_business = seller.available
        opening_hour = seller.opening_hour
        closing_hour = seller.closing_hour
        start_day = seller.start_day
        end_day = seller.end_day
        available_delivery = seller.delivers
        delivery_time = seller.average_delivery_time
        delivery_price = seller.delivery_price
        logo_url = str(seller.logo.url)
        try:
            logo_url = img_url[:int(logo_url.index('?'))]
        except:
            pass

        c = {'user': request.user, 'jollof_code': jollof_code, 'username': seller.username, 'restaurant_name': restaurant_name, 'email': email, 'first_name': first_name, 'last_name': last_name, 'phone_number': phone_number, 'available_business': available_business, 'opening_hour': opening_hour, 'closing_hour': closing_hour, 'available_delivery': available_delivery, 'delivery_time': delivery_time, 'delivery_price': delivery_price, 'start_day': start_day, 'end_day': end_day, 'logo_url': logo_url }
        pprint(c)
        return render(request, 'profile.html', c)
    elif request.method == 'POST':
        pprint(request.POST)
        if request.POST.get('basic'):
            #handle basic profile submission
            seller = Seller.objects.get(pk=request.user.pk)
            seller.restaurant = request.POST.get('restaurant_name', '')
            seller.first_name = request.POST.get('first_name', '')
            seller.last_name = request.POST.get('last_name', '')
            seller.phone_number = request.POST.get('phone_number', '')
            seller.save()
            #retrieve new values
            jollof_code = seller.code
            restaurant_name = seller.restaurant
            email = seller.email
            username = seller.username
            first_name = seller.first_name
            last_name = seller.last_name
            phone_number = seller.phone_number
            available_business = seller.available
            opening_hour = seller.opening_hour
            closing_hour = seller.closing_hour
            available_delivery = seller.delivers
            delivery_time = seller.average_delivery_time
            delivery_price = seller.delivery_price
            logo_url = str(seller.logo.url)
            try:
                logo_url = logo_url[:int(logo_url.index('?'))]
            except:
                pass     
            c = {'user': request.user, 'jollof_code': jollof_code, 'username': seller.username, 'restaurant_name': restaurant_name, 'email': email, 'first_name': first_name, 'last_name': last_name, 'phone_number': phone_number, 'available_business': available_business, 'opening_hour': opening_hour, 'closing_hour': closing_hour, 'available_delivery': available_delivery, 'delivery_time': delivery_time, 'delivery_price': delivery_price,'basic_result': 'Changes saved successfully.', 'logo_url': logo_url}
            pprint(c)
            return render(request, 'profile.html', c)
        elif request.POST.get('business'):
            #handle business profile submission
            seller = Seller.objects.get(pk=request.user.pk)
            seller.opening_hour = request.POST.get('opening_hour', '')
            seller.closing_hour = request.POST.get('closing_hour', '')
            seller.start_day = request.POST.get('start_day', '')
            seller.end_day = request.POST.get('end_day', '')
            seller.average_delivery_time = request.POST.get('delivery_time', '')
            seller.delivery_price = request.POST.get('delivery_price', '')
            if request.POST.get('available_delivery'):
                seller.delivers = True
            if request.POST.get('available_business'):
                seller.delivers = True
            seller.save()
            #retrieve new values
            jollof_code = seller.code
            restaurant_name = seller.restaurant
            email = seller.email
            username = seller.username
            first_name = seller.first_name
            last_name = seller.last_name
            phone_number = seller.phone_number
            available_business = seller.available
            opening_hour = seller.opening_hour
            closing_hour = seller.closing_hour
            available_delivery = seller.delivers
            delivery_time = seller.average_delivery_time
            delivery_price = seller.delivery_price
            logo_url = str(seller.logo.url)
            try:
                logo_url = logo_url[:int(logo_url.index('?'))]
            except:
                pass
            c = {'user': request.user, 'jollof_code': jollof_code, 'username': seller.username, 'restaurant_name': restaurant_name, 'email': email, 'first_name': first_name, 'last_name': last_name, 'phone_number': phone_number, 'available_business': available_business, 'opening_hour': opening_hour, 'closing_hour': closing_hour, 'available_delivery': available_delivery, 'delivery_time': delivery_time, 'delivery_price': delivery_price,'business_result': 'Changes saved successfully.', 'logo_url': logo_url}
            pprint(c)
            return render(request, 'profile.html', c)
        elif request.POST.get('logo'):
            #handle restaurant logo submission
            seller = Seller.objects.get(pk=request.user.pk)
            form = SellerLogo(request.POST, request.FILES)
            logo_result = None
            logo_url = None
            if form.is_valid():
                seller.logo = form.cleaned_data['logo']
                seller.save()
                logo_url = str(seller.logo.url)
                try:
                    logo_url = logo_url[:int(logo_url.index('?'))]
                except:
                    pass
                logo_result = 'Saved successfully.'
            else:
                #seller uploaded a non image file.
                logo_result = 'Shucks! An error occured. Please try again with a file with any of these extensions: jpg,png.'
            #retrieve new values
            jollof_code = seller.code
            restaurant_name = seller.restaurant
            email = seller.email
            username = seller.username
            first_name = seller.first_name
            last_name = seller.last_name
            phone_number = seller.phone_number
            available_business = seller.available
            opening_hour = seller.opening_hour
            closing_hour = seller.closing_hour
            available_delivery = seller.delivers
            delivery_time = seller.average_delivery_time
            delivery_price = seller.delivery_price
            logo_url = str(seller.logo.url)
            try:
                logo_url = logo_url[:int(logo_url.index('?'))]
            except:
                pass
            c = {'user': request.user, 'jollof_code': jollof_code, 'username': seller.username, 'restaurant_name': restaurant_name, 'email': email, 'first_name': first_name, 'last_name': last_name, 'phone_number': phone_number, 'available_business': available_business, 'opening_hour': opening_hour, 'closing_hour': closing_hour, 'available_delivery': available_delivery, 'delivery_time': delivery_time, 'delivery_price': delivery_price,'logo_result': logo_result, 'logo_url': logo_url}




@login_required 
def show_jollof(request):
    if request.method == 'GET':
        seller = Seller.objects.get(pk=request.user.pk)
        jollof = None
        try:
            jollof = Jollof.objects.get(seller=seller)
        except Jollof.DoesNotExist:
            c = {'user': request.user}
            pprint(c)
            return render(request, 'jollof.html', c)
        price = jollof.price
        description = jollof.description
        available = jollof.available
        delivery_price = seller.delivery_price
        jollof_url = str(jollof.image.url)
        try:
            jollof_url = jollof_url[:int(jollof_url.index('?'))]
        except:
            pass
        c = {'user': request.user, 'price': price, 'available': available, 'delivery_price': delivery_price, 'description': description, 'jollof_url': jollof_url }
        pprint(c)
        return render(request, 'jollof.html', c)
    elif request.method == 'POST':
        pprint(request.POST)
        pprint('post made')
        seller = Seller.objects.get(pk=request.user.pk)
        jollof = None
        if request.POST.get('price'):
            try:
                jollof = Jollof.objects.get(seller=seller)
                jollof.price = request.POST.get('price', '')
                jollof.description = request.POST.get('description', '')
                if request.POST.get('available'):
                    jollof.available = True
                else:
                    jollof.available = False
                jollof.save()
            except Jollof.DoesNotExist:
                available = False
                if request.POST.get('available'):
                    available = True
                jollof = Jollof(seller=seller, price=request.POST.get('price', ''), description=request.POST.get('description', ''), available=available)
                jollof.save()
            #retrieve uptodate info
            price = jollof.price
            description = jollof.description
            available = jollof.available
            delivery_price = seller.delivery_price
            jollof_url = str(jollof.image.url)
            try:
                jollof_url = jollof_url[:int(jollof_url.index('?'))]
            except:
                pass
            c = {'user': request.user, 'price': price, 'available': available, 'delivery_price': delivery_price, 'description': description, 'jollof_result': 'Jollof details saved.', 'jollof_url': jollof_url }
            pprint(c)
            return render(request, 'jollof.html', c)
        elif request.POST.get('jollof_image'):
            pprint('file received.')
            form = JollofImage(request.POST, request.FILES)
            jollof_result = None
            jollof_url = None
            if form.is_valid():
                try:
                    jollof = Jollof.objects.get(seller=seller)
                    jollof.image = form.cleaned_data['image']
                    jollof.save()
                    jollof_url = str(jollof.image.url)
                    try:
                        jollof_url = jollof_url[:int(jollof_url.index('?'))]
                    except:
                        pass
                    jollof_result = 'Saved successfully.'
                    price = jollof.price
                    description = jollof.description
                    available = jollof.available
                    delivery_price = seller.delivery_price
                    c = {'user': request.user, 'price': price, 'available': available, 'delivery_price': delivery_price, 'description': description, 'jollof_result': jollof_result, 'jollof_url': jollof_url }
                    pprint(c)
                    return render(request, 'jollof.html', c)
                except Jollof.DoesNotExist:
                    pprint('No jollof yet.')
                    jollof_result = 'Sorry, you need to setup your restaurant\'s Jollof first.'
            else:
                #seller uploaded a non image file.
                pprint('invalid file type')
                jollof_result = 'Shucks! An error occured. Please try again with a file with any of these extensions: jpg,png.'
            #retrieve uptodate info
            price = jollof.price
            description = jollof.description
            available = jollof.available
            delivery_price = seller.delivery_price
            jollof_url = str(jollof.image.url)
            try:
                jollof_url = jollof_url[:int(jollof_url.index('?'))]
            except:
                pass
            c = {'user': request.user, 'jollof_result': jollof_result}
            pprint(c)
            return render(request, 'jollof.html', c)


@login_required
def show_delicacies(request):
    if request.method == 'GET':
        seller = Seller.objects.get(pk=request.user.pk)
        delicacies = Delicacy.objects.filter(seller=seller)
        delivery_price = seller.delivery_price
        c = {'user': request.user, 'delicacies': delicacies, 'delivery_price': delivery_price}
        pprint(c)
        return render(request, 'delicacies.html', c)
    elif request.method == 'POST':
        pprint(request.POST)
        seller = Seller.objects.get(pk=request.user.pk)
        delivery_price = seller.delivery_price
        delicacy_result = None
        delicacy = None
        if request.POST.get('pk'):         
            delicacy = Delicacy.objects.get(pk=int(request.POST.get('pk')))
            delicacy.name = request.POST.get('name', '')
            delicacy.description = request.POST.get('description', '')
            delicacy.price = request.POST.get('price', '')
            if request.POST.get('available'):
                delicacy.available = True
            else:
                delicacy.available = False
            delicacy.save()
            delicacy_result = 'Delicacy changes saved.'
        else:
            delicacies = Delicacy.objects.filter(seller=seller)  
            if delicacies.count() < 10:
                available = False
                if request.POST.get('available'):
                    available = True
                delicacy = Delicacy(seller=seller, name=request.POST.get('name', ''), price=request.POST.get('price', ''), description=request.POST.get('description', ''), available=available)
                delicacy.save()
                delicacy_result = 'Delicacy created.'
            else:
                delicacy_result = 'Sorry, you can\'t have more than 10 delicacies for now.'
        delicacies = Delicacy.objects.filter(seller=seller)
        c = {'user': request.user, 'delicacies': delicacies, 'delivery_price': delivery_price, 'delicacy_result': delicacy_result }
        pprint(c)
        return render(request, 'delicacies.html', c)


@login_required 
def show_jollof_reservations(request):
    if request.method == 'GET':
        seller = Seller.objects.get(pk=request.user.pk)
        pendings = JollofOrder.objects.filter(jollof_seller=seller).filter(order_type=1).filter(status=0)
        accepteds = JollofOrder.objects.filter(jollof_seller=seller).filter(order_type=1).filter(status=1)
        c = {'user': request.user, 'pendings': pendings, 'accepteds': accepteds}
        pprint(c)
        return render(request, 'jollof_reservations.html', c)
    elif request.method == 'POST':
        pprint(request.POST)
        seller = Seller.objects.get(pk=request.user.pk)
        jollof_order = JollofOrder.objects.get(pk=int(request.POST.get('pk')))
        a = str(jollof_order.pk)
        if request.POST.get('accept'):
            sell.jollof_pending_reservations(seller.fbid, 'JOLLOF_PENDING_RESERVATIONS_'+a+'_1')
        elif request.POST.get('reject'):
            sell.jollof_pending_reservations(seller.fbid, 'JOLLOF_PENDING_RESERVATIONS_'+a+'_2')
        elif request.POST.get('complete'):
            sell.jollof_accepted_reservations(seller.fbid, 'JOLLOF_ACCEPTED_RESERVATIONS_'+a+'_1')
        elif request.POST.get('cancel'):
            sell.jollof_accepted_reservations(seller.fbid, 'JOLLOF_ACCEPTED_RESERVATIONS_'+a+'_2')
        pendings = JollofOrder.objects.filter(jollof_seller=seller).filter(order_type=1).filter(status=0)
        accepteds = JollofOrder.objects.filter(jollof_seller=seller).filter(order_type=1).filter(status=1)
        c = {'user': request.user, 'pendings': pendings, 'accepteds': accepteds}
        pprint(c)
        return render(request, 'jollof_reservations.html', c)


@login_required 
def show_jollof_deliveries(request):
    if request.method == 'GET':
        seller = Seller.objects.get(pk=request.user.pk)
        pendings = JollofOrder.objects.filter(jollof_seller=seller).filter(order_type=2).filter(status=0)
        accepteds = JollofOrder.objects.filter(jollof_seller=seller).filter(order_type=2).filter(status=1)
        c = {'user': request.user, 'pendings': pendings, 'accepteds': accepteds}
        pprint(c)
        return render(request, 'jollof_deliveries.html', c)
    elif request.method == 'POST':
        pprint(request.POST)
        seller = Seller.objects.get(pk=request.user.pk)
        jollof_order = JollofOrder.objects.get(pk=int(request.POST.get('pk')))
        a = str(jollof_order.pk)
        if request.POST.get('accept'):
            sell.jollof_pending_deliveries(seller.fbid, 'JOLLOF_PENDING_DELIVERIES_'+a+'_1')
        elif request.POST.get('reject'):
            sell.jollof_pending_deliveries(seller.fbid, 'JOLLOF_PENDING_DELIVERIES_'+a+'_2')
        elif request.POST.get('complete'):
            sell.jollof_accepted_deliveries(seller.fbid, 'JOLLOF_ACCEPTED_DELIVERIES_'+a+'_1')
        elif request.POST.get('cancel'):
            sell.jollof_accepted_deliveries(seller.fbid, 'JOLLOF_ACCEPTED_DELIVERIES_'+a+'_2')
        pendings = JollofOrder.objects.filter(jollof_seller=seller).filter(order_type=2).filter(status=0)
        accepteds = JollofOrder.objects.filter(jollof_seller=seller).filter(order_type=2).filter(status=1)
        c = {'user': request.user, 'pendings': pendings, 'accepteds': accepteds}
        pprint(c)
        return render(request, 'jollof_deliveries.html', c)


@login_required 
def show_delicacy_reservations(request):
    if request.method == 'GET':
        seller = Seller.objects.get(pk=request.user.pk)
        pendings = DelicacyOrder.objects.filter(delicacy_seller=seller).filter(order_type=1).filter(status=0)
        accepteds = DelicacyOrder.objects.filter(delicacy_seller=seller).filter(order_type=1).filter(status=1)
        c = {'user': request.user, 'pendings': pendings, 'accepteds': accepteds}
        pprint(c)
        return render(request, 'delicacy_reservations.html', c)
    elif request.method == 'POST':
        pprint(request.POST)
        seller = Seller.objects.get(pk=request.user.pk)
        delicacy_order = DelicacyOrder.objects.get(pk=int(request.POST.get('pk')))
        a = str(delicacy_order.pk)
        if request.POST.get('accept'):
            sell.delicacy_pending_reservations(seller.fbid, 'DELICACY_PENDING_RESERVATIONS_'+a+'_1')
        elif request.POST.get('reject'):
            sell.delicacy_pending_reservations(seller.fbid, 'DELICACY_PENDING_RESERVATIONS_'+a+'_2')
        elif request.POST.get('complete'):
            sell.delicacy_accepted_reservations(seller.fbid, 'DELICACY_ACCEPTED_RESERVATIONS_'+a+'_1')
        elif request.POST.get('cancel'):
            sell.delicacy_accepted_reservations(seller.fbid, 'DELICACY_ACCEPTED_RESERVATIONS_'+a+'_2')
        pendings = DelicacyOrder.objects.filter(delicacy_seller=seller).filter(order_type=1).filter(status=0)
        accepteds = DelicacyOrder.objects.filter(delicacy_seller=seller).filter(order_type=1).filter(status=1)
        c = {'user': request.user, 'pendings': pendings, 'accepteds': accepteds}
        pprint(c)
        return render(request, 'delicacy_reservations.html', c)


@login_required 
def show_delicacy_deliveries(request):
    if request.method == 'GET':
        seller = Seller.objects.get(pk=request.user.pk)
        pendings = DelicacyOrder.objects.filter(delicacy_seller=seller).filter(order_type=2).filter(status=0)
        accepteds = DelicacyOrder.objects.filter(delicacy_seller=seller).filter(order_type=2).filter(status=1)
        c = {'user': request.user, 'pendings': pendings, 'accepteds': accepteds}
        pprint(c)
        return render(request, 'delicacy_deliveries.html', c)
    elif request.method == 'POST':
        pprint(request.POST)
        seller = Seller.objects.get(pk=request.user.pk)
        delicacy_order = DelicacyOrder.objects.get(pk=int(request.POST.get('pk')))
        a = str(delicacy_order.pk)
        if request.POST.get('accept'):
            sell.delicacy_pending_deliveries(seller.fbid, 'DELICACY_PENDING_DELIVERIES_'+a+'_1')
        elif request.POST.get('reject'):
            sell.delicacy_pending_deliveries(seller.fbid, 'DELICACY_PENDING_DELIVERIES_'+a+'_2')
        elif request.POST.get('complete'):
            sell.delicacy_accepted_deliveries(seller.fbid, 'DELICACY_ACCEPTED_DELIVERIES_'+a+'_1')
        elif request.POST.get('cancel'):
            sell.delicacy_accepted_deliveries(seller.fbid, 'DELICACY_ACCEPTED_DELIVERIES_'+a+'_2')
        pendings = DelicacyOrder.objects.filter(delicacy_seller=seller).filter(order_type=2).filter(status=0)
        accepteds = DelicacyOrder.objects.filter(delicacy_seller=seller).filter(order_type=2).filter(status=1)
        c = {'user': request.user, 'pendings': pendings, 'accepteds': accepteds}
        pprint(c)
        return render(request, 'delicacy_deliveries.html', c)
        

def csu(request):
    s = Seller.objects.create_superuser('boom', 'boom@gmail.com', 'c0mpl1cat3d')
    s = Seller.objects.get('boom')
    s.first_name = 'Boom'
    s.last_name = 'Shakalaka'
    s.restaurant = 'Boom Restaurant'
    s.save()
    return HttpResponse()


def landbot(request):
    return render(request, 'bot.html')


def show_test_upload(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            m = SampleFile(title=form.cleaned_data['title'], file=form.cleaned_data['file'])
            m.save()
            form = UploadFileForm()
            c = {'form': form, 'result': 'Done', 'sample': m}
            pprint(c)
            pprint(m.file.url)
            img_url = str(m.file.url)
            img_url = img_url[:int(img_url.index('?'))]
            pprint(img_url)
            c['img_url'] = img_url
            return render(request, 'upload.html', c)
        else:
            print('not valid')
    else:
        form = UploadFileForm()
    return render(request, 'upload.html', {'form': form})