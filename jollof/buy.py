import os
import re
import requests
import json
import random
import string
import geopy.distance
from pprint import pprint

from jollof.models import *


class Buy(object):
    
    def __init__(self):
        self.BUYER_ACCESS_TOKEN = os.environ.get('BUYER_ACCESS_TOKEN')
        self.BLUMAN_ID = os.environ.get('BLUMAN_ID')
        self.NEAREST_KM = float(os.environ.get('NEAREST_KM'))

    
    def get_distance(self, coords1, coords2):
        # coords_1 = (52.2296756, 21.0122287) lat,long
        # coords_2 = (52.406374, 16.9251681) lat,long
        distance = geopy.distance.vincenty(coords1, coords2).km
        print('Distance: ' + str(distance))
        return distance

    
    def get_directions(self, origin_lat, origin_long, dest_lat, dest_long):
        return 'https://www.google.com/maps/dir/' + str(origin_lat) + ',' + str(origin_long) + '/' + str(dest_lat) + ',' + str(dest_long) + '/'


    def generate_order_code(self):
        valid = True
        code = None
        while valid:
            code = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(6))
            try:
                jollof_order = JollofOrder.objects.get(code=code)
                print(code + ' already exists.')
                continue
            except JollofOrder.DoesNotExist:
                try:
                    delicacy_order = DelicacyOrder.objects.get(code=code)
                    print(code + ' already exists.')
                    continue
                except DelicacyOrder.DoesNotExist:
                    valid = False
        print('ORDERCODE: ' + code)
        return code
    

    def generate_jollof_code(self):
        valid = True
        code = None
        while valid:
            code = 'JLF' + ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(3))
            try:
                seller = Profile.objects.get(code=code)
                print(code + ' already exists.')
            except Profile.DoesNotExist:
                valid = False
        print('JOLLOFCODE: ' + code)
        return code


    def parse_phone(self, phone):
        ''' A valid Nigerian phone number.  
        08012345678 - 11 digits starts with 0, network=80,81,70,90, followed by 8 digits
        +2348012345678 - 13 digits with +, code=234, network=80,81,70,90, followed by 8 digits
        0112345678 - 10 digits starts with 01, followed by 8 digits
        '''
        network_operators = ['80', '81', '70', '90', '01']
        phone_len = len(phone)
        if phone_len == 14 and phone.startswith('+234') and phone[4:6] in network_operators:
            #+2348012345678
            return True
        if phone_len == 11 and phone.startswith('0') and phone[1:3] in network_operators:
            #08012345678
            return True
        if phone_len == 10 and phone.startswith('01'):
            #0112345678
            return True
        return False


    def get_started_button(self):
        headers = {
            'Content-Type': 'application/json',
        }
        params = (
            ('access_token', self.BUYER_ACCESS_TOKEN),
        )
        data = '{"get_started":{"payload":"GET_STARTED"}}'
        response = requests.post('https://graph.facebook.com/v2.6/me/messenger_profile',
                    headers=headers, params=params, data=data)
        pprint(response.json())


    def get_user_details(self, fbid):
        user_details_url = "https://graph.facebook.com/v2.6/%s"%fbid
        user_details_params = {'fields':'first_name,last_name,profile_pic', 'access_token':self.BUYER_ACCESS_TOKEN}
        user_details = requests.get(user_details_url, user_details_params).json()
        return user_details


    def alert_me(self, fbid, alert_type):
        my_fbid = self.BLUMAN_ID
        if alert_type == 1:
            buyer = Profile.objects.get(fbid=fbid)

            msg = 'New User - ' + buyer.user.first_name + ' ' + buyer.user.last_name + ' just became a Jollof Buyer. FBID = ' + str(fbid) + '.'
            headers = {
                'Content-Type': 'application/json; charset=utf-8',
            }
            params = (
                ('access_token', self.BUYER_ACCESS_TOKEN),
            )
            data = {"recipient": {"id": str(my_fbid)},"message": {"text": str(msg)}}
            data = json.dumps(data).encode("utf-8")
            response = requests.post('https://graph.facebook.com/v2.6/me/messages', headers=headers, params=params, data=data)
            pprint(response.json())
        else:
            msg = 'FBID - ' + str(fbid) + '. INFO: ' + str(alert_type) + '.'
            headers = {
                'Content-Type': 'application/json; charset=utf-8',
            }
            params = (
                ('access_token', self.BUYER_ACCESS_TOKEN),
            )
            data = {"recipient": {"id": str(my_fbid)},"message": {"text": str(msg)}}
            data = json.dumps(data).encode("utf-8")
            response = requests.post('https://graph.facebook.com/v2.6/me/messages', headers=headers, params=params, data=data)
            pprint(response.json())


    def text_message(self, fbid, msg):
        buyer = Profile.objects.get(fbid=fbid)
        if '{{user_first_name}}' in msg:
            msg = msg.replace('{{user_first_name}}', buyer.user.first_name)
        print(msg)
        headers = {
            'Content-Type': 'application/json; charset=utf-8',         
        }
        params = (
            ('access_token', self.BUYER_ACCESS_TOKEN),
        )
        data = {"recipient": {"id": str(fbid)},"message": {"text": str(msg)}}
        data = json.dumps(data).encode("utf-8")
        response = requests.post('https://graph.facebook.com/v2.6/me/messages', headers=headers, params=params, data=data)
        pprint(response.json())

    
    def text_seller(self, fbid, msg):
        headers = {
            'Content-Type': 'application/json; charset=utf-8',
        }
        params = (
            ('access_token', os.environ.get('SELLER_ACCESS_TOKEN')),
        )
        data = {"recipient": {"id": str(fbid)},"message": {"text": str(msg)}}
        data = json.dumps(data).encode("utf-8")
        response = requests.post('https://graph.facebook.com/v2.6/me/messages', headers=headers, params=params, data=data)
        pprint(response.json())


    def greet_buyer(self, fbid):
        msg = 'Hi {{user_first_name}} 🙌, I am JollofBot 😎 and I can help you find the nearest place where you can buy Jollof 🍲 and other delicacies 🍱 You can either have it delivered 🛵 to you right where you are as quick as ⚡ or get directions ↗ to the best Jollof you\'ll ever have!'
        self.text_message(fbid, msg)
        headers = {
            'Content-Type': 'application/json; charset=utf-8',
        }
        params = (
            ('access_token', self.BUYER_ACCESS_TOKEN),
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
                "text":"What would you like, FIRST_NAME?",
                "buttons":[
                {
                    "type":"postback",
                    "title":"I want Jollof! 🍲",
                    "payload":"GET_LOCATION_JOLLOF"
                },
                {
                    "type":"postback",
                    "title":"I want Delicacies!🍱",
                    "payload":"GET_LOCATION_DELICACY"
                },
                {
                    "type":"postback",
                    "title":"Chat with Jollof!😎",
                    "payload":"TALK_TO_JOLLOF"
                }
                ]
            }
            }
        }
        }'''

        buyer = Profile.objects.get(fbid=fbid)
        data = data.replace('FIRST_NAME', buyer.user.first_name)
        data = data.replace('USER_ID', fbid)
        data = json.dumps(json.loads(data)).encode('utf-8')
        response = requests.post('https://graph.facebook.com/v2.6/me/messages', headers=headers, params=params, data=data)
        pprint(response.json())
        return


    def cancel_action(self, fbid, payload):
        buyer = Profile.objects.get(fbid=fbid)
        buyer.current_state = 'DEFAULT'
        buyer.save()
        msg = 'I\'ve cancelled that action.'
        self.text_message(fbid, msg)


    def request_phone(self, fbid, text):
        buyer = Profile.objects.get(fbid=fbid)
        phone = self.parse_phone(text.strip())
        if not phone:
            msg = 'Ugh mehn, that phone number doesn\'t look right 🤦. Please enter a valid Nigerian Phone Number. e.g. 08030123456'
            self.text_message(fbid, msg)
            return
        buyer.phone_number = text.strip()
        buyer.current_state = 'DEFAULT'
        buyer.save()
        msg = 'Woot woot!💃💃💃 I can now contact you when any of your deliveries arrive. Now to properly introduce myself...'
        self.text_message(fbid, msg)
        self.greet_buyer(fbid)
        return


    def request_location(self, fbid):
        headers = {
            'Content-Type': 'application/json',
        }
        params = (
            ('access_token', self.BUYER_ACCESS_TOKEN),
        )
        data = '{"recipient":{"id":"' + str(fbid) + '"},"message":{"text":"Please share your location with me.","quick_replies":[{"content_type":"location"},{"content_type":"text","title":"Cancel","payload":"CANCELLED"}]}}'
        response = requests.post('https://graph.facebook.com/v2.6/me/messages', headers=headers, params=params, data=data)
        pprint(response.json())

    
    def jollof_chat(self, fbid, received):
        if fbid == self.BLUMAN_ID:
            splitit = received.split('_')
            if len(splitit) != 2:
                msg = 'I didn\'t quite get that, {{user_first_name}}. Jollof is life! 😁'
                self.text_message(fbid, msg)
                return
            buyer_pk = int(splitit[0])
            buyer = Profile.objects.get(pk=buyer_pk)
            buyer_fbid = buyer.fbid
            to_send = str(splitit[1])
            if splitit[1].lower() == 'done':
                buyer.current_state = 'DEFAULT'
                buyer.save()
            else:
                self.text_message(buyer_fbid, to_send)
        else:
            original = received
            if received.lower() == 'done':
                buyer = Profile.objects.get(fbid=fbid)
                buyer.current_state = 'DEFAULT'
                buyer.save()
                self.text_message(fbid, 'Jollof Chat ended.')
            buyer = Profile.objects.get(fbid=fbid)
            msg = 'ID: ' + str(buyer.pk) + '. ' + buyer.user.first_name + ' ' + buyer.user.last_name + '. MSG: ' + original 
            headers = {
                'Content-Type': 'application/json; charset=utf-8',         
            }
            params = (
                ('access_token', self.BUYER_ACCESS_TOKEN),
            )
            data = {"recipient": {"id": str(self.BLUMAN_ID)},"message": {"text": str(msg)}}
            data = json.dumps(data).encode("utf-8")
            response = requests.post('https://graph.facebook.com/v2.6/me/messages', headers=headers, params=params, data=data)
            pprint(response.json())


    def talk_to_jollof(self, fbid, text):
        if text == 'TALK_TO_JOLLOF':
            if fbid == self.BLUMAN_ID:
                return self.text_message(fbid, 'Sorry fam, you can not be chatting with yourself.')
            buyer = Profile.objects.get(fbid=fbid)
            buyer.current_state = 'TALK_TO_JOLLOF'
            buyer.save()
            self.text_message(fbid, 'Send Done to end the conversation.')
            self.text_message(fbid, 'Hey {{user_first_name}}, what\'s up? 😏')
            return
        self.jollof_chat(fbid, text)
        return
    

    def get_jollof_location(self, fbid, payload, location_title=None, location_url=None, location_lat=None, location_long=None):
        if payload == 'CANCELLED':
            self.cancel_action(fbid, payload)
            return
        elif location_lat:
            # save location_lat and location_long
            buyer = Profile.objects.get(fbid=fbid)
            buyer.longitude = float(location_long)
            buyer.latitude = float(location_lat)
            buyer.current_state = 'DEFAULT'
            prev_locations = str(buyer.location_history)
            if prev_locations == '':
                buyer.location_history = str(location_lat) + ',' + str(location_long) #try to add the datetime too
            else:
                buyer.location_history = prev_locations + '\t' + str(location_lat) + ',' + str(location_long) #try to add the datetime here too.
            buyer.save()       
            self.text_message(fbid, 'Searching for nearby Jollof!🔎')
            # Pass lat and long to function that will retrieve nearest sellers
            sellers = Profile.objects.filter(user_type='s')
            if sellers.count() < 1:
                self.text_message(fbid, 'I am working very hard to find the best places for you to find Jollof around you. I will let you know when you can find them, thank you.')
            else:
                generic_sellers = '{"recipient":{"id":"'+str(fbid)+'"},"message":{"attachment":{"type":"template","payload":{"template_type":"generic","elements":['
                generic_ending = ']}}}}'
                generic_elements = ''
                places_found = False
                for seller in sellers:
                    if seller.longitude != 0.0 and seller.latitude != 0.0:
                        distance = self.get_distance((location_lat,location_long), (seller.latitude, seller.longitude))
                        if distance <= self.NEAREST_KM:
                            # gather restaurant location here and build generic template.
                            seller_jollof = None
                            try:
                                seller_jollof = Jollof.objects.get(seller=seller.pk)
                            except Jollof.DoesNotExist:
                                continue
                            if seller_jollof.available is False:
                                continue
                            places_found = True
                            #  img_link = 'http://via.placeholder.com/350x350'
                            img_link = str(seller_jollof.image.url)
                            try:
                                img_link = img_link[:int(img_link.index('?'))]
                            except:
                                pass
                            generic_title = seller.restaurant + ' Jollof at N' + str(seller_jollof.price)
                            generic_subtitle = seller_jollof.description
                            order_payload = 'JOLLOF_QUANTITY_' + str(seller_jollof.pk)
                            reservation_payload = 'JOLLOF_RESERVATION_' + str(seller_jollof.pk)
                            generic_elements += '{"title":"'+str(generic_title)+'","image_url":"'+str(img_link)+'","subtitle":"'+str(generic_subtitle)+'.","buttons":[{"type":"postback","title":"Order for Delivery 🚚","payload":"'+str(order_payload)+'"},{"type":"postback","payload":"'+str(reservation_payload)+'","title":"Make Reservation🍽"}]},'      
                if places_found:
                    #Remove trailing comma
                    generic_elements = generic_elements[:-1]
                    if len(generic_elements) > 0:
                        data = generic_sellers + generic_elements + generic_ending
                        pprint('Generic message: ' + data)
                        data = json.dumps(json.loads(data)).encode('utf-8')
                        headers = {
                            'Content-Type': 'application/json; charset=utf-8',
                        }
                        params = (
                            ('access_token', self.BUYER_ACCESS_TOKEN),
                        )
                        response = requests.post('https://graph.facebook.com/v2.6/me/messages', headers=headers, params=params, data=data)
                        pprint(response.json())
                else:
                    self.text_message(fbid, 'I cannot smell jollof near you ☹ I am working hard to find the best Jollof place close to you.') 
                    future_location = FutureLocation(fbid=buyer.fbid, latitude=float(location_lat), longitude=float(location_long))
                    future_location.save()
            return
        self.request_location(fbid)
        buyer = Profile.objects.get(fbid=fbid)
        buyer.current_state = 'GET_LOCATION_JOLLOF'
        buyer.save()

    
    def make_jollof_reservation(self, fbid, payload):
        if 'JOLLOF_RESERVATION' in payload:
            # reconfirm the distance between the buyer and the seller here first.
            jollof_id = int(payload[19:])
            jollof = Jollof.objects.get(pk=jollof_id)
            seller = Profile.objects.get(pk=(int(jollof.seller.pk)))
            buyer = Profile.objects.get(fbid=fbid)
            distance = self.get_distance((buyer.latitude,buyer.longitude), (seller.latitude, seller.longitude))
            if distance > self.NEAREST_KM:
                # buyer no longer in proximity
                msg = 'Sorry {{user_first_name}}, you are no longer near ' + seller.restaurant + '. Say jollof! to find new places near you. 👍'
                self.text_message(fbid, msg)
                return
            # Place order for jollof here  
            order_code = self.generate_order_code()
            jollof_order = JollofOrder(code=order_code, jollof_buyer=buyer, jollof_seller=seller, jollof=jollof, order_type=1)
            jollof_order.save()
            # and notify the seller of the reservation.
            msg = 'You have a new jollof reservation!🎉🎉🎉'
            self.text_seller(seller.fbid, msg)
            headers = {
                'Content-Type': 'application/json; charset=utf-8',
            }
            params = (
                ('access_token', os.environ.get('SELLER_ACCESS_TOKEN')),
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
                    "text":"Name: FULL_NAME. Order Code: ORDER_CODE. JOLLOF_INFO",
                    "buttons":[
                    {
                        "type":"postback",
                        "title":"Accept Reservation",
                        "payload":"ACCEPT_RESERVATION"
                    },
                    {
                        "type":"postback",
                        "title":"Reject Reservation",
                        "payload":"REJECT_RESERVATION"
                    }
                    ]
                }
                }
            }
            }'''
            data = data.replace('FULL_NAME', buyer.user.first_name + ' ' + buyer.user.last_name)
            data = data.replace('USER_ID', seller.fbid)
            data = data.replace('ORDER_CODE', jollof_order.code)
            data = data.replace('ACCEPT_RESERVATION', 'JOLLOF_PENDING_RESERVATIONS_' + str(jollof_order.pk) + '_1')
            data = data.replace('REJECT_RESERVATION', 'JOLLOF_PENDING_RESERVATIONS_' + str(jollof_order.pk) + '_2')
            data = data.replace('JOLLOF_INFO', jollof.description)
            pprint(str(data))
            data = json.dumps(json.loads(data)).encode('utf-8')
            response = requests.post('https://graph.facebook.com/v2.6/me/messages', headers=headers, params=params, data=data)
            pprint(response.json())
            # Buyer can cancel anytime before the reservation is accepted.
            msg = 'Great {{user_first_name}}, I have reserved a table for you at ' + seller.restaurant + '. You will get to dine on the N' + str(jollof.price) + ' Jollof.'
            self.text_message(fbid, msg)
            msg = 'Your reservation code is ' + order_code + '. Please show them when you get there.'
            self.text_message(fbid, msg) 
            msg ='If the restaurant has not accepted your reservation yet, you can send cancel to... well, cancel the reservation.'
            self.text_message(fbid, msg)
                      
            headers = {
                'Content-Type': 'application/json; charset=utf-8',
            }
            params = (
                ('access_token', self.BUYER_ACCESS_TOKEN),
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
                    "text":"Don\'t know where SELLER is?",
                    "buttons":[
                    {
                        "type":"web_url",
                        "title":"Get Directions ↗",
                        "url":"DIRECTIONS"
                    }
                    ]
                }
                }
            }
            }'''
            data = data.replace('DIRECTIONS', self.get_directions(buyer.latitude, buyer.longitude, seller.latitude, seller.longitude))
            data = data.replace('USER_ID', fbid)
            data = data.replace('SELLER', seller.restaurant)
            pprint(str(data))
            data = json.dumps(json.loads(data)).encode('utf-8')
            response = requests.post('https://graph.facebook.com/v2.6/me/messages', headers=headers, params=params, data=data)
            pprint(response.json())
            #Alert me of the reservation made here.
            buyer = Profile.objects.get(fbid=fbid)
            buyer.current_state = 'DEFAULT'
            buyer.has_order = True
            buyer.save()

    
    def get_jollof_quantity(self, fbid, payload):
        if payload == 'CANCELLED':
            self.cancel_action(fbid, payload)
            return
        elif 'JOLLOF_QUANTITY' in payload:
            # reconfirm the distance between the buyer and the seller here first.
            pprint(payload)
            jollof_id = int(payload[16:])
            jollof_data = jollof_id.split('_')
            if len(jollof_data) == 2:
                pprint('Qty sent. Ordering Jollof Now')
                self.order_jollof(fbid, payload)
                return
            jollof = Jollof.objects.get(pk=jollof_id)
            seller = Profile.objects.get(pk=int(jollof.seller.pk))
            buyer = Profile.objects.get(fbid=fbid)
            distance = self.get_distance((buyer.latitude,buyer.longitude), (seller.latitude, seller.longitude))
            if distance > self.NEAREST_KM:
                # buyer no longer in proximity
                msg = 'Sorry {{user_first_name}}, you are no longer near ' + seller.restaurant + '. Say jollof! to find new places near you. 👍'
                self.text_message(fbid, msg)
                return
            # Ask for quantity here
            data = '''{
            "recipient":{
                "id":"USER_ID"
            },
            "message":{
                "text": "So how much of it should I get for you?",
                "quick_replies":[
                {
                    "content_type":"text",
                    "title":"1",
                    "payload":"JOLLOF_QUANTITY_JID_1"
                },
                {
                    "content_type":"text",
                    "title":"2",
                    "payload":"JOLLOF_QUANTITY_JID_2"
                },
                {
                    "content_type":"text",
                    "title":"3",
                    "payload":"JOLLOF_QUANTITY_JID_3"
                },
                {
                    "content_type":"text",
                    "title":"4",
                    "payload":"JOLLOF_QUANTITY_JID_4"
                },
                {
                    "content_type":"text",
                    "title":"5",
                    "payload":"JOLLOF_QUANTITY_JID_5"
                },
                {
                    "content_type":"text",
                    "title":"Cancel",
                    "payload":"CANCELLED"
                }
                ]
            }
            }
            '''
            data = data.replace('USER_ID', seller.fbid)
            data = data.replace('JID', str(jollof_id))
            pprint(str(data))
            data = json.dumps(json.loads(data)).encode('utf-8')
            response = requests.post('https://graph.facebook.com/v2.6/me/messages', headers=headers, params=params, data=data)
            buyer = Profile.objects.get(fbid=fbid)
            buyer.current_state = 'JOLLOF_QUANTITY'
            buyer.save()
            return


    def order_jollof(self, fbid, payload):
        if payload == 'CANCELLED':
            self.cancel_action(fbid, payload)
            return
        elif 'JOLLOF_QUANTITY' in payload:
            jollof_id_qty = int(payload[16:])
            jollof_data = jollof_id_qty.split('_')
            jollof_id = int(jollof_data[0])
            jollof_quantity = int(jollof_data[1])
            jollof = Jollof.objects.get(pk=jollof_id)
            seller = Profile.objects.get(pk=int(jollof.seller.pk))
            buyer = Profile.objects.get(fbid=fbid)
            # Place order for jollof here
            order_code = self.generate_order_code()
            jollof_order = JollofOrder(code=order_code, jollof_buyer=buyer, jollof_seller=seller, quantity=jollof_quantity, jollof=jollof, order_type=2)
            jollof_order.save()
            # and notify the seller.
            msg = 'You have a new jollof delivery order!🎉🎉🎉'
            self.text_seller(seller.fbid, msg)
            headers = {
                'Content-Type': 'application/json; charset=utf-8',
            }
            params = (
                ('access_token', os.environ.get('SELLER_ACCESS_TOKEN')),
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
                    "text":"Name: FULL_NAME. Order Code: ORDER_CODE. Qty: QUANTITY. JOLLOF_INFO",
                    "buttons":[
                    {
                        "type":"postback",
                        "title":"Accept Deliv. Order",
                        "payload":"ACCEPT_ORDER"
                    },
                    {
                        "type":"postback",
                        "title":"Reject Deliv. Order",
                        "payload":"REJECT_ORDER"
                    }
                    ]
                }
                }
            }
            }'''
            data = data.replace('FULL_NAME', buyer.user.first_name + ' ' + buyer.user.last_name)
            data = data.replace('USER_ID', seller.fbid)
            data = data.replace('ORDER_CODE', jollof_order.code)
            data = data.replace('QUANTITY', str(jollof_quantity))
            data = data.replace('ACCEPT_ORDER', 'JOLLOF_PENDING_DELIVERIES_' + str(jollof_order.pk) + '_1')
            data = data.replace('REJECT_ORDER', 'JOLLOF_PENDING_DELIVERIES_' + str(jollof_order.pk) + '_2')
            data = data.replace('JOLLOF_INFO', str(jollof_quantity) + ' plate of ' + jollof.description)
            pprint(str(data))
            data = json.dumps(json.loads(data)).encode('utf-8')
            response = requests.post('https://graph.facebook.com/v2.6/me/messages', headers=headers, params=params, data=data)
            pprint('Jollof Order Sent: ' + str(response.json()['message_id']))
            # Buyer can cancel anytime before the order is accepted.
            msg = 'Great {{user_first_name}}, I have ordered ' + str(jollof_quantity) + ' plate of the irresistible N'+str(jollof.price)+' Jollof by '+seller.restaurant+' for you. You will get to pay on delivery. Your order code is ' + jollof_order.code
            self.text_message(fbid, msg)
            msg ='If the restaurant has not accepted your order yet, you can send cancel to... well, cancel the order.'
            self.text_message(fbid, msg)
            #Alert me of the order made here.
            buyer = Profile.objects.get(fbid=fbid)
            buyer.current_state = 'DEFAULT'
            buyer.has_order = True
            buyer.save()
            return


    def get_delicacy_location(self, fbid, payload, location_title=None, location_url=None, location_lat=None, location_long=None):
        if payload == 'CANCELLED':
            self.cancel_action(fbid, payload)
            return
        elif location_lat:
            # save location_lat and location_long
            buyer = Profile.objects.get(fbid=fbid)
            buyer.longitude = float(location_long)
            buyer.latitude = float(location_lat)
            print('Lat: ' + str(float(location_lat)) + ' Long: ' + str(float(location_long)))
            buyer.current_state = 'DEFAULT'
            prev_locations = str(buyer.location_history)
            if prev_locations == '':
                buyer.location_history = str(location_lat) + ',' + str(location_long) #try to add the datetime too
            else:
                buyer.location_history = prev_locations + '\t' + str(location_lat) + ',' + str(location_long) #try to add the datetime here too.
            buyer.save()       
            self.text_message(fbid, 'Searching for nearby delicacies!🔎')
            # Pass lat and long to function that will retrieve nearest sellers
            sellers = Profile.objects.filter(user_type='s')
            if sellers.count() < 1:
                self.text_message(fbid, 'I am working very hard to find the best places for you to find awesome delicacies. I will let you know when you can find them, thank you.')
            else:
                generic_sellers = '{"recipient":{"id":"'+str(fbid)+'"},"message":{"attachment":{"type":"template","payload":{"template_type":"generic","elements":['
                generic_ending = ']}}}}'
                generic_elements = ''
                places_found = False
                for seller in sellers:
                    if seller.longitude != 0.0 and seller.latitude != 0.0:
                        distance = self.get_distance((location_lat,location_long), (seller.latitude, seller.longitude))
                        if distance <= self.NEAREST_KM:
                            # gather restaurant location here and build generic template.
                            seller_delicacy = Delicacy.objects.filter(seller=seller)
                            if seller_delicacy.count() < 1:
                                continue
                            places_found = True
                            #img_link = 'http://via.placeholder.com/350x350'
                            img_link = str(seller.logo.url)
                            try:
                                img_link = img_link[:int(img_link.index('?'))]
                            except:
                                pass
                            generic_title = seller.restaurant
                            generic_subtitle = seller.phone_number
                            generic_payload = 'VIEW_DELICACY_SELLERS_' + str(seller.pk)
                            generic_elements += '{"title":"'+str(generic_title)+'","image_url":"'+str(img_link)+'","subtitle":"'+str(generic_subtitle)+'.","buttons":[{"type":"postback","title":"View Delicacies","payload":"'+str(generic_payload)+'"},{"type":"web_url","url":"'+self.get_directions(buyer.latitude, buyer.longitude, seller.latitude, seller.longitude)+'","title":"Get Directions"}]},'  
                if places_found:
                    #Remove trailing comma
                    generic_elements = generic_elements[:-1]
                    if len(generic_elements) > 0:
                        data = generic_sellers + generic_elements + generic_ending
                        print('Generic message: ' + data)
                        data = json.dumps(json.loads(data)).encode('utf-8')
                        headers = {
                            'Content-Type': 'application/json; charset=utf-8',
                        }
                        params = (
                            ('access_token', self.BUYER_ACCESS_TOKEN),
                        )
                        response = requests.post('https://graph.facebook.com/v2.6/me/messages', headers=headers, params=params, data=data)
                        pprint(response.json())
                else:
                    self.text_message(fbid, 'I cannot smell delicacies near you ☹ I am working hard to find the best places close to you.') # Ask to increase search radius
            return
        self.request_location(fbid)
        buyer = Profile.objects.get(fbid=fbid)
        buyer.current_state = 'GET_LOCATION_DELICACY'
        buyer.save()
    

    def view_delicacy_sellers(self, fbid, payload):
        if 'VIEW_DELICACY_SELLERS' in payload:
            # reconfirm proximity to seller first
            seller_id = int(payload[22:])
            seller = Profile.objects.get(pk=seller_id)
            buyer = Profile.objects.get(fbid=fbid)
            distance = self.get_distance((buyer.latitude,buyer.longitude), (seller.latitude, seller.longitude))
            if distance > self.NEAREST_KM:
                # buyer no longer in proximity
                msg = 'Sorry {{user_first_name}}, you are no longer near ' + seller.restaurant + '. Say jollof! to find new places near you. 👍'
                self.text_message(fbid, msg)
                return
            # show sellers delicacies
            delicacies = Delicacy.objects.filter(seller=int(seller.pk)).filter(available=True)
            if delicacies.count() < 1:
                self.text_message(fbid, seller.restaurant + ' does not have delicacies right now :( Please try another restaurant nearby.')
            else:
                generic_sellers = '{"recipient":{"id":"'+str(fbid)+'"},"message":{"attachment":{"type":"template","payload":{"template_type":"generic","elements":['
                generic_ending = ']}}}}'
                generic_elements = ''
                for delicacy in delicacies:
                    #img_link = 'http://via.placeholder.com/350x350'
                    img_link = str(delicacy.image.url)
                    try:
                        img_link = img_link[:int(img_link.index('?'))]
                    except:
                        pass
                    generic_title = str(delicacy.price)
                    generic_subtitle = delicacy.description
                    order_payload = 'ORDER_DELICACY_' + str(delicacy.pk)
                    reservation_payload = 'DELICACY_RESERVATION_' + str(delicacy.pk)
                    generic_elements += '{"title":"'+str(generic_title)+'","image_url":"'+str(img_link)+'","subtitle":"'+str(generic_subtitle)+'.","buttons":[{"type":"postback","title":"Order for Delivery 🚚","payload":"'+str(order_payload)+'"},{"type":"postback","title":"Make Reservation🍽","payload":"'+str(reservation_payload)+'"}]},'
                #Remove trailing comma
                generic_elements = generic_elements[:-1]
                data = generic_sellers + generic_elements + generic_ending
                print('Generic message: ' + data)
                data = json.dumps(json.loads(data)).encode('utf-8')
                headers = {
                    'Content-Type': 'application/json; charset=utf-8',
                }
                params = (
                    ('access_token', self.BUYER_ACCESS_TOKEN),
                )
                response = requests.post('https://graph.facebook.com/v2.6/me/messages', headers=headers, params=params, data=generic_message)
                pprint(response.json())

    
    def make_delicacy_reservation(self, fbid, payload):
        if 'DELICACY_RESERVATION' in payload:
            # reconfirm the distance between the buyer and the seller here first.
            delicacy_id = int(payload[21:])
            delicacy = Delicacy.objects.get(pk=delicacy_id)
            seller = Profile.objects.get(pk=int(delicacy.seller.pk))
            buyer = Profile.objects.get(fbid=fbid)
            distance = self.get_distance((buyer.latitude,buyer.longitude), (seller.latitude, seller.longitude))
            if distance > self.NEAREST_KM:
                # buyer no longer in proximity
                msg = 'Sorry {{user_first_name}}, you are no longer near ' + seller.restaurant + '. Say jollof! to find new places near you. 👍'
                self.text_message(fbid, msg)
                return
            # Place order for delicacy here  
            order_code = self.generate_order_code()
            delicacy_order = DelicacyOrder(code=order_code, delicacy_buyer=buyer, delicacy_seller=seller, delicacy=delicacy, order_type=1)
            delicacy_order.save()
            # and notify the seller.
            msg = 'You have a new delicacy reservation!🎉🎉🎉'
            self.text_seller(seller.fbid, msg)
            headers = {
                'Content-Type': 'application/json; charset=utf-8',
            }
            params = (
                ('access_token', os.environ.get('SELLER_ACCESS_TOKEN')),
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
                    "text":"Name: FULL_NAME. Order Code: ORDER_CODE. DELICACY_INFO",
                    "buttons":[
                    {
                        "type":"postback",
                        "title":"Accept Reservation",
                        "payload":"ACCEPT_RESERVATION"
                    },
                    {
                        "type":"postback",
                        "title":"Reject Reservation",
                        "payload":"REJECT_RESERVATION"
                    }
                    ]
                }
                }
            }
            }'''
            data = data.replace('FULL_NAME', buyer.user.first_name + ' ' + buyer.user.last_name)
            data = data.replace('USER_ID', seller.fbid)
            data = data.replace('ORDER_CODE', delicacy_order.code)
            data = data.replace('ACCEPT_RESERVATION', 'DELICACY_PENDING_DELIVERIES_' + str(delicacy_order.pk) + '_1')
            data = data.replace('REJECT_RESERVATION', 'DELICACY_PENDING_DELIVERIES_' + str(delicacy_order.pk) + '_2')
            data = data.replace('DELICACY_INFO', delicacy.description)
            pprint(str(data))
            data = json.dumps(json.loads(data)).encode('utf-8')
            response = requests.post('https://graph.facebook.com/v2.6/me/messages', headers=headers, params=params, data=data)
            pprint(response.json())
            # Buyer can cancel anytime before the reservation is accepted.
            msg = 'Great {{user_first_name}}, I have reserved a table for you at ' + seller.restaurant + '. You will get to dine on the N'+str(delicacy.price)+ ' ' + delicacy.name + ' :D'
            self.text_message(fbid, msg)
            msg = 'Your reservation code is ' + order_code + '. Please show them when you get there.'
            self.text_message(fbid, msg)
            msg ='If the restaurant has not accepted your reservation yet, you can send cancel to... well, cancel the reservation.'
            self.text_message(fbid, msg)           
            headers = {
                'Content-Type': 'application/json; charset=utf-8',
            }
            params = (
                ('access_token', self.BUYER_ACCESS_TOKEN),
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
                    "text":"Don\'t know where SELLER is?",
                    "buttons":[
                    {
                        "type":"web_url",
                        "title":"Get Directions ↗",
                        "url":"DIRECTIONS"
                    }
                    ]
                }
                }
            }
            }'''
            data = data.replace('DIRECTIONS', self.get_directions(buyer.latitude, buyer.longitude, seller.latitude, seller.longitude))
            data = data.replace('USER_ID', fbid)
            data = data.replace('SELLER', seller.restaurant)
            pprint(str(data))
            data = json.dumps(json.loads(data)).encode('utf-8')
            response = requests.post('https://graph.facebook.com/v2.6/me/messages', headers=headers, params=params, data=data)
            pprint(response.json())
            #Alert me of the reservation made here.
            buyer = Profile.objects.get(fbid=fbid)
            buyer.current_state = 'DEFAULT'
            buyer.has_order = True
            buyer.save()


    def order_delicacy(self, fbid, payload):
        if 'ORDER_DELICACY' in payload:
            # reconfirm the distance between the buyer and the seller here first.
            delicacy_id = int(payload[15:])
            delicacy = Delicacy.objects.get(pk=delicacy_id)
            seller = Profile.objects.get(pk=int(delicacy.seller.pk))
            buyer = Profile.objects.get(fbid=fbid)
            distance = self.get_distance((buyer.latitude,buyer.longitude), (seller.latitude, seller.longitude))
            if distance > self.NEAREST_KM:
                # buyer no longer in proximity
                msg = 'Sorry {{user_first_name}}, you are no longer near ' + seller.restaurant + '. Say jollof! to find new places near you. 👍'
                self.text_message(fbid, msg)
                return
            # Place order for delicacy here  
            order_code = self.generate_order_code()
            delicacy_order = DelicacyOrder(code=order_code, delicacy_buyer=buyer, delicacy_seller=seller, delicacy=delicacy, order_type=2)
            delicacy_order.save()
            # and notify the seller.
            msg = 'You have a new delicacy delivery order!🎉🎉🎉'
            self.text_seller(seller.fbid, msg)
            headers = {
                'Content-Type': 'application/json; charset=utf-8',
            }
            params = (
                ('access_token', os.environ.get('SELLER_ACCESS_TOKEN')),
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
                    "text":"Name: FULL_NAME. Order Code: ORDER_CODE. DELICACY_INFO",
                    "buttons":[
                    {
                        "type":"postback",
                        "title":"Accept Deliv. Order",
                        "payload":"ACCEPT_ORDER"
                    },
                    {
                        "type":"postback",
                        "title":"Reject Deliv. Order",
                        "payload":"REJECT_ORDER"
                    }
                    ]
                }
                }
            }
            }'''
            data = data.replace('FULL_NAME', buyer.user.first_name + ' ' + buyer.user.last_name)
            data = data.replace('USER_ID', seller.fbid)
            data = data.replace('ORDER_CODE', delicacy_order.code)
            data = data.replace('ACCEPT_ORDER', 'DELICACY_PENDING_DELIVERIES_' + str(delicacy_order.pk) + '_1')
            data = data.replace('REJECT_ORDER', 'DELICACY_PENDING_DELIVERIES_' + str(delicacy_order.pk) + '_2')
            data = data.replace('DELICACY_INFO', delicacy.description)
            pprint(str(data))
            data = json.dumps(json.loads(data)).encode('utf-8')
            response = requests.post('https://graph.facebook.com/v2.6/me/messages', headers=headers, params=params, data=data)
            pprint(response.json())
            # Buyer can cancel anytime before the order is accepted.
            msg = 'Great {{user_first_name}}, I have ordered the sumptuous N'+str(delicacy.price)+' '+str(delicacy.name)+' by '+seller.restaurant+' for you. You will get to pay on delivery. You will definitely love this :D'
            self.text_message(fbid, msg)
            msg ='If the restaurant has not accepted your order yet, you can send cancel to... well, cancel the order.'
            self.text_message(fbid, msg)
            # Alert me of the order made here.
            buyer = Profile.objects.get(fbid=fbid)
            buyer.current_state = 'DEFAULT'
            buyer.has_order = True
            buyer.save()
            

    def order_status(self, fbid):
        buyer = Profile.objects.get(fbid=fbid)
        # if there are more than one orders that are not cancelled or delivered, we should show them all and let them choose the order to show status for.
        # a cancelled order is a complete order.
        if buyer.has_order:
            jollof_orders = JollofOrder.objects.filter(jollof_buyer=buyer)
            if jollof_orders.count() == 1:
                #single order, show status directly
                pass
            elif jollof_orders.count() > 1:
                #show all jollof orders statuses in a generic horizontal list
                for jollof_order in jollof_orders:
                    if jollof_order.status < 4:
                        # we have orders that have not been delivered. prolly cancelled or rejected.
                        pass


