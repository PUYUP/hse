class JSONDecodeError(Exception):
    pass

class MidtransAPIError(Exception):
    def __init__(self, message, api_response_dict=None, http_status_code=None, raw_http_learner_data=None):
        self.message = message
        self.api_response_dict = api_response_dict
        self.http_status_code = int(http_status_code)
        self.raw_http_learner_data = raw_http_learner_data

    def __str__(self):
        return self.message
