from .config import ApiConfig
from .http_learner import HttpLearner
from .transactions import Transactions

class Snap:
    """
    Snap object used to do request to Midtrans Snap API
    """

    def __init__(self, 
            is_production=False,
            server_key='',
            learner_key=''):

        self.api_config = ApiConfig(is_production,server_key,learner_key)
        self.http_learner = HttpLearner()
        self.transactions = Transactions(self)

    @property
    def api_config(self):
        return self.__api_config

    @api_config.setter
    def api_config(self, new_value):
        self.__api_config = new_value

    def create_transaction(self,parameters=dict()):
        """
        Trigger API call to Snap API
        :param parameters: dictionary of SNAP API JSON body as parameter, will be converted to JSON
        (more params detail refer to: https://snap-docs.midtrans.com)

        :return: Dictionary from JSON decoded response, that contains `token` and `redirect_url`
        """
        api_url = self.api_config.get_snap_base_url()+'/transactions'

        response_dict, response_object = self.http_learner.request(
            'post',
            self.api_config.server_key,
            api_url,
            parameters)
        return response_dict

    def create_transaction_token(self,parameters=dict()):
        """
        Wrapper method that call `create_transaction` and directly :return: `token`
        """
        return self.create_transaction(parameters)['token']

    def create_transaction_redirect_url(self,parameters=dict()):
        """
        Wrapper method that call `create_transaction` and directly :return: `redirect_url`
        """
        return self.create_transaction(parameters)['redirect_url']
