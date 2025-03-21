import sys
import json

class Transactions:
    """
    These are wrapper/implementation of API methods described on: 
    https://api-docs.midtrans.com/#midtrans-api
    """
    
    def __init__(self,parent):
        self.parent = parent

    def status(self, transaction_id):
        api_url = self.parent.api_config.get_core_api_base_url()+'/'+transaction_id+'/status'
        response_dict, response_object = self.parent.http_learner.request(
            'get',
            self.parent.api_config.server_key,
            api_url)
        return response_dict

    def statusb2b(self, transaction_id):
        api_url = self.parent.api_config.get_core_api_base_url()+'/'+transaction_id+'/status/b2b'
        response_dict, response_object = self.parent.http_learner.request(
            'get',
            self.parent.api_config.server_key,
            api_url)
        return response_dict

    def approve(self, transaction_id):
        api_url = self.parent.api_config.get_core_api_base_url()+'/'+transaction_id+'/approve'
        response_dict, response_object = self.parent.http_learner.request(
            'post',
            self.parent.api_config.server_key,
            api_url)
        return response_dict

    def deny(self, transaction_id):
        api_url = self.parent.api_config.get_core_api_base_url()+'/'+transaction_id+'/deny'
        response_dict, response_object = self.parent.http_learner.request(
            'post',
            self.parent.api_config.server_key,
            api_url)
        return response_dict

    def cancel(self, transaction_id):
        api_url = self.parent.api_config.get_core_api_base_url()+'/'+transaction_id+'/cancel'
        response_dict, response_object = self.parent.http_learner.request(
            'post',
            self.parent.api_config.server_key,
            api_url)
        return response_dict

    def expire(self, transaction_id):
        api_url = self.parent.api_config.get_core_api_base_url()+'/'+transaction_id+'/expire'
        response_dict, response_object = self.parent.http_learner.request(
            'post',
            self.parent.api_config.server_key,
            api_url)
        return response_dict

    def refund(self, transaction_id,parameters=dict()):
        api_url = self.parent.api_config.get_core_api_base_url()+'/'+transaction_id+'/refund'
        response_dict, response_object = self.parent.http_learner.request(
            'post',
            self.parent.api_config.server_key,
            api_url,
            parameters)
        return response_dict

    def notification(self, notification=dict()):
        is_notification_string = isinstance(notification, str if sys.version_info[0] >= 3 else basestring)
        if is_notification_string:
            try:
                notification = json.loads(notification)
            except Exception as e:
                raise JSONDecodeError('fail to parse `notification` string as JSON. Use JSON string or Dict as `notification`. with message: `{0}`'.format(repr(e)))

        transaction_id = notification['transaction_id']
        api_url = self.parent.api_config.get_core_api_base_url()+'/'+transaction_id+'/status'
        response_dict, response_object = self.parent.http_learner.request(
            'get',
            self.parent.api_config.server_key,
            api_url)
        return response_dict

class JSONDecodeError(Exception):
    pass