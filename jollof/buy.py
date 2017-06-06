import os
import requests
import json
import random
import string
import geopy.distance
from pprint import pprint

from jollof.models import *


class Buy():

    BUYER_ACCESS_TOKEN = os.environ.get('BUYER_ACCESS_TOKEN')
    BLUMAN_ID = os.environ.get('BLUMAN_ID')
    NEAREST_KM = 1
    
    def __init__(self):
        pass

    
    def get_distance(self, coords1, coords2):
        # coords_1 = (52.2296756, 21.0122287) lat,long
        # coords_2 = (52.406374, 16.9251681) lat,long
        return geopy.distance.vincenty(coords1, coords2).km

    
    def generate_order_code(self):
        return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(6))
    

    def generate_jollof_code(self):
        return 'JOLLOF-' ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(3))


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
            buyer = Buyer.objects.get(fbid=fbid)

            msg = 'New User - ' + buyer.first_name + ' ' + buyer.last_name + ' just became a Jollof Buyer. FBID = ' + str(fbid) + '.'
            headers = {
                'Content-Type': 'application/json',
            }
            params = (
                ('access_token', self.BUYER_ACCESS_TOKEN),
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
                ('access_token', self.BUYER_ACCESS_TOKEN),
            )
            data = '{"recipient": {"id": "'+str(my_fbid)+'"},"message": {"text": "'+str(msg)+'"}}'
            pprint(str(data))
            response = requests.post('https://graph.facebook.com/v2.6/me/messages', headers=headers, params=params, data=data)
            pprint(response.json())


    def text_message(self, fbid, msg):
        buyer = Buyer.objects.get(fbid=fbid)
        if '{{user_first_name}}' in msg:
            msg = msg.replace('{{user_first_name}}', buyer.first_name)
        print(msg)
        headers = {
            'Content-Type': 'application/json',
        }
        params = (
            ('access_token', self.BUYER_ACCESS_TOKEN),
        )
        data = '{"recipient": {"id": "'+str(fbid)+'"},"message": {"text": "'+str(msg)+'"}}'
        pprint(str(data))
        response = requests.post('https://graph.facebook.com/v2.6/me/messages', headers=headers, params=params, data=data)
        pprint(response.json())


    def greet_buyer(self, fbid):
        msg = 'Hi {{user_first_name}}, I am JollofBot. I can help you find the nearest place where you can buy #NigerianJollof. You can either have it delivered to you right where you are or get directions to the best Jollof you\'ll ever have!'
        self.text_message(fbid, msg)
        headers = {
            'Content-Type': 'application/json',
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
                    "title":"I want Jollof!",
                    "payload":"GET_LOCATION_JOLLOF"
                },
                {
                    "type":"postback",
                    "title":"Nigerian delicacies!",
                    "payload":"GET_LOCATION_DELICACY"
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


    def cancel_action(self, fbid, payload):
        buyer = Buyer.objects.get(fbid=fbid)
        buyer.current_state = 'DEFAULT'
        buyer.save()
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


    def get_jollof_location(self, fbid, payload, location_title=None, location_url=None, location_lat=None, location_long=None):
        if payload == 'CANCELLED':
            self.cancel_action(fbid, payload)
            return
        elif location_lat:
            # save location_lat and location_long
            buyer = Buyer.objects.get(fbid=fbid)
            buyer.longitude = float(location_long)
            buyer.latitude = float(location_lat)
            print('Lat: ' + str(float(location_lat)) + ' Long: ' + str(float(location_long)))
            buyer.current_state = 'DEFAULT'
            buyer.save()       
            self.text_message(fbid, 'You are at ' + str(location_title) + '.')
            self.text_message(fbid, 'Searching for nearby Jollof!')
            # Pass lat and long to function that will retrieve nearest sellers
            sellers = Seller.objects.all()
            if sellers.count() < 1:
                self.text_message(fbid, 'I am working very hard to find the best places for you to find Jollof. I will let you know when you can find them, thank you.')
            else:
                generic_sellers = '{"recipient":{"id":"'+str(fbid)+'"},"message":{"attachment":{"type":"template","payload":{"template_type":"generic","elements":['
                generic_ending = ']}}}}'
                generic_elements = ''
                places_found = False
                for seller in sellers:
                    if seller.longitude != 0.0 and seller.latitude != 0.0:
                        distance = self.get_distance((location_lat,location_long), (seller.latitude, seller.longitude))
                        if distance <= self.NEAREST_KM:
                            places_found = True
                            # gather restaurant location here and build generic template.
                            seller_jollof = Jollof.objects.get(seller=seller.pk)
                            if seller_jollof.count() < 1:
                                continue
                            seller_jollof = seller_jollof[0]
                            imgur_link = 'http://i.imgur.com/' + ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(7)) + '.jpg'
                            print('Random Imgur Link: ' + imgur_link)
                            generic_title = seller.restaurant + ' jollof at N' + seller_jollof.price
                            generic_subtitle = seller_jollof.description
                            generic_payload = 'ORDER_JOLLOF_' + seller_jollof.pk
                            generic_elements += '{"title":"'+str(generic_title)+'","image_url":"'+str(imgur_link)+'","subtitle":"'+str(generic_subtitle)+'.","buttons":[{"type":"postback","title":"Order for Delivery","payload":"'+str(generic_payload)+'"},{"type":"web_url","url":"http://jollofbot.tk","title":"Get Directions"}]},'
                            #TODO: get gmaps link for directions, retrieve restaurants logo from url                 
                if places_found:
                    self.text_message(fbid, 'I can smell jollof near you! But I can not show them now :(')
                    #Remove trailing comma
                    generic_elements = generic_elements[:-1]
                    if len(generic_elements) > 0:
                        generic_message = generic_sellers + generic_elements + generic_ending
                        print('Generic message: ' + generic_message)
                        headers = {
                            'Content-Type': 'application/json',
                        }
                        params = (
                            ('access_token', self.BUYER_ACCESS_TOKEN),
                        )
                        response = requests.post('https://graph.facebook.com/v2.6/me/messages', headers=headers, params=params, data=generic_message)
                        print(response.json())
                else:
                    self.text_message(fbid, 'I cannot smell jollof near you :(') # Ask to increase search radius
            return
        self.request_location(fbid)
        buyer = Buyer.objects.get(fbid=fbid)
        buyer.current_state = 'GET_LOCATION_JOLLOF'
        buyer.save()


    def get_delicacy_location(self, fbid, payload, location_title=None, location_url=None, location_lat=None, location_long=None):
        if payload == 'CANCELLED':
            self.cancel_action(fbid, payload)
            return
        elif location_lat:
            # save location_lat and location_long
            buyer = Buyer.objects.get(fbid=fbid)
            buyer.longitude = float(location_long)
            buyer.latitude = float(location_lat)
            print('Lat: ' + str(float(location_lat)) + ' Long: ' + str(float(location_long)))
            buyer.current_state = 'DEFAULT'
            buyer.save()       
            self.text_message(fbid, 'You are at ' + str(location_title) + '.')
            self.text_message(fbid, 'Searching for nearby delicacies!')
            # Pass lat and long to function that will retrieve nearest sellers
            sellers = Seller.objects.all()
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
                            places_found = True
                            # gather restaurant location here and build generic template.
                            seller_delicacy = Delicacy.objects.get(seller=seller.pk)
                            if seller_delicacy.count() < 1:
                                continue
                            imgur_link = 'http://i.imgur.com/' + ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(7)) + '.jpg'
                            print('Random Imgur Link: ' + imgur_link)
                            generic_title = seller.restaurant
                            generic_subtitle = seller.phone_number
                            generic_payload = 'VIEW_DELICACY_SELLERS_' + seller.pk
                            generic_elements += '{"title":"'+str(generic_title)+'","image_url":"'+str(imgur_link)+'","subtitle":"'+str(generic_subtitle)+'.","buttons":[{"type":"postback","title":"Delicacies Available","payload":"'+str(generic_payload)+'"},{"type":"web_url","url":"http://jollofbot.tk","title":"Get Directions"}]},'
                            #TODO: get gmaps link for directions, retrieve restaurants logo from url    
                if places_found:
                    self.text_message(fbid, 'I can smell some nice delicacies near you, but I can\'t show them now :(')
                    #Remove trailing comma
                    generic_elements = generic_elements[:-1]
                    if len(generic_elements) > 0:
                        generic_message = generic_sellers + generic_elements + generic_ending
                        print('Generic message: ' + generic_message)
                        headers = {
                            'Content-Type': 'application/json',
                        }
                        params = (
                            ('access_token', self.BUYER_ACCESS_TOKEN),
                        )
                        response = requests.post('https://graph.facebook.com/v2.6/me/messages', headers=headers, params=params, data=generic_message)
                        print(response.json())
                else:
                    self.text_message(fbid, 'I cannot smell delicacies near you :(') # Ask to increase search radius
            return
        self.request_location(fbid)
        buyer = Buyer.objects.get(fbid=fbid)
        buyer.current_state = 'GET_LOCATION_DELICACY'
        buyer.save()


    def talk_to_jollof(self, fbid, text):
        if text == 'TALK_TO_JOLLOF':
            buyer = Buyer.objects.get(fbid=fbid)
            buyer.current_state = 'TALK_TO_JOLLOF'
            buyer.save()
            self.text_message(fbid, 'Hey {{user_first_name}}, what\'s up? :D')
            self.alert_me(fbid, 'Jollof chat initiated.')
            return
        self.alert_me(fbid, 'Jollof: ' + text)
        self.text_message(fbid, 'Sorry {{user_first_name}}, I do not know how to say a lot yet :(')
        self.greet_buyer(fbid)
        buyer = Buyer.objects.get(fbid=fbid)
        buyer.current_state = 'DEFAULT'
        buyer.save()
        return
    

    def order_jollof(self, fbid, payload):
        if 'ORDER_JOLLOF' in payload:
            # reconfirm the distance between the buyer and the seller here first.
            jollof_id = int(payload[13:])
            jollof = Jollof.objects.get(pk=jollof_id)
            seller = Seller.objects.get(pk=int(jollof.seller.pk))
            buyer = Buyer.objects.get(fbid=fbid)
            distance = self.get_distance((buyer.latitude,buyer.longitude), (seller.latitude, seller.longitude))
            if distance > self.NEAREST_KM:
                # buyer no longer in proximity
                msg = 'Sorry {{user_first_name}}, you are no longer near ' + seller.restaurant + '. Say jollof! to find new places.'
                self.text_message(fbid, msg)
                return
            # Place order for jollof here  
            order_code = self.generate_order_code()
            jollof_order = JollofOrder(code=order_code, jollof_buyer=buyer, jollof_seller=seller, jollof=jollof)
            jollof_order.save()
            # and notify the seller.

            # Buyer can cancel anytime before the order is accepted.
            msg = 'Great {{user_first_name}}, I have ordered the irresistible N'+str(jollof.price)+' Jollof by '+seller.restaurant+' for you. You will get to pay on delivery. You will definitely love this :D'
            self.text_message(fbid, msg)
            msg ='If the restaurant has not accepted your order yet, you can send cancel to... well, cancel the order. You can also send status to track your meal\'s status.'
            self.text_message(fbid, msg)
            #Alert me of the order made here.
            buyer = Buyer.objects.get(fbid=fbid)
            buyer.current_state = 'DEFAULT'
            buyer.has_order = True
            buyer.save()
    

    def view_delicacy_sellers(self, fbid, payload):
        if 'VIEW_DELICACY_SELLERS' in payload:
            # reconfirm proximity to seller first
            seller_id = int(payload[22:])
            seller = Seller.objects.get(pk=seller_id)
            buyer = Buyer.objects.get(fbid=fbid)
            distance = self.get_distance((buyer.latitude,buyer.longitude), (seller.latitude, seller.longitude))
            if distance > self.NEAREST_KM:
                # buyer no longer in proximity
                msg = 'Sorry {{user_first_name}}, you are no longer near ' + seller.restaurant + '. Say jollof! to find new places.'
                self.text_message(fbid, msg)
                return
            # show sellers delicacies
            delicacies = Delicacy.objects.filter(seller=int(seller.pk)).filter(available=True)
            if delicacies.count() < 1:
                self.text_message(fbid, seller.restaurant + ' does not have delicacies right now :( please try another restaurant nearby.')
            else:
                generic_sellers = '{"recipient":{"id":"'+str(fbid)+'"},"message":{"attachment":{"type":"template","payload":{"template_type":"generic","elements":['
                generic_ending = ']}}}}'
                generic_elements = ''
                for delicacy in delicacies:
                    imgur_link = 'http://i.imgur.com/' + ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(7)) + '.jpg'
                    print('Random Imgur Link: ' + imgur_link)
                    generic_title = delicacy.price
                    generic_subtitle = delicacy.description
                    generic_payload = 'ORDER_DELICACY_' + delicacy.pk
                    generic_elements += '{"title":"'+str(generic_title)+'","image_url":"'+str(imgur_link)+'","subtitle":"'+str(generic_subtitle)+'.","buttons":[{"type":"postback","title":"Order","payload":"'+str(generic_payload)+'"},{"type":"web_url","url":"http://jollofbot.tk","title":"Get Directions"}]},'
                    #TODO: get gmaps link for directions, retrieve restaurants logo from url
                #Remove trailing comma
                generic_elements = generic_elements[:-1]
                generic_message = generic_sellers + generic_elements + generic_ending
                print('Generic message: ' + generic_message)
                headers = {
                    'Content-Type': 'application/json',
                }
                params = (
                    ('access_token', self.BUYER_ACCESS_TOKEN),
                )
                response = requests.post('https://graph.facebook.com/v2.6/me/messages', headers=headers, params=params, data=generic_message)
                print(response.json())


    def order_delicacy(self, fbid, payload):
        if 'ORDER_DELICACY' in payload:
            # reconfirm the distance between the buyer and the seller here first.
            delicacy_id = int(payload[13:])
            delicacy = Delicacy.objects.get(pk=delicacy_id)
            seller = Seller.objects.get(pk=int(delicacy.seller.pk))
            buyer = Buyer.objects.get(fbid=fbid)
            distance = self.get_distance((buyer.latitude,buyer.longitude), (seller.latitude, seller.longitude))
            if distance > self.NEAREST_KM:
                # buyer no longer in proximity
                msg = 'Sorry {{user_first_name}}, you are no longer near ' + seller.restaurant + '. Say jollof! to find new places.'
                self.text_message(fbid, msg)
                return
            # Place order for delicacy here  
            order_code = self.generate_order_code()
            delicacy_order = DelicacyOrder(code=order_code, delicacy_buyer=buyer, delicacy_seller=seller, delicacy=delicacy)
            delicacy_order.save()
            # and notify the seller.

            # Buyer can cancel anytime before the order is accepted.
            msg = 'Great {{user_first_name}}, I have ordered the sumptuous N'+str(jollof.price)+' Delicacy by '+seller.restaurant+' for you. You will get to pay on delivery. You will definitely love this :D'
            self.text_message(fbid, msg)
            msg ='If the restaurant has not accepted your order yet, you can send cancel to... well, cancel the order. You can also send status to track your meal\'s status.'
            self.text_message(fbid, msg)
            # Alert me of the order made here.
            buyer = Buyer.objects.get(fbid=fbid)
            buyer.current_state = 'DEFAULT'
            buyer.has_order = True
            buyer.save()
            

    def order_status(self, fbid):
        buyer = Buyer.objects.get(fbid=fbid)
        if buyer.has_order:
            jollof_orders = JollofOrder.objects.filter(jollof_buyer=buyer)
            if jollof_orders.count > 0:
                for jollof_order in jollof_orders:
                    if jollof_order.status < 4:
                        # we have orders that have not been delivered. prolly cancelled or rejected.


