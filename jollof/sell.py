import os
import requests
import json
import geopy.distance
from pprint import pprint

from jollof.models import *


class Sell(object):

    def __init__(self):
        self.SELLER_ACCESS_TOKEN = os.environ.get('SELLER_ACCESS_TOKEN')
        self.DELIVER_ACCESS_TOKEN = os.environ.get('DELIVER_ACCESS_TOKEN')
        self.BUYER_ACCESS_TOKEN = os.environ.get('BUYER_ACCESS_TOKEN')
        self.BLUMAN_ID = os.environ.get('BLUMAN_ID')
        self.NEAREST_KM = os.environ.get('NEAREST_KM')

    
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
                                "title":"Pending Jollof Deliveries",
                                "type":"postback",
                                "payload":"JOLLOF_PENDING_DELIVERIES"
                            },
                            {
                                "title":"Pending Jollof Reservations",
                                "type":"postback",
                                "payload":"JOLLOF_PENDING_RESERVATIONS"
                            },
                            {
                                "title":"Accepted Jollof Deliveries",
                                "type":"postback",
                                "payload":"JOLLOF_ACCEPTED_DELIVERIES"
                            },
                            {
                                "title":"Accepted Jollof Reservations",
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
                                "title":"Pending Delicacy Deliveries",
                                "type":"postback",
                                "payload":"DELICACY_PENDING_DELIVERIES"
                            },
                            {
                                "title":"Pending Delicacy Reservations",
                                "type":"postback",
                                "payload":"DELICACY_PENDING_RESERVATIONS"
                            },
                            {
                                "title":"Accepted Delicacy Deliveries",
                                "type":"postback",
                                "payload":"DELICACY_ACCEPTED_DELIVERIES"
                            },
                            {
                                "title":"Accepted Delicacy Reservations",
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


    def get_distance(self, coords1, coords2):
        distance = geopy.distance.vincenty(coords1, coords2).km
        pprint('Distance: ' + str(distance))
        return distance


    def get_user_details(self, fbid):
        user_details_url = "https://graph.facebook.com/v2.6/%s"%fbid
        user_details_params = {'fields':'first_name,last_name,profile_pic', 'access_token':self.SELLER_ACCESS_TOKEN}
        user_details = requests.get(user_details_url, user_details_params).json()
        return user_details
    
    
    def get_directions(self, origin_lat, origin_long, dest_lat, dest_long):
        return 'https://www.google.com/maps/dir/' + str(origin_lat) + ',' + str(origin_long) + '/' + str(dest_lat) + ',' + str(dest_long) + '/'


    def text_message(self, fbid, msg):
        try:
            seller = Profile.objects.get(fbid=fbid)
            if '{{user_first_name}}' in msg:
                msg = msg.replace('{{user_first_name}}', seller.user.first_name)
        except Profile.DoesNotExist:
            msg = msg.replace('{{user_first_name}}', 'Jollof Creator')
        print(msg)
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
    

    def text_buyer(self, fbid, msg):
        headers = {
            'Content-Type': 'application/json; charset=utf-8',
        }
        params = (
            ('access_token', os.environ.get('BUYER_ACCESS_TOKEN')),
        )
        data = {"recipient": {"id": str(fbid)},"message": {"text": str(msg)}}
        data = json.dumps(data).encode("utf-8")
        response = requests.post('https://graph.facebook.com/v2.6/me/messages', headers=headers, params=params, data=data)
        pprint(response.json())


    def cancel_action(self, fbid, payload):
        seller = Profile.objects.get(fbid=fbid)
        seller.current_state = 'DEFAULT'
        seller.save()
        msg = 'I\'ve cancelled that action.'
        self.text_message(fbid, msg)
    

    def request_location(self, fbid):
        headers = {
            'Content-Type': 'application/json',
        }
        params = (
            ('access_token', self.SELLER_ACCESS_TOKEN),
        )
        data = '{"recipient":{"id":"' + str(fbid) + '"},"message":{"text":"Please share your location with me.","quick_replies":[{"content_type":"location"}]}}'
        response = requests.post('https://graph.facebook.com/v2.6/me/messages', headers=headers, params=params, data=data)
        pprint(response.json())


    def process_code(self, fbid, jollof_code):
        try:
            seller = Profile.objects.get(code=jollof_code)
            seller.fbid = fbid
            seller.current_state = 'VENDOR_LOCATION'
            seller.save()
            msg = 'Nice having you here ' + seller.restaurant + ' :)'
            self.text_message(fbid, msg)
            self.request_location(fbid)
            return
        except Profile.DoesNotExist:
            msg = 'Sorry, the Jollof code you entered is incorrect. Please double check and enter again.'
            self.text_message(fbid, msg)
            return
    

    def save_location(self, fbid, payload, location_title=None, location_url=None, location_lat=None, location_long=None):
        if payload == 'CANCELLED':
            self.cancel_action(fbid, payload)
        elif location_lat:
            # save location_lat and location_long
            seller = Profile.objects.get(fbid=fbid)
            seller.longitude = float(location_long)
            seller.latitude = float(location_lat)
            print('Lat: ' + str(float(location_lat)) + ' Long: ' + str(float(location_long)))
            seller.current_state = 'DEFAULT'
            seller.save()       
            self.text_message(fbid, 'Great! Now you can receive order and reservation updates!')
            self.text_message(fbid, 'Please use the menu options to view pending and accepted orders/reservations.')
        return
    

    def jollof_pending_deliveries(self, fbid, payload):
        if 'JOLLOF_PENDING_DELIVERIES_' in payload:
            seller = Profile.objects.get(fbid=fbid)
            payload_list = payload.split('_')
            jollof_delivery_pk = int(payload_list[3])
            jollof_action = int(payload_list[4])
            jollof_order = JollofOrder.objects.get(pk=jollof_delivery_pk)
            if jollof_action == 1:
                #seller accepted order           
                buyer = Profile.objects.get(pk=int(jollof_order.jollof_buyer.pk))
                if jollof_order.status != 0:
                    msg = 'You can no longer accept this order.'
                    self.text_message(fbid, msg)
                    seller.current_state = 'DEFAULT'
                    seller.save()
                    return
                jollof_order.status = 1
                jollof_order.save()
                msg = 'Great news! ' + seller.restaurant + ' has accepted your order and it has been broadcasted to The Flash. I will let you know once they have picked it up. Remember your order code is ' + jollof_order.code + ' :D'
                self.text_buyer(buyer.fbid, msg)
                seller.current_state = 'DEFAULT'
                seller.save()
                msg = 'You have accepted to deliver ' + buyer.user.first_name + '\'s Jollof and they have been notified.'
                self.text_message(fbid, msg)
                #  broadcast to flash for acceptance
                avalaible_flash = Profile.objects.filter(user_type='f').filter(available=True)
                for flash in avalaible_flash:
                    #  check if flash doesn't have any order to fufill
                    flash_jollof_order = JollofOrder.objects.filter(jollof_flash=flash)
                    flash_busy = False
                    for flash_jollof in flash_jollof_order:
                        if flash_jollof.flash_status > 0 and flash_jollof.flash_status < 4:
                            #  flash is currently busy
                            flash_busy = True
                            break
                    if flash_busy:
                        continue
                    flash_delicacy_order = DelicacyOrder.objects.filter(delicacy_flash=flash)
                    for flash_delicacy in flash_delicacy_order:       
                        if flash_delicacy.flash_status > 0 and flash_delicacy.flash_status < 4:
                            # flash is currently busy
                            flash_busy = True
                            break
                    if flash_busy:
                        continue
                    # flash not busy, check if flash in proximity of restaurant.
                    distance = self.get_distance((flash.latitude, flash.longitude), (jollof_order.jollof_seller.latitude, jollof_order.jollof_seller.longitude))
                    if distance >= float(self.NEAREST_KM):
                        # flash not in range.
                        continue
                    # flash not busy, check if flash in proximity of buyer.
                    distance = self.get_distance((flash.latitude, flash.longitude), (jollof_order.jollof_buyer.latitude, jollof_order.jollof_buyer.longitude))
                    if distance >= float(self.NEAREST_KM):
                        # flash not in range.
                        continue
                    #  flash is free and in range
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
                            "text":"You have a Jollof delivery from REST to FULL_NAME with order code ORDER_CODE. ",
                            "buttons":[
                            {
                                "type":"postback",
                                "title":"Accept To Deliver",
                                "payload":"PAYLOAD"
                            }
                            ]
                        }
                        }
                    }
                    }'''
                    data = data.replace('FULL_NAME', buyer.user.first_name + ' ' + buyer.user.last_name)
                    data = data.replace('USER_ID', flash.fbid)
                    data = data.replace('REST', jollof_order.jollof_seller.restaurant)
                    data = data.replace('ORDER_CODE', jollof_order.code)
                    data = data.replace('PAYLOAD', 'ACCEPT_PENDING_JOLLOF_' + str(jollof_order.pk))
                    pprint(str(data))
                    data = json.dumps(json.loads(data)).encode('utf-8')
                    response = requests.post('https://graph.facebook.com/v2.6/me/messages', headers=headers, params=params, data=data)
                    pprint(response.json())
            elif jollof_action == 2:
                # seller rejected order.
                if jollof_order.status != 0:
                    msg = 'You can no longer reject this order.'
                    self.text_message(fbid, msg)
                    seller.current_state = 'DEFAULT'
                    seller.save()
                    return
                jollof_order.status = 2
                jollof_order.save()
                msg = 'You have rejected the order. I hope all is well with your Jollof.'
                self.text_message(fbid, msg)
                buyer = Profile.objects.get(pk=int(jollof_order.jollof_buyer.pk))
                msg = 'Oh shucks! ' + seller.restaurant + ' will not be able to get you your Jollof :( Just say Jollof! to find other places near you.'
                self.text_buyer(buyer.fbid, msg)            
        else:
            seller = Profile.objects.get(fbid=fbid)
            jollof_orders = JollofOrder.objects.filter(jollof_seller=seller).filter(order_type=2).filter(status=0)
            if jollof_orders.count() < 1:
                msg = 'You have no pending jollof deliveries right now. I will send you updates in real-time.'
                self.text_message(fbid, msg)
            else:
                count = 0
                generic_sellers = '{"recipient":{"id":"'+str(fbid)+'"},"message":{"attachment":{"type":"template","payload":{"template_type":"generic","elements":['
                generic_ending = ']}}}}'
                generic_elements = ''
                for jollof_order in jollof_orders:
                    if count >= 10:
                        break
                    count += 1
                    buyer = Profile.objects.get(pk=int(jollof_order.jollof_buyer.pk))
                    img_link = 'http://via.placeholder.com/350x350'
                    generic_title = buyer.user.first_name + ' wants your Jollof delivered!'
                    generic_subtitle = 'Order Code: ' + jollof_order.code                   
                    accept_order_payload = 'JOLLOF_PENDING_DELIVERIES_' + str(jollof_order.pk) + '_1'
                    reject_order_payload = 'JOLLOF_PENDING_DELIVERIES_' + str(jollof_order.pk) + '_2'
                    generic_elements += '{"title":"'+str(generic_title)+'","image_url":"'+str(img_link)+'","subtitle":"'+str(generic_subtitle)+'.","buttons":[{"type":"postback","title":"Accept Order","payload":"'+str(accept_order_payload)+'"},{"type":"postback","payload":"'+str(reject_order_payload)+'","title":"Reject Order"}]},'
                #Remove trailing comma
                generic_elements = generic_elements[:-1]
                generic_message = generic_sellers + generic_elements + generic_ending
                print('Generic message: ' + generic_message)
                headers = {
                    'Content-Type': 'application/json',
                }
                params = (
                    ('access_token', self.SELLER_ACCESS_TOKEN),
                )
                response = requests.post('https://graph.facebook.com/v2.6/me/messages', headers=headers, params=params, data=generic_message)
                pprint(response.json())
        return
    

    def jollof_pending_reservations(self, fbid, payload):
        if 'JOLLOF_PENDING_RESERVATIONS_' in payload:
            seller = Profile.objects.get(fbid=fbid)
            payload_list = payload.split('_')
            jollof_delivery_pk = int(payload_list[3])
            jollof_action = int(payload_list[4])
            jollof_order = JollofOrder.objects.get(pk=jollof_delivery_pk)
            if jollof_action == 1:
                #seller accepted reservation
                buyer = Profile.objects.get(pk=int(jollof_order.jollof_buyer.pk))
                if jollof_order.status != 0:
                    msg = 'You can no longer accept this reservation.'
                    self.text_message(fbid, msg)
                    seller.current_state = 'DEFAULT'
                    seller.save()
                    return
                jollof_order.status = 1
                jollof_order.save()
                msg = 'Great news! ' + seller.restaurant + ' have accepted your reservation and they are waiting for you with your jollof!. Remember your order code is ' + jollof_order.code + ' :D'
                self.text_buyer(buyer.fbid, msg)
                seller.current_state = 'DEFAULT'
                seller.save()
                msg = 'You have accepted ' + buyer.user.first_name + '\'s reservation for Jollof and they have been notified. They will be at your restaurant soon with their order code: ' + jollof_order.code
                self.text_message(fbid, msg)
            elif jollof_action == 2:
                # seller rejected order.
                if jollof_order.status != 0:
                    msg = 'You can no longer reject this reservation.'
                    self.text_message(fbid, msg)
                    seller.current_state = 'DEFAULT'
                    seller.save()
                    return
                jollof_order.status = 2
                jollof_order.save()
                msg = 'You have rejected the reservation. I hope all is well with your Jollof and your restaurant.'
                self.text_message(fbid, msg)
                buyer = Profile.objects.get(pk=int(jollof_order.jollof_buyer.pk))
                msg = 'Oh shucks! ' + seller.restaurant + ' will not be able to set up a jollof reservation for you :( Say Jollof! to find other places near you.'
                self.text_buyer(buyer.fbid, msg)            
        else:
            seller = Profile.objects.get(fbid=fbid)
            jollof_orders = JollofOrder.objects.filter(jollof_seller=seller).filter(order_type=1).filter(status=0)
            if jollof_orders.count() < 1:
                msg = 'You have no pending jollof reservations right now. I will send you updates in real-time.'
                self.text_message(fbid, msg)
            else:
                count = 0
                generic_sellers = '{"recipient":{"id":"'+str(fbid)+'"},"message":{"attachment":{"type":"template","payload":{"template_type":"generic","elements":['
                generic_ending = ']}}}}'
                generic_elements = ''
                for jollof_order in jollof_orders:
                    if count >= 10:
                        break
                    count += 1
                    buyer = Profile.objects.get(pk=int(jollof_order.jollof_buyer.pk))
                    img_link = 'http://via.placeholder.com/350x350'
                    generic_title = buyer.user.first_name + ' is requesting a Jollof reservation!'
                    generic_subtitle = 'Order Code: ' + jollof_order.code           
                    accept_order_payload = 'JOLLOF_PENDING_RESERVATIONS_' + str(jollof_order.pk) + '_1'
                    reject_order_payload = 'JOLLOF_PENDING_RESERVATIONS_' + str(jollof_order.pk) + '_2'
                    generic_elements += '{"title":"'+str(generic_title)+'","image_url":"'+str(img_link)+'","subtitle":"'+str(generic_subtitle)+'.","buttons":[{"type":"postback","title":"Accept Reservation","payload":"'+str(accept_order_payload)+'"},{"type":"postback","payload":"'+str(reject_order_payload)+'","title":"Reject Reservation"}]},'
                #Remove trailing comma
                generic_elements = generic_elements[:-1]
                generic_message = generic_sellers + generic_elements + generic_ending
                print('Generic message: ' + generic_message)
                headers = {
                    'Content-Type': 'application/json',
                }
                params = (
                    ('access_token', self.SELLER_ACCESS_TOKEN),
                )
                response = requests.post('https://graph.facebook.com/v2.6/me/messages', headers=headers, params=params, data=generic_message)
                pprint(response.json())
        return
    

    def jollof_accepted_deliveries(self, fbid, payload):
        if 'JOLLOF_ACCEPTED_DELIVERIES_' in payload:
            seller = Profile.objects.get(fbid=fbid)
            payload_list = payload.split('_')
            jollof_delivery_pk = int(payload_list[3])
            jollof_action = int(payload_list[4])
            jollof_order = JollofOrder.objects.get(pk=jollof_delivery_pk)
            if jollof_action == 1:
                #seller completed order
                buyer = Profile.objects.get(pk=int(jollof_order.jollof_buyer.pk))
                if jollof_order.status != 1:
                    msg = 'You can no longer complete this order.'
                    self.text_message(fbid, msg)
                    seller.current_state = 'DEFAULT'
                    seller.save()
                    return
                jollof_order.status = 4
                jollof_order.save()
                msg = seller.restaurant + ' just marked your delivery as completed! I hope you are enjoying your Jollof :D'
                self.text_buyer(buyer.fbid, msg)
                seller.current_state = 'DEFAULT'
                seller.save()
                msg = 'You have marked ' + buyer.user.first_name + '\'s Jollof delivery as completed and they have been notified. Sweet!'
                self.text_message(fbid, msg)
            elif jollof_action == 2:
                # seller cancelled order.
                if jollof_order.status != 1:
                    msg = 'You can no longer complete this order.'
                    self.text_message(fbid, msg)
                    seller.current_state = 'DEFAULT'
                    seller.save()
                    return
                jollof_order.status = 3
                jollof_order.save()
                msg = 'You have cancelled the delivery. I hope all is well with your Jollof.'
                self.text_message(fbid, msg)
                buyer = Profile.objects.get(pk=int(jollof_order.jollof_buyer.pk))
                msg = 'Oh shucks! ' + seller.restaurant + ' will not be able to deliver your Jollof. Seems like Ghanian goblins got their delivery guy. Say Jollof! to find other places near you.'
                self.text_buyer(buyer.fbid, msg)            
        else:
            seller = Profile.objects.get(fbid=fbid)
            jollof_orders = JollofOrder.objects.filter(jollof_seller=seller).filter(order_type=2).filter(status=1)
            if jollof_orders.count() < 1:
                msg = 'You have not accepted to deliver any orders.'
                self.text_message(fbid, msg)
            else:
                count = 0
                generic_sellers = '{"recipient":{"id":"'+str(fbid)+'"},"message":{"attachment":{"type":"template","payload":{"template_type":"generic","elements":['
                generic_ending = ']}}}}'
                generic_elements = ''
                for jollof_order in jollof_orders:
                    if count >= 10:
                        break
                    count += 1
                    buyer = Profile.objects.get(pk=int(jollof_order.jollof_buyer.pk))
                    img_link = 'http://via.placeholder.com/350x350'
                    generic_title = buyer.user.first_name + ' wants your Jollof delivery completed!'
                    generic_subtitle = 'Order Code: ' + jollof_order.code                
                    accept_order_payload = 'JOLLOF_ACCEPTED_DELIVERIES_' + str(jollof_order.pk) + '_1'
                    reject_order_payload = 'JOLLOF_ACCEPTED_DELIVERIES_' + str(jollof_order.pk) + '_2'
                    generic_elements += '{"title":"'+str(generic_title)+'","image_url":"'+str(img_link)+'","subtitle":"'+str(generic_subtitle)+'.","buttons":[{"type":"postback","title":"Complete Order","payload":"'+str(accept_order_payload)+'"},{"type":"postback","payload":"'+str(reject_order_payload)+'","title":"Cancel Order"}]},'
                #Remove trailing comma
                generic_elements = generic_elements[:-1]
                generic_message = generic_sellers + generic_elements + generic_ending
                print('Generic message: ' + generic_message)
                headers = {
                    'Content-Type': 'application/json',
                }
                params = (
                    ('access_token', self.SELLER_ACCESS_TOKEN),
                )
                response = requests.post('https://graph.facebook.com/v2.6/me/messages', headers=headers, params=params, data=generic_message)
                pprint(response.json())
        return


    def jollof_accepted_reservations(self, fbid, payload):
        if 'JOLLOF_ACCEPTED_RESERVATIONS_' in payload:
            seller = Profile.objects.get(fbid=fbid)
            payload_list = payload.split('_')
            jollof_delivery_pk = int(payload_list[3])
            jollof_action = int(payload_list[4])
            jollof_order = JollofOrder.objects.get(pk=jollof_delivery_pk)
            if jollof_action == 1:
                #seller completed reservation
                buyer = Profile.objects.get(pk=int(jollof_order.jollof_buyer.pk))
                if jollof_order.status != 1:
                    msg = 'You can no longer complete this reservation.'
                    self.text_message(fbid, msg)
                    seller.current_state = 'DEFAULT'
                    seller.save()
                    return
                jollof_order.status = 4
                jollof_order.save()
                msg = 'Sweet! ' + seller.restaurant + ' just marked your reservation as completed. I hope you are enjoying your jollof :D'
                self.text_buyer(buyer.fbid, msg)
                seller.current_state = 'DEFAULT'
                seller.save()
                msg = 'You have marked ' + buyer.user.first_name + '\'s Jollof reservation as completed and they have been notified. Nice!'
                self.text_message(fbid, msg)
            elif jollof_action == 2:
                # seller cancelled order.
                if jollof_order.status != 1:
                    msg = 'You can no longer complete this reservation.'
                    self.text_message(fbid, msg)
                    seller.current_state = 'DEFAULT'
                    seller.save()
                    return
                jollof_order.status = 3
                jollof_order.save()
                buyer = Profile.objects.get(pk=int(jollof_order.jollof_buyer.pk))
                msg = 'You have cancelled the reservation and ' + buyer.user.first_name + ' has been informed. I hope all is well with your Jollof.'
                self.text_message(fbid, msg)
                msg = 'I am so sorry right now but ' + seller.restaurant + ' will not be able to accept your jollof reservation. :( Say Jollof! to find other places near you.'
                self.text_buyer(buyer.fbid, msg)           
        else:
            seller = Profile.objects.get(fbid=fbid)
            jollof_orders = JollofOrder.objects.filter(jollof_seller=seller).filter(order_type=1).filter(status=1)
            if jollof_orders.count() < 1:
                msg = 'You have not accepted any reservations for your jollof.'
                self.text_message(fbid, msg)
            else:
                count = 0
                generic_sellers = '{"recipient":{"id":"'+str(fbid)+'"},"message":{"attachment":{"type":"template","payload":{"template_type":"generic","elements":['
                generic_ending = ']}}}}'
                generic_elements = ''
                for jollof_order in jollof_orders:
                    if count >= 10:
                        break
                    count += 1
                    buyer = Profile.objects.get(pk=int(jollof_order.jollof_buyer.pk))
                    img_link = 'http://via.placeholder.com/350x350'
                    generic_title = buyer.user.first_name + ' wants their Jollof reservation completed!'
                    generic_subtitle = 'Order Code: ' + jollof_order.code                   
                    accept_order_payload = 'JOLLOF_ACCEPTED_RESERVATIONS_' + str(jollof_order.pk) + '_1'
                    reject_order_payload = 'JOLLOF_ACCEPTED_RESERVATIONS_' + str(jollof_order.pk) + '_2'
                    generic_elements += '{"title":"'+str(generic_title)+'","image_url":"'+str(img_link)+'","subtitle":"'+str(generic_subtitle)+'.","buttons":[{"type":"postback","title":"Complete Reservation","payload":"'+str(accept_order_payload)+'"},{"type":"postback","payload":"'+str(reject_order_payload)+'","title":"Cancel Reservation"}]},'
                #Remove trailing comma
                generic_elements = generic_elements[:-1]
                generic_message = generic_sellers + generic_elements + generic_ending
                print('Generic message: ' + generic_message)
                headers = {
                    'Content-Type': 'application/json',
                }
                params = (
                    ('access_token', self.SELLER_ACCESS_TOKEN),
                )
                response = requests.post('https://graph.facebook.com/v2.6/me/messages', headers=headers, params=params, data=generic_message)
                pprint(response.json())
        return


    def delicacy_pending_deliveries(self, fbid, payload):
        if 'DELICACY_PENDING_DELIVERIES_' in payload:
            seller = Profile.objects.get(fbid=fbid)
            payload_list = payload.split('_')
            delicacy_delivery_pk = int(payload_list[3])
            delicacy_action = int(payload_list[4])
            delicacy_order = DelicacyOrder.objects.get(pk=delicacy_delivery_pk)
            delicacy = Delicacy.objects.get(pk=int(delicacy_order.delicacy.pk))
            if delicacy_action == 1:
                #seller accepted order
                buyer = Profile.objects.get(pk=int(delicacy_order.delicacy_buyer.pk))
                if delicacy_order.status != 0:
                    msg = 'You can no longer accept this order.'
                    self.text_message(fbid, msg)
                    seller.current_state = 'DEFAULT'
                    seller.save()
                    return
                delicacy_order.status = 1
                delicacy_order.save()
                msg = seller.restaurant + ' just accepted your order for ' + delicacy.name + ' and are on their way to deliver it to you! You will get a phone call from them once they arrive. Remember your order code is ' + delicacy_order.code + ' :D'
                self.text_buyer(buyer.fbid, msg)
                seller.current_state = 'DEFAULT'
                seller.save()
                msg = 'You have accepted to deliver ' + buyer.user.first_name + '\'s ' + delicacy.name + ' delicacy and they have been notified.'
                self.text_message(fbid, msg)
                #  broadcast to flash for acceptance
                avalaible_flash = Profile.objects.filter(user_type='f').filter(available=True)
                for flash in avalaible_flash:
                    #  check if flash doesn't have any order to fufill
                    flash_jollof_order = JollofOrder.objects.filter(jollof_flash=flash)
                    flash_busy = False
                    for flash_jollof in flash_jollof_order:
                        if flash_jollof.flash_status > 0 and flash_jollof.flash_status < 4:
                            #  flash is currently busy
                            flash_busy = True
                            break
                    if flash_busy:
                        continue
                    flash_delicacy_order = DelicacyOrder.objects.filter(delicacy_flash=flash)
                    for flash_delicacy in flash_delicacy_order:       
                        if flash_delicacy.flash_status > 0 and flash_delicacy.flash_status < 4:
                            # flash is currently busy
                            flash_busy = True
                            break
                    if flash_busy:
                        continue
                    # flash not busy, check if flash in proximity of restaurant.
                    distance = self.get_distance((flash.latitude, flash.longitude), (delicacy_order.delicacy_seller.latitude, delicacy_order.delicacy_seller.longitude))
                    if distance >= float(self.NEAREST_KM):
                        # flash not in range.
                        continue
                    # flash not busy, check if flash in proximity of buyer.
                    distance = self.get_distance((flash.latitude, flash.longitude), (delicacy_order.delicacy_buyer.latitude, delicacy_order.delicacy_buyer.longitude))
                    if distance >= float(self.NEAREST_KM):
                        # flash not in range.
                        continue
                    #  flash is free and in range
                    headers = {
                        'Content-Type': 'application/json',
                    }
                    params = (
                        ('access_token', self.SELLER_ACCESS_TOKEN),
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
                            "text":"You have a Delicacy delivery from REST to FULL_NAME with order code ORDER_CODE. DELICACY_INFO",
                            "buttons":[
                            {
                                "type":"postback",
                                "title":"Accept To Deliver",
                                "payload":"PAYLOAD"
                            }
                            ]
                        }
                        }
                    }
                    }'''
                    data = data.replace('FULL_NAME', buyer.user.first_name + ' ' + buyer.user.last_name)
                    data = data.replace('USER_ID', flash.fbid)
                    data = data.replace('REST', delicacy_order.delicacy_seller.restaurant)
                    data = data.replace('ORDER_CODE', delicacy_order.code)
                    data = data.replace('PAYLOAD', 'ACCEPT_PENDING_JOLLOF_' + str(delicacy_order.pk))
                    data = data.replace('DELICACY_INFO', delicacy.name + '; ' + delicacy.description)
                    pprint(str(data))
                    data = json.dumps(json.loads(data)).encode('utf-8')
                    response = requests.post('https://graph.facebook.com/v2.6/me/messages', headers=headers, params=params, data=data)
                    pprint(response.json())
            elif delicacy_action == 2:
                # seller rejected order.
                if delicacy_order.status != 0:
                    msg = 'You can no longer reject this order.'
                    self.text_message(fbid, msg)
                    seller.current_state = 'DEFAULT'
                    seller.save()
                    return
                delicacy_order.status = 2
                delicacy_order.save()
                buyer = Profile.objects.get(pk=int(delicacy_order.delicacy_buyer.pk))
                msg = 'You have rejected ' + buyer.user.first_name + '\'s' + ' order for ' + delicacy.name + '. I hope all is well with your restaurant.'
                self.text_message(fbid, msg)
                msg = 'Oh shucks! ' + seller.restaurant + ' will not be able to get you your ' + delicacy.name + ' Delicacy :( Say Jollof! to find other places near you.'
                self.text_buyer(buyer.fbid, msg)            
        else:
            seller = Profile.objects.get(fbid=fbid)
            delicacy_orders = DelicacyOrder.objects.filter(delicacy_seller=seller).filter(order_type=2).filter(status=0)
            if delicacy_orders.count() < 1:
                msg = 'You have no pending delicacy deliveries right now. I will send you updates in real-time.'
                self.text_message(fbid, msg)
            else:
                count = 0
                generic_sellers = '{"recipient":{"id":"'+str(fbid)+'"},"message":{"attachment":{"type":"template","payload":{"template_type":"generic","elements":['
                generic_ending = ']}}}}'
                generic_elements = ''
                for delicacy_order in delicacy_orders:
                    if count >= 10:
                        break
                    count += 1
                    buyer = Profile.objects.get(pk=int(delicacy_order.delicacy_buyer.pk))
                    delicacy = Delicacy.objects.get(pk=int(delicacy_order.delicacy.pk))
                    img_link = 'http://via.placeholder.com/350x350'
                    generic_title = buyer.user.first_name + ' wants ' + delicacy.name + ' delivered!'
                    generic_subtitle = 'Order Code: ' + delicacy_order.code          
                    accept_order_payload = 'DELICACY_PENDING_DELIVERIES_' + str(delicacy_order.pk) + '_1'
                    reject_order_payload = 'DELICACY_PENDING_DELIVERIES_' + str(delicacy_order.pk) + '_2'
                    generic_elements += '{"title":"'+str(generic_title)+'","image_url":"'+str(img_link)+'","subtitle":"'+str(generic_subtitle)+'.","buttons":[{"type":"postback","title":"Accept Order","payload":"'+str(accept_order_payload)+'"},{"type":"postback","payload":"'+str(reject_order_payload)+'","title":"Reject Order"}]},'
                #Remove trailing comma
                generic_elements = generic_elements[:-1]
                generic_message = generic_sellers + generic_elements + generic_ending
                print('Generic message: ' + generic_message)
                headers = {
                    'Content-Type': 'application/json',
                }
                params = (
                    ('access_token', self.SELLER_ACCESS_TOKEN),
                )
                response = requests.post('https://graph.facebook.com/v2.6/me/messages', headers=headers, params=params, data=generic_message)
                pprint(response.json())
        return
    

    def delicacy_pending_reservations(self, fbid, payload):
        if 'DELICACY_PENDING_RESERVATIONS_' in payload:
            seller = Profile.objects.get(fbid=fbid)
            payload_list = payload.split('_')
            delicacy_delivery_pk = int(payload_list[3])
            delicacy_action = int(payload_list[4])
            delicacy_order = DelicacyOrder.objects.get(pk=delicacy_delivery_pk)
            delicacy = Delicacy.objects.get(pk=int(delicacy_order.delicacy.pk))
            if delicacy_action == 1:
                #seller accepted reservation
                buyer = Profile.objects.get(pk=int(delicacy_order.delicacy_buyer.pk))
                if delicacy_order.status != 0:
                    msg = 'You can no longer accept this reservation.'
                    self.text_message(fbid, msg)
                    seller.current_state = 'DEFAULT'
                    seller.save()
                    return
                delicacy_order.status = 1
                delicacy_order.save()
                msg = 'Great news! ' + seller.restaurant + ' have accepted your reservation for ' + delicacy.name + ' at their restaurant!. Remember your order code is ' + delicacy_order.code + ' :D'
                self.text_buyer(buyer.fbid, msg)
                seller.current_state = 'DEFAULT'
                seller.save()
                msg = 'You have accepted ' + buyer.user.first_name + '\'s ' + delicacy.name + ' reservation and they have been notified. They will be at your restaurant soon with their order code: ' + jollof_order.code
                self.text_message(fbid, msg)
            elif delicacy_action == 2:
                # seller rejected order.
                if delicacy_order.status != 0:
                    msg = 'You can no longer reject this reservation.'
                    self.text_message(fbid, msg)
                    seller.current_state = 'DEFAULT'
                    seller.save()
                    return
                delicacy_order.status = 2
                delicacy_order.save()
                buyer = Profile.objects.get(pk=int(delicacy_order.delicacy_buyer.pk))
                msg = 'You have rejected ' + buyer.user.first_name + '\'s ' + delicacy.name + ' reservation. I hope all is well with your restaurant.'
                self.text_message(fbid, msg)
                msg = 'Oh shucks! ' + seller.restaurant + ' will not be able to set up a reservation for ' + delicacy.name + ' :( Say Jollof! to find other places near you.'
                self.text_buyer(buyer.fbid, msg)   
        else:
            seller = Profile.objects.get(fbid=fbid)
            delicacy_orders = DelicacyOrder.objects.filter(delicacy_seller=seller).filter(order_type=1).filter(status=0)
            if delicacy_orders.count() < 1:
                msg = 'You have no pending delicacy reservations right now. I will send you updates in real-time.'
                self.text_message(fbid, msg)
            else:
                count = 0
                generic_sellers = '{"recipient":{"id":"'+str(fbid)+'"},"message":{"attachment":{"type":"template","payload":{"template_type":"generic","elements":['
                generic_ending = ']}}}}'
                generic_elements = ''
                for delicacy_order in delicacy_orders:
                    if count >= 10:
                        break
                    count += 1
                    buyer = Profile.objects.get(pk=int(delicacy_order.delicacy_buyer.pk))
                    delicacy = Delicacy.objects.get(pk=int(delicacy_order.delicacy.pk))
                    img_link = 'http://via.placeholder.com/350x350'
                    generic_title = buyer.user.first_name + ' is requesting a reservation for ' + delicacy.name + '!'
                    generic_subtitle = 'Order Code: ' + delicacy_order.code 
                    accept_order_payload = 'DELICACY_PENDING_RESERVATIONS_' + str(delicacy_order.pk) + '_1'
                    reject_order_payload = 'DELICACY_PENDING_RESERVATIONS_' + str(delicacy_order.pk) + '_2'
                    generic_elements += '{"title":"'+str(generic_title)+'","image_url":"'+str(img_link)+'","subtitle":"'+str(generic_subtitle)+'.","buttons":[{"type":"postback","title":"Accept Reservation","payload":"'+str(accept_order_payload)+'"},{"type":"postback","payload":"'+str(reject_order_payload)+'","title":"Reject Reservation"}]},'
                #Remove trailing comma
                generic_elements = generic_elements[:-1]
                generic_message = generic_sellers + generic_elements + generic_ending
                print('Generic message: ' + generic_message)
                headers = {
                    'Content-Type': 'application/json',
                }
                params = (
                    ('access_token', self.SELLER_ACCESS_TOKEN),
                )
                response = requests.post('https://graph.facebook.com/v2.6/me/messages', headers=headers, params=params, data=generic_message)
                pprint(response.json())
        return
    

    def delicacy_accepted_deliveries(self, fbid, payload):
        if 'DELICACY_ACCEPTED_DELIVERIES_' in payload:
            seller = Profile.objects.get(fbid=fbid)
            payload_list = payload.split('_')
            delicacy_delivery_pk = int(payload_list[3])
            delicacy_action = int(payload_list[4])
            delicacy_order = DelicacyOrder.objects.get(pk=delicacy_delivery_pk)
            delicacy = Delicacy.objects.get(pk=int(delicacy_order.delicacy.pk))
            if delicacy_action == 1:
                #seller completed order
                buyer = Profile.objects.get(pk=int(delicacy_order.delicacy_buyer.pk))
                if delicacy_order.status != 1:
                    msg = 'You can no longer complete this order.'
                    self.text_message(fbid, msg)
                    seller.current_state = 'DEFAULT'
                    seller.save()
                    return
                delicacy_order.status = 4
                delicacy_order.save()
                msg = seller.restaurant + ' just marked your delivery as completed! I hope you are enjoying your ' + delicacy.name + ' :D'
                self.text_buyer(buyer.fbid, msg)
                seller.current_state = 'DEFAULT'
                seller.save()
                msg = 'You have marked ' + buyer.user.first_name + '\'s ' + delicacy.name + ' delivery as completed and they have been notified. Sweet!'
                self.text_message(fbid, msg)
            elif delicacy_action == 2:
                # seller cancelled order.
                if delicacy_order.status != 1:
                    msg = 'You can no longer cancel this order.'
                    self.text_message(fbid, msg)
                    seller.current_state = 'DEFAULT'
                    seller.save()
                    return
                delicacy_order.status = 3
                delicacy_order.save()
                buyer = Profile.objects.get(pk=int(delicacy_order.delicacy_buyer.pk))
                msg = 'You have cancelled ' + buyer.user.first_name + '\'s delivery of ' + delicacy.name + '. I hope all is well with your restaurant.'
                self.text_message(fbid, msg)
                msg = 'Oh shucks! ' + seller.restaurant + ' will not be able to deliver your ' + delicacy.name + '. Seems like Ghanaian goblins got their delivery guy. Say Jollof! to find other places near you.'
                self.text_buyer(buyer.fbid, msg)            
        else:
            seller = Profile.objects.get(fbid=fbid)
            delicacy_orders = DelicacyOrder.objects.filter(delicacy_seller=seller).filter(order_type=2).filter(status=1)
            if delicacy_orders.count() < 1:
                msg = 'You have not accepted to deliver any orders.'
                self.text_message(fbid, msg)
            else:
                count = 0
                generic_sellers = '{"recipient":{"id":"'+str(fbid)+'"},"message":{"attachment":{"type":"template","payload":{"template_type":"generic","elements":['
                generic_ending = ']}}}}'
                generic_elements = ''
                for delicacy_order in delicacy_orders:
                    if count >= 10:
                        break
                    count += 1
                    delicacy = Delicacy.objects.get(pk=int(delicacy_order.delicacy.pk))
                    buyer = Profile.objects.get(pk=int(delicacy_order.delicacy_buyer.pk))
                    img_link = 'http://via.placeholder.com/350x350'
                    generic_title = buyer.user.first_name + ' wants your ' + delicacy.name + ' delivery completed!'
                    generic_subtitle = 'Order Code: ' + delicacy_order.code        
                    accept_order_payload = 'DELICACY_ACCEPTED_DELIVERIES_' + str(delicacy_order.pk) + '_1'
                    reject_order_payload = 'DELICACY_ACCEPTED_DELIVERIES_' + str(delicacy_order.pk) + '_2'
                    generic_elements += '{"title":"'+str(generic_title)+'","image_url":"'+str(img_link)+'","subtitle":"'+str(generic_subtitle)+'.","buttons":[{"type":"postback","title":"Complete Order","payload":"'+str(accept_order_payload)+'"},{"type":"postback","payload":"'+str(reject_order_payload)+'","title":"Cancel Order"}]},'
                #Remove trailing comma
                generic_elements = generic_elements[:-1]
                generic_message = generic_sellers + generic_elements + generic_ending
                print('Generic message: ' + generic_message)
                headers = {
                    'Content-Type': 'application/json',
                }
                params = (
                    ('access_token', self.SELLER_ACCESS_TOKEN),
                )
                response = requests.post('https://graph.facebook.com/v2.6/me/messages', headers=headers, params=params, data=generic_message)
                pprint(response.json())
        return


    def delicacy_accepted_reservations(self, fbid, payload):
        if 'DELICACY_ACCEPTED_RESERVATIONS_' in payload:
            seller = Profile.objects.get(fbid=fbid)
            payload_list = payload.split('_')
            delicacy_delivery_pk = int(payload_list[3])
            delicacy_action = int(payload_list[4])
            delicacy_order = DelicacyOrder.objects.get(pk=delicacy_delivery_pk)
            if delicacy_action == 1:
                #seller completed reservation
                buyer = Profile.objects.get(pk=int(delicacy_order.delicacy_buyer.pk))
                if delicacy_order.status != 1:
                    msg = 'You can no longer complete this reservation.'
                    self.text_message(fbid, msg)
                    seller.current_state = 'DEFAULT'
                    seller.save()
                    return
                delicacy_order.status = 4
                delicacy_order.save()
                msg = 'Sweet! ' + seller.restaurant + ' just marked your reservation as completed. I hope you are enjoying your delicacy :D'
                self.text_buyer(buyer.fbid, msg)
                seller.current_state = 'DEFAULT'
                seller.save()
                msg = 'You have marked ' + buyer.user.first_name + '\'s delicacy reservation as completed and they have been notified. Nice!'
                self.text_message(fbid, msg)
            elif delicacy_action == 2:
                # seller cancelled order.
                if delicacy_order.status != 1:
                    msg = 'You can no longer cancel this reservation.'
                    self.text_message(fbid, msg)
                    seller.current_state = 'DEFAULT'
                    seller.save()
                    return
                delicacy_order.status = 3
                delicacy_order.save()
                buyer = Profile.objects.get(pk=int(delicacy_order.jollof_buyer.pk))
                msg = 'You have cancelled the reservation and ' + buyer.user.first_name + ' has been informed. I hope all is well with your restaurant.'
                self.text_message(fbid, msg)
                msg = 'I am so sorry right now but ' + seller.restaurant + ' will not be able to accept your delicacy reservation. :( Say Jollof! to find other places near you.'
                self.text_buyer(buyer.fbid, msg)           
        else:
            seller = Profile.objects.get(fbid=fbid)
            delicacy_orders = DelicacyOrder.objects.filter(delicacy_seller=seller).filter(order_type=1).filter(status=1)
            if delicacy_orders.count() < 1:
                msg = 'You have not accepted any reservations for your delicacies.'
                self.text_message(fbid, msg)
            else:
                count = 0
                generic_sellers = '{"recipient":{"id":"'+str(fbid)+'"},"message":{"attachment":{"type":"template","payload":{"template_type":"generic","elements":['
                generic_ending = ']}}}}'
                generic_elements = ''
                for delicacy_order in delicacy_orders:
                    if count >= 10:
                        break
                    count += 1
                    buyer = Profile.objects.get(pk=int(delicacy_order.delicacy_buyer.pk))
                    delicacy = Delicacy.objects.get(pk=int(delicacy_order.delicacy.pk))
                    img_link = 'http://via.placeholder.com/350x350'
                    generic_title = buyer.user.first_name + ' wants their Delicacy reservation completed!'
                    generic_subtitle = 'Order Code: ' + delicacy_order.code       
                    accept_order_payload = 'DELICACY_ACCEPTED_RESERVATIONS_' + str(delicacy_order.pk) + '_1'
                    reject_order_payload = 'DELICACY_ACCEPTED_RESERVATIONS_' + str(delicacy_order.pk) + '_2'
                    generic_elements += '{"title":"'+str(generic_title)+'","image_url":"'+str(img_link)+'","subtitle":"'+str(generic_subtitle)+'.","buttons":[{"type":"postback","title":"Complete Reservation","payload":"'+str(accept_order_payload)+'"},{"type":"postback","payload":"'+str(reject_order_payload)+'","title":"Cancel Reservation"}]},'
                #Remove trailing comma
                generic_elements = generic_elements[:-1]
                generic_message = generic_sellers + generic_elements + generic_ending
                print('Generic message: ' + generic_message)
                headers = {
                    'Content-Type': 'application/json',
                }
                params = (
                    ('access_token', self.SELLER_ACCESS_TOKEN),
                )
                response = requests.post('https://graph.facebook.com/v2.6/me/messages', headers=headers, params=params, data=generic_message)
                pprint(response.json())
        return
