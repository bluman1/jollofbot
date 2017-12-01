import os
import re
import requests
import json
import random
import string
import geopy.distance
from pprint import pprint

from jollof.models import *


class Deliver(object):

    def __init__(self):
        self.DELIVER_ACCESS_TOKEN = os.environ.get('DELIVER_ACCESS_TOKEN')
        self.BUYER_ACCESS_TOKEN = os.environ.get('BUYER_ACCESS_TOKEN')
        self.SELLER_ACCESS_TOKEN = os.environ.get('SELLER_ACCESS_TOKEN')
        self.BLUMAN_ID = os.environ.get('BLUMAN_ID')
        self.NEAREST_KM = os.environ.get('NEAREST_KM')

    def get_started_button(self):
        pprint('Get Started Button')
        headers = {
            'Content-Type': 'application/json',
        }
        params = (
            ('access_token', self.DELIVER_ACCESS_TOKEN),
        )
        data = '{"get_started":{"payload":"GET_STARTED"}}'
        response = requests.post('https://graph.facebook.com/v2.6/me/messenger_profile',
                    headers=headers, params=params, data=data)
        pprint(response.json())

    def persistent_menu(self):
        pprint('Persistent Menu')
        headers = {
            'Content-Type': 'application/json',
        }
        params = (
            ('access_token', self.DELIVER_ACCESS_TOKEN),
        )
        data = """{
            "persistent_menu":[
                {
                    "locale":"default",
                    "composer_input_disabled":false,
                    "call_to_actions":[
                        {
                        "title":"Available Orders",
                        "type":"nested",
                        "call_to_actions":[
                            {
                                "title":"Pending Orders",
                                "type":"postback",
                                "payload":"PENDING_ORDERS"
                            },
                            {
                                "title":"To Pickup",
                                "type":"postback",
                                "payload":"TO_PICKUP"
                            },
                            {
                                "title":"To Drop Off",
                                "type":"postback",
                                "payload":"TO_DROPOFF"
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

    def get_distance(self, coords1, coords2):
        distance = geopy.distance.vincenty(coords1, coords2).km
        pprint('Distance: ' + str(distance))
        return distance

    def get_directions(self, origin_lat, origin_long, dest_lat, dest_long):
        return 'https://www.google.com/maps/dir/' + str(origin_lat) + ',' + str(origin_long) + '/' + str(dest_lat) + ',' + str(dest_long) + '/'

    def parse_phone(self, phone):
        ''' A valid Nigerian phone number.  
        08012345678 - 11 digits starts with 0, network=80,81,70,90, followed by 8 digits
        +2348012345678 - 13 digits with +, code=234, network=80,81,70,90, followed by 8 digits
        0112345678 - 10 digits starts with 01, followed by 8 digits
        '''
        network_operators = ['80', '81', '70', '90', '01']
        phone_len = len(phone)
        if phone_len == 14 and phone.startswith('+234') and phone[4:6] in network_operators:
            # +2348012345678
            return True
        if phone_len == 11 and phone.startswith('0') and phone[1:3] in network_operators:
            # 08012345678
            return True
        if phone_len == 10 and phone.startswith('01'):
            # 0112345678
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
        return

    def get_user_details(self, fbid):
        user_details_url = "https://graph.facebook.com/v2.6/%s"%fbid
        user_details_params = {'fields':'first_name,last_name,profile_pic', 'access_token':self.DELIVER_ACCESS_TOKEN}
        user_details = requests.get(user_details_url, user_details_params).json()
        return user_details

    def alert_me(self, fbid, alert_type):
        my_fbid = self.BLUMAN_ID
        if alert_type == 1:
            flash = Flash.objects.get(fbid=fbid)

            msg = 'New Flash - ' + flash.first_name + ' ' + flash.last_name + ' just became a Jollof Flash. FBID = ' + str(fbid) + '.'
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
        return

    def text_message(self, fbid, msg):
        try:
            flash = Flash.objects.get(fbid=fbid)
            if '{{user_first_name}}' in msg:
                msg = msg.replace('{{user_first_name}}', flash.first_name)
        except:
            pass
        pprint(msg)
        headers = {
            'Content-Type': 'application/json; charset=utf-8',         
        }
        params = (
            ('access_token', self.DELIVER_ACCESS_TOKEN),
        )
        data = {"recipient": {"id": str(fbid)}, "message": {"text": str(msg)}}
        data = json.dumps(data).encode("utf-8")
        response = requests.post('https://graph.facebook.com/v2.6/me/messages', headers=headers, params=params, data=data)
        pprint(response.json())
        return

    def text_seller_message(self, fbid, msg):
        pprint(msg)
        headers = {
            'Content-Type': 'application/json; charset=utf-8',         
        }
        params = (
            ('access_token', self.SELLER_ACCESS_TOKEN),
        )
        data = {"recipient": {"id": str(fbid)},"message": {"text": str(msg)}}
        data = json.dumps(data).encode("utf-8")
        response = requests.post('https://graph.facebook.com/v2.6/me/messages', headers=headers, params=params, data=data)
        pprint(response.json())
        return

    def text_buyer_message(self, fbid, msg):
        pprint(msg)
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
        return
    
    def cancel_action(self, fbid, payload):
        flash = Flash.objects.get(fbid=fbid)
        flash.current_state = 'DEFAULT'
        flash.save()
        msg = 'I\'ve cancelled that action.'
        self.text_message(fbid, msg)
        return

    def request_phone(self, fbid, text):
        flash = Flash.objects.get(fbid=fbid)
        phone = self.parse_phone(text.strip())
        if not phone:
            msg = 'Ugh mehn, that phone number doesn\'t look right 🤦. Please enter a valid Nigerian Phone Number. e.g 08031234567'
            self.text_message(fbid, msg)
            return
        flash.phone_number = text.strip()
        flash.current_state = 'DEFAULT'
        flash.save()
        msg = 'Woot woot!💃💃💃 We can now share your number with a client when a delivery is to be made.'
        self.text_message(fbid, msg)
        return

    def request_location(self, fbid):
        headers = {
            'Content-Type': 'application/json',
        }
        params = (
            ('access_token', self.DELIVER_ACCESS_TOKEN),
        )
        data = '{"recipient":{"id":"' + str(fbid) + '"},"message":{"text":"Please share your location with me.","quick_replies":[{"content_type":"location"},{"content_type":"text","title":"Cancel","payload":"CANCELLED"}]}}'
        response = requests.post('https://graph.facebook.com/v2.6/me/messages', headers=headers, params=params, data=data)
        pprint(response.json())
        return

    def save_location(self, fbid, payload, location_title=None, location_url=None, location_lat=None, location_long=None):
        if payload == 'CANCELLED':
            self.cancel_action(fbid, payload)
        elif location_lat:
            # save location_lat and location_long
            flash = Flash.objects.get(fbid=fbid)
            flash.longitude = float(location_long)
            flash.latitude = float(location_lat)
            print('Lat: ' + str(float(location_lat)) + ' Long: ' + str(float(location_long)))
            msg = None
            if flash.phone_number == '0':
                flash.current_state = 'REQUEST_PHONE'
                msg = 'Now to the final step. Please share your phone number e.g. 08031234567'
            else:
                flash.current_state = 'DEFAULT'
            flash.save()       
            self.text_message(fbid, 'Great! Now I can direct you from your location to delivery point!')
            if msg is not None:
                self.text_message(fbid, msg)            
        return

    def process_code(self, fbid, flash_code):
        master_flash = Flash.objects.filter(flash_code=flash_code)
        if master_flash.count() < 1:
            pprint('Wrong code entered.')
            msg = 'Sorry, the FlashCode you entered is incorrect. Please double check and enter again.'
            self.text_message(fbid, msg)
            return
        msg = ''
        try:
            flash = Flash.objects.get(fbid=fbid)
            flash.flash_code = flash_code
            flash.save()
            msg = 'Welcome back!'
        except Flash.DoesNotExist:
            user_details = self.get_user_details(fbid)
            pprint(user_details)
            flash = Flash(fbid=fbid, flash_code=flash_code, first_name=user_details['first_name'], last_name=user_details['last_name'], current_state='FLASH_LOCATION')
            flash.save()
            msg = 'Great to have you here. On to the next step, your location.'
        self.text_message(fbid, msg)
        self.request_location(fbid)
        return

    def pending_orders(self, fbid, payload):
        self.text_message(fbid, 'Searching for pending orders.')
        flash = Flash.objects.get(fbid=fbid)
        all_pending_jollof_orders = JollofOrder.objects.filter(status=1).filter(order_type=2)
        pending_jollof_orders = []
        for pending_jollof_order in all_pending_jollof_orders:
            # filter orders by nearest buyer location
            distance = self.get_distance((flash.latitude, flash.longitude), (pending_jollof_order.jollof_buyer.latitude, pending_jollof_order.jollof_buyer.longitude))
            if distance >= float(self.NEAREST_KM):
                # buyer not in range.
                continue
            pending_jollof_orders.append(pending_jollof_order)
        all_pending_delicacy_orders = DelicacyOrder.objects.filter(status=1).filter(order_type=2)
        pending_delicacy_orders = []
        for pending_delicacy_order in all_pending_delicacy_orders:
            # filter orders by nearest buyer location
            distance = self.get_distance((flash.latitude, flash.longitude), (pending_delicacy_order.delicacy_buyer.latitude, pending_delicacy_order.delicacy_buyer.longitude))
            if distance >= float(self.NEAREST_KM):
                # buyer not in range.
                continue
            pending_delicacy_orders.append(pending_delicacy_order)
        if len(pending_delicacy_orders) + len(pending_jollof_orders) < 1:
            #  Flash has no pending order
            msg = 'There are no pending orders for you to deliver for now. Don\'t worry, I\'ll notify you once an order is available :)'
            self.text_message(fbid, msg)
            return
        self.text_message(fbid, 'Great! Found some pending orders close to you.')
        if pending_jollof_orders:
            jollof_orders = '{"recipient":{"id":"'+str(fbid)+'"},"message":{"attachment":{"type":"template","payload":{"template_type":"generic","elements":['
            jollof_ending = ']}}}}'
            jollof_elements = ''
            limit = 0
            for pending_jollof in pending_jollof_orders:
                if limit > 8:
                    break
                limit += 1
                img_link = str(pending_jollof.jollof_seller.logo.url)
                try:
                    img_link = img_link[:int(img_link.index('?'))]
                except:
                    pass
                generic_title = 'Jollof delivery from ' + pending_jollof.jollof_seller.restaurant + ' to ' + pending_jollof.jollof_buyer.first_name + '.'
                generic_subtitle = pending_jollof.jollof.description + '\nOrder Code: ' + pending_jollof.code + '.'
                accept_jollof = 'ACCEPT_PENDING_JOLLOF_' + str(pending_jollof.pk)
                jollof_elements += '{"title":"'+str(generic_title)+'","image_url":"'+str(img_link)+'","subtitle":"'+str(generic_subtitle)+'.","buttons":[{"type":"postback","title":"Accept To Deliver","payload":"'+str(accept_jollof)+'"}]},'
            if jollof_elements:
                jollof_elements = jollof_elements[:-1]
                data = jollof_orders + jollof_elements + jollof_ending
                pprint('Jollof Pending Message: ' + data)
                data = json.dumps(json.loads(data)).encode('utf-8')
                headers = {
                    'Content-Type': 'application/json; charset=utf-8',
                }
                params = (
                    ('access_token', self.DELIVER_ACCESS_TOKEN),
                )
                response = requests.post('https://graph.facebook.com/v2.6/me/messages', headers=headers, params=params, data=data)
                pprint(response.json())
        if pending_delicacy_orders:
            delicacy_orders = '{"recipient":{"id":"'+str(fbid)+'"},"message":{"attachment":{"type":"template","payload":{"template_type":"generic","elements":['
            delicacy_ending = ']}}}}'
            delicacy_elements = ''
            limit = 0
            for pending_delicacy in pending_delicacy_orders:
                if limit > 8:
                    break
                limit += 1
                img_link = str(pending_delicacy.delicacy_seller.logo.url)
                try:
                    img_link = img_link[:int(img_link.index('?'))]
                except:
                    pass
                generic_title = 'Delicacy delivery from ' + pending_delicacy.delicacy_seller.restaurant + ' to ' + pending_delicacy.delicacy_buyer.first_name + '.'
                generic_subtitle = pending_delicacy.delicacy.description + '\nOrder Code: ' + pending_delicacy.code + '.'
                accept_delicacy = 'ACCEPT_PENDING_DELICACY_' + str(pending_delicacy.pk)
                delicacy_elements += '{"title":"'+str(generic_title)+'","image_url":"'+str(img_link)+'","subtitle":"'+str(generic_subtitle)+'.","buttons":[{"type":"postback","title":"Accept To Deliver","payload":"'+str(accept_delicacy)+'"}]},'
            if delicacy_elements:
                delicacy_elements = delicacy_elements[:-1]
                data = jollof_orders + delicacy_elements + delicacy_ending
                pprint('Delicacy Pending Message: ' + data)
                data = json.dumps(json.loads(data)).encode('utf-8')
                headers = {
                    'Content-Type': 'application/json; charset=utf-8',
                }
                params = (
                    ('access_token', self.DELIVER_ACCESS_TOKEN),
                )
                response = requests.post('https://graph.facebook.com/v2.6/me/messages', headers=headers, params=params, data=data)
                pprint(response.json())
        return

    def accept_pending_jollof(self, fbid, payload):
        flash = Flash.objects.get(fbid=fbid)
        jollof_order_id = int(payload[22:])
        jollof_order = JollofOrder.objects.get(pk=jollof_order_id)
        if jollof_order.flash_status != 0:
            msg = 'Sorry, another Flash got to this order before you did. You gotta be faster next time!'
            self.text_message(fbid, msg)
            return
        if jollof_order.flash_status == 1:
            msg = 'You have already accepted this order. Go forth and pick it up!'
            self.text_message(fbid, msg)
            return
        check_accepted = JollofOrder.objects.filter(flash=flash).filter(flash_status=1)
        check_picked_up = JollofOrder.objects.filter(flash=flash).filter(flash_status=3)
        if check_accepted.count() > 0:
            msg = 'Sorry, you need to deliver the order you accepted before accepting a new one.'
            self.text_message(fbid, msg)
            return
        if check_picked_up.count() > 0:
            msg = 'Sorry, you need to deliver the order you just picked up before accepting a new one.'
            self.text_message(fbid, msg)
            return
        directions_to_restaurant = self.get_directions(flash.latitude, flash.longitude, jollof_order.jollof_seller.latitude, jollof_order.jollof_seller.longitude)
        jollof_order.flash = flash
        jollof_order.flash_status = 1
        jollof_order.save()
        msg = 'Great, you have accepted to deliver this order. Be swift, Be Flash!'
        self.text_message(fbid, msg)
        headers = {
            'Content-Type': 'application/json',
        }
        params = (
            ('access_token', self.DELIVER_ACCESS_TOKEN),
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
                "text":"Pick up ORDER_DETAILS at RESTAURANT. Order Code: ORDER_CODE",
                "buttons":[
                {
                    "type":"web_url",
                    "title":"Get Directions",
                    "url":"DIRECTIONS"
                },
                {
                    "type":"postback",
                    "title":"Mark As Picked Up",
                    "payload":"PICKED_UP"
                }
                ]
            }
            }
        }
        }'''
        data = data.replace('ORDER_DETAILS', jollof_order.jollof.description)
        data = data.replace('USER_ID', fbid)
        data = data.replace('ORDER_CODE', jollof_order.code)
        data = data.replace('DIRECTIONS', directions_to_restaurant)
        data = data.replace('RESTAURANT', jollof_order.jollof_seller.restaurant)
        data = data.replace('PICKED_UP', 'PICKED_UP_JOLLOF_' + str(jollof_order.pk))
        pprint(str(data))
        response = requests.post('https://graph.facebook.com/v2.6/me/messages', headers=headers, params=params, data=data)
        pprint('Notified Flash')
        pprint(response.json())
        msg = 'Hey there! A Flash has accepted to deliver ' + jollof_order.jollof_buyer.first_name + '\'s order of ' + jollof_order.jollof.description + ' with order code ' + jollof_order.code +'.'
        self.text_seller_message(jollof_order.jollof_seller.fbid, msg)
        msg = "Our Flash's name is " + flash.first_name + " " + flash.last_name + ". Remember to confirm the order code with him before handing over the package."
        self.text_seller_message(jollof_order.jollof_seller.fbid, msg)
        pprint('Notified Restaurant')
        msg = 'Woot woot! Our very own Flash has gone to pick up your order! He will be there sooooon...'
        self.text_buyer_message(jollof_order.jollof_buyer.fbid, msg)
        pprint('Notified Buyer')
        return

    def accept_pending_delicacy(self, fbid, payload):
        flash = Flash.objects.get(fbid=fbid)
        delicacy_order_id = int(payload[24:])
        delicacy_order = DelicacyOrder.objects.get(pk=jollof_order_id)
        if delicacy_order.flash_status != 0:
            msg = 'Sorry, another Flash got to this order before you did. You gotta be faster next time!'
            self.text_message(fbid, msg)
            return
        if delicacy_order.flash_status == 1:
            msg = 'You have already accepted this order. Go forth and pick it up!'
            self.text_message(fbid, msg)
            return
        check_accepted = DelicacyOrder.objects.filter(flash=flash).filter(flash_status=1)
        check_picked_up = DelicacyOrder.objects.filter(flash=flash).filter(flash_status=3)
        if check_accepted.count() > 0:
            msg = 'Sorry, you need to deliver the order you accepted before accepting a new one.'
            self.text_message(fbid, msg)
            return
        if check_picked_up.count() > 0:
            msg = 'Sorry, you need to deliver the order you just picked up before accepting a new one.'
            self.text_message(fbid, msg)
            return
        directions_to_restaurant = self.get_directions(flash.latitude, flash.longitude, delicacy_order.delicacy_seller.latitude, delicacy_order.delicacy_seller.longitude)
        delicacy_order.flash = flash
        delicacy_order.flash_status = 1
        delicacy_order.save()
        msg = 'Great, you have accepted to deliver this order. Here is the direction to the restaurant. Be swift, Be Flash!'
        self.text_message(fbid, msg)
        headers = {
            'Content-Type': 'application/json',
        }
        params = (
            ('access_token', self.DELIVER_ACCESS_TOKEN),
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
                "text":"Pick up ORDER_DETAILS at RESTAURANT. Order Code: ORDER_CODE",
                "buttons":[
                {
                    "type":"web_url",
                    "title":"Get Directions",
                    "url":"DIRECTIONS"
                },
                {
                    "type":"postback",
                    "title":"Mark As Picked Up",
                    "payload":"PICKED_UP"
                }
                ]
            }
            }
        }
        }'''
        data = data.replace('ORDER_DETAILS', delicacy_order.jollof.description)
        data = data.replace('USER_ID', fbid)
        data = data.replace('ORDER_CODE', delicacy_order.code)
        data = data.replace('DIRECTIONS', directions_to_restaurant)
        data = data.replace('RESTAURANT', delicacy_order.delicacy_seller.restaurant)
        data = data.replace('PICKED_UP', 'PICKED_UP_DELICACY_' + str(delicacy_order.pk))
        pprint(str(data))
        response = requests.post('https://graph.facebook.com/v2.6/me/messages', headers=headers, params=params, data=data)
        msg = 'Please remember to save your new location when you get to the restaurant so that I will be able to direct you to ' + delicacy_order.delicacy_buyer.first_name + 's location. Just send "location"'
        self.text_message(fbid, msg)
        pprint('Notified Flash')
        pprint(response.json())
        msg = 'Hey there! A Flash has accepted to deliver ' + delicacy_order.delicacy_buyer.first_name + '\'s order of ' + delicacy_order.delicacy.description + ' with order code ' + delicacy_order.code +'.'
        self.text_seller_message(delicacy_order.delicacy_seller.fbid, msg)
        msg = "Our Flash's name is " + flash.first_name + " " + flash.last_name + ". Remember to confirm the order code with him before handing over the package."
        self.text_seller_message(delicacy_order.delicacy_seller.fbid, msg)
        pprint('Notified Restaurant')
        msg = 'Woot woot! Our very own Flash has gone to pick up your order! He will be there sooooon...'
        self.text_buyer_message(delicacy_order.delicacy_buyer.fbid, msg)
        pprint('Notified Buyer')
        return

    def to_pickup(self, fbid, payload):
        self.text_message(fbid, 'Searching for orders to pick up.')
        flash = Flash.objects.get(fbid=fbid)
        all_pickup_jollof_orders = JollofOrder.objects.filter(flash_status=1).filter(order_type=2)
        pickup_jollof_orders = []
        for pickup_jollof_order in all_pickup_jollof_orders:
            pending_jollof_orders.append(pending_jollof_order)
        all_pickup_delicacy_orders = DelicacyOrder.objects.filter(flash_status=1).filter(order_type=2)
        pickup_delicacy_orders = []
        for pickup_delicacy_order in all_pickup_delicacy_orders:
            pending_delicacy_orders.append(pending_delicacy_order)
        if len(pending_delicacy_orders) + len(pending_jollof_orders) < 1:
            #  Flash has no order to pickup
            msg = 'There are no orders to pick up right now. Accept some orders and then you can go pick them up :)'
            self.text_message(fbid, msg)
            return
        self.text_message(fbid, 'Great! Found some orders you have to pick up.')
        if pickup_jollof_orders:
            jollof_orders = '{"recipient":{"id":"'+str(fbid)+'"},"message":{"attachment":{"type":"template","payload":{"template_type":"generic","elements":['
            jollof_ending = ']}}}}'
            jollof_elements = ''
            limit = 0
            for pickup_jollof in pickup_jollof_orders:
                if limit > 8:
                    break
                limit += 1
                img_link = str(pickup_jollof.jollof_seller.logo.url)
                try:
                    img_link = img_link[:int(img_link.index('?'))]
                except:
                    pass
                generic_title = 'Jollof delivery from ' + pickup_jollof.jollof_seller.restaurant + ' to ' + pickup_jollof.jollof_buyer.first_name + '.'
                generic_subtitle = pickup_jollof.jollof.description + '\
                nOrder Code: ' + pickup_jollof.code + '.'
                accept_jollof = 'PICKED_UP_JOLLOF_' + str(pickup_jollof.pk)
                jollof_elements += '{"title":"'+str(generic_title)+'","image_url":"'+str(img_link)+'","subtitle":"'+str(generic_subtitle)+'.","buttons":[{"type":"postback","title":"Mark As Picked Up","payload":"'+str(accept_jollof)+'"}]},'
            if jollof_elements:
                jollof_elements = jollof_elements[:-1]
                data = jollof_orders + jollof_elements + jollof_ending
                pprint('Jollof Pick Up Message: ' + data)
                data = json.dumps(json.loads(data)).encode('utf-8')
                headers = {
                    'Content-Type': 'application/json; charset=utf-8',
                }
                params = (
                    ('access_token', self.DELIVER_ACCESS_TOKEN),
                )
                response = requests.post('https://graph.facebook.com/v2.6/me/messages', headers=headers, params=params, data=data)
                pprint(response.json())
        if pickup_delicacy_orders:
            delicacy_orders = '{"recipient":{"id":"'+str(fbid)+'"},"message":{"attachment":{"type":"template","payload":{"template_type":"generic","elements":['
            delicacy_ending = ']}}}}'
            delicacy_elements = ''
            limit = 0
            for pickup_delicacy in pickup_delicacy_orders:
                if limit > 8:
                    break
                limit += 1
                img_link = str(pickup_delicacy.delicacy_seller.logo.url)
                try:
                    img_link = img_link[:int(img_link.index('?'))]
                except:
                    pass
                generic_title = 'Delicacy delivery from ' + pickup_delicacy.delicacy_seller.restaurant + ' to ' + pickup_delicacy.delicacy_buyer.first_name + '.'
                generic_subtitle = pickup_delicacy.delicacy.description + '\nOrder Code: ' + pickup_delicacy.code + '.'
                accept_delicacy = 'PICKED_UP_DELICACY_' + str(pickup_delicacy.pk)
                delicacy_elements += '{"title":"'+str(generic_title)+'","image_url":"'+str(img_link)+'","subtitle":"'+str(generic_subtitle)+'.","buttons":[{"type":"postback","title":"Mark As Picked Up","payload":"'+str(accept_delicacy)+'"}]},'
            if delicacy_elements:
                delicacy_elements = delicacy_elements[:-1]
                data = jollof_orders + delicacy_elements + delicacy_ending
                pprint('Delicacy Pick Up Message: ' + data)
                data = json.dumps(json.loads(data)).encode('utf-8')
                headers = {
                    'Content-Type': 'application/json; charset=utf-8',
                }
                params = (
                    ('access_token', self.DELIVER_ACCESS_TOKEN),
                )
                response = requests.post('https://graph.facebook.com/v2.6/me/messages', headers=headers, params=params, data=data)
                pprint(response.json())
        return

    def picked_up_jollof(self, fbid, payload):
        flash = Flash.objects.get(fbid=fbid)
        jollof_order_id = int(payload[17:])
        jollof_order = JollofOrder.objects.get(pk=jollof_order_id)
        if jollof_order.flash_status == 3:
            msg = 'You have already picked up this order. Go forth and deliver it!'
            self.text_message(fbid, msg)
            return
        check_picked_up = JollofOrder.objects.filter(flash=flash).filter(flash_status=3)
        if check_picked_up.count() > 0:
            msg = 'Sorry, you need to deliver the order you just picked up before picking up another.'
            self.text_message(fbid, msg)
            return
        directions_to_buyer = self.get_directions(flash.latitude, flash.longitude, jollof_order.jollof_buyer.latitude, jollof_order.jollof_buyer.longitude)
        jollof_order.flash_status = 3
        jollof_order.save()
        msg = 'Great, now to deliver this order. Be swift, Be Flash!'
        self.text_message(fbid, msg)
        headers = {
            'Content-Type': 'application/json',
        }
        params = (
            ('access_token', self.DELIVER_ACCESS_TOKEN),
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
                "text":"Deliver ORDER_DETAILS to BUYER. Order Code: ORDER_CODE",
                "buttons":[
                {
                    "type":"web_url",
                    "title":"Get Directions",
                    "url":"DIRECTIONS"
                },
                {
                    "type":"postback",
                    "title":"Mark As Delivered",
                    "payload":"DROPPED_OFF_JOLLOF"
                }
                ]
            }
            }
        }
        }'''
        data = data.replace('ORDER_DETAILS', jollof_order.jollof.description)
        data = data.replace('USER_ID', fbid)
        data = data.replace('ORDER_CODE', jollof_order.code)
        data = data.replace('DIRECTIONS', directions_to_buyer)
        data = data.replace('BUYER', jollof_order.jollof_buyer.first_name + ' ' + jollof_order.jollof_buyer.last_name)
        data = data.replace('DROPPED_OFF_JOLLOF', 'DROPPED_OFF_JOLLOF_' + str(jollof_order.pk))
        pprint(str(data))
        response = requests.post('https://graph.facebook.com/v2.6/me/messages', headers=headers, params=params, data=data)
        pprint('Notified Flash')
        pprint(response.json())
        msg = 'Hey hey! Thank you for the prompt service. Flash has gone to deliver the beauty you prepared.'
        self.text_seller_message(jollof_order.jollof_seller.fbid, msg)
        pprint('Notified Restaurant')
        msg = 'Hey hey! Flash has picked up your order and he is on his way to you right now! Be prepared...'
        self.text_buyer_message(jollof_order.jollof_buyer.fbid, msg)
        pprint('Notified Buyer')
        return

    def picked_up_delicacy(self, fbid, payload):
        flash = Flash.objects.get(fbid=fbid)
        delicacy_order_id = int(payload[19:])
        delicacy_order = DelicacyOrder.objects.get(pk=delicacy_order_id)
        if delicacy_order.flash_status == 3:
            msg = 'You have already picked up this order. Go forth and deliver it!'
            self.text_message(fbid, msg)
            return
        check_picked_up = DelicacyOrder.objects.filter(flash=flash).filter(flash_status=3)
        if check_picked_up.count() > 0:
            msg = 'Sorry, you need to deliver the order you just picked up before picking up another.'
            self.text_message(fbid, msg)
            return
        directions_to_buyer = self.get_directions(flash.latitude, flash.longitude, delicacy_order.delicacy_buyer.latitude, delicacy_order.delicacy_buyer.longitude)
        delicacy_order.flash_status = 3
        delicacy_order.save()
        msg = 'Great, now to deliver this order. Be swift, Be Flash!'
        self.text_message(fbid, msg)
        headers = {
            'Content-Type': 'application/json',
        }
        params = (
            ('access_token', self.DELIVER_ACCESS_TOKEN),
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
                "text":"Deliver ORDER_DETAILS to BUYER. Order Code: ORDER_CODE",
                "buttons":[
                {
                    "type":"web_url",
                    "title":"Get Directions",
                    "url":"DIRECTIONS"
                },
                {
                    "type":"postback",
                    "title":"Mark As Delivered",
                    "payload":"DROPPED_OFF_DELICACY"
                }
                ]
            }
            }
        }
        }'''
        data = data.replace('ORDER_DETAILS', delicacy_order.delicacy.description)
        data = data.replace('USER_ID', fbid)
        data = data.replace('ORDER_CODE', delicacy_order.code)
        data = data.replace('DIRECTIONS', directions_to_buyer)
        data = data.replace('BUYER', delicacy_order.delicacy_buyer.first_name + ' ' + delicacy_order.delicacy_buyer.last_name)
        data = data.replace('DROPPED_OFF_DELICACY', 'DROPPED_OFF_DELICACY_' + str(delicacy_order.pk))
        pprint(str(data))
        response = requests.post('https://graph.facebook.com/v2.6/me/messages', headers=headers, params=params, data=data)
        pprint('Notified Flash')
        pprint(response.json())
        msg = 'Hey hey! Thank you for the prompt service. Flash has gone to deliver the beauty you prepared.'
        self.text_seller_message(delicacy_order.delicacy_seller.fbid, msg)
        pprint('Notified Restaurant')
        msg = 'Hey hey! Flash has picked up your order and he is on his way to you right now! Be prepared...'
        self.text_buyer_message(delicacy_order.delicacy_buyer.fbid, msg)
        pprint('Notified Buyer')
        return

    def to_dropoff(self, fbid, payload):
        self.text_message(fbid, 'Searching for orders to drop off.')
        flash = Flash.objects.get(fbid=fbid)
        all_dropoff_jollof_orders = JollofOrder.objects.filter(flash_status=3).filter(order_type=2)
        dropoff_jollof_orders = []
        for dropoff_jollof_order in all_dropoff_jollof_orders:
            dropoff_jollof_orders.append(dropoff_jollof_order)
        all_dropoff_delicacy_orders = DelicacyOrder.objects.filter(flash_status=3).filter(order_type=2)
        dropoff_delicacy_orders = []
        for dropoff_delicacy_order in all_dropoff_delicacy_orders:
            dropoff_delicacy_orders.append(dropoff_delicacy_order)
        if len(dropoff_delicacy_orders) + len(dropoff_jollof_orders) < 1:
            #  Flash has no order to dropoff
            msg = 'There are no orders to drop off right now. Pick up some orders and then you can go drop them off :)'
            self.text_message(fbid, msg)
            return
        self.text_message(fbid, 'Great! Found some orders you have to drop off.')
        if dropoff_jollof_orders:
            jollof_orders = '{"recipient":{"id":"'+str(fbid)+'"},"message":{"attachment":{"type":"template","payload":{"template_type":"generic","elements":['
            jollof_ending = ']}}}}'
            jollof_elements = ''
            limit = 0
            for dropoff_jollof in dropoff_jollof_orders:
                if limit > 8:
                    break
                limit += 1
                img_link = str(dropoff_jollof.jollof_seller.logo.url)
                try:
                    img_link = img_link[:int(img_link.index('?'))]
                except:
                    pass
                generic_title = 'Jollof delivery from ' + dropoff_jollof.jollof_seller.restaurant + ' to ' + dropoff_jollof.jollof_buyer.first_name + '.'
                generic_subtitle = dropoff_jollof.jollof.description + '\
                nOrder Code: ' + dropoff_jollof.code + '.'
                accept_jollof = 'DROPPED_OFF_JOLLOF_' + str(dropoff_jollof.pk)
                jollof_elements += '{"title":"'+str(generic_title)+'","image_url":"'+str(img_link)+'","subtitle":"'+str(generic_subtitle)+'.","buttons":[{"type":"postback","title":"Mark As Dropped Off","payload":"'+str(accept_jollof)+'"}]},'
            if jollof_elements:
                jollof_elements = jollof_elements[:-1]
                data = jollof_orders + jollof_elements + jollof_ending
                pprint('Jollof Pick Up Message: ' + data)
                data = json.dumps(json.loads(data)).encode('utf-8')
                headers = {
                    'Content-Type': 'application/json; charset=utf-8',
                }
                params = (
                    ('access_token', self.DELIVER_ACCESS_TOKEN),
                )
                response = requests.post('https://graph.facebook.com/v2.6/me/messages', headers=headers, params=params, data=data)
                pprint(response.json())
        if dropoff_delicacy_orders:
            delicacy_orders = '{"recipient":{"id":"'+str(fbid)+'"},"message":{"attachment":{"type":"template","payload":{"template_type":"generic","elements":['
            delicacy_ending = ']}}}}'
            delicacy_elements = ''
            limit = 0
            for dropoff_delicacy in dropoff_delicacy_orders:
                if limit > 8:
                    break
                limit += 1
                img_link = str(dropoff_delicacy.delicacy_seller.logo.url)
                try:
                    img_link = img_link[:int(img_link.index('?'))]
                except:
                    pass
                generic_title = 'Delicacy delivery from ' + dropoff_delicacy.delicacy_seller.restaurant + ' to ' + dropoff_delicacy.delicacy_buyer.first_name + '.'
                generic_subtitle = dropoff_delicacy.delicacy.description + '\nOrder Code: ' + dropoff_delicacy.code + '.'
                accept_delicacy = 'DROPPED_OFF_DELICACY_' + str(dropoff_delicacy.pk)
                delicacy_elements += '{"title":"'+str(generic_title)+'","image_url":"'+str(img_link)+'","subtitle":"'+str(generic_subtitle)+'.","buttons":[{"type":"postback","title":"Mark As Picked Up","payload":"'+str(accept_delicacy)+'"}]},'
            if delicacy_elements:
                delicacy_elements = delicacy_elements[:-1]
                data = jollof_orders + delicacy_elements + delicacy_ending
                pprint('Delicacy Pick Up Message: ' + data)
                data = json.dumps(json.loads(data)).encode('utf-8')
                headers = {
                    'Content-Type': 'application/json; charset=utf-8',
                }
                params = (
                    ('access_token', self.DELIVER_ACCESS_TOKEN),
                )
                response = requests.post('https://graph.facebook.com/v2.6/me/messages', headers=headers, params=params, data=data)
                pprint(response.json())
        return

    def dropped_off_jollof(self, fbid, payload):
        flash = Flash.objects.get(fbid=fbid)
        jollof_order_id = int(payload[19:])
        jollof_order = JollofOrder.objects.get(pk=jollof_order_id)
        if jollof_order.flash_status == 4:
            msg = 'You have already dropped off this order.'
            self.text_message(fbid, msg)
            return
        jollof_order.flash_status = 4
        jollof_order.save()
        msg = 'You were swift, you are Flash ⚡'
        self.text_message(fbid, msg)
        msg = 'Touch down! I hope you enjoy the delectable meal you ordered. What do you think of ther service?'
        self.text_buyer_message(jollof_order.jollof_buyer.fbid, msg)
        pprint('Notified Buyer')
        return

    def dropped_off_delicacy(self, fbid, payload):
        flash = Flash.objects.get(fbid=fbid)
        delicacy_order_id = int(payload[21:])
        delicacy_order = DelicacyOrder.objects.get(pk=delicacy_order_id)
        if delicacy_order.flash_status == 4:
            msg = 'You have already dropped off this order.'
            self.text_message(fbid, msg)
            return
        delicacy_order.flash_status = 4
        delicacy_order.save()
        msg = 'You were swift, you are Flash ⚡'
        self.text_message(fbid, msg)
        msg = 'Touch down! I hope you enjoy the delectable meal you ordered. What do you think of ther service?'
        self.text_buyer_message(jollof_order.jollof_buyer.fbid, msg)
        pprint('Notified Buyer')
        return
