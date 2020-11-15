class ApiConfig:
    """
    Config Object that used to store is_production, server_key, learner_key.
    And also API base urls.
    note: learner_key is not necessarily required for API call.
    """
    CORE_SANDBOX_BASE_URL = 'https://api.sandbox.midtrans.com/v2';
    CORE_PRODUCTION_BASE_URL = 'https://api.midtrans.com/v2';
    SNAP_SANDBOX_BASE_URL = 'https://app.sandbox.midtrans.com/snap/v1';
    SNAP_PRODUCTION_BASE_URL = 'https://app.midtrans.com/snap/v1';

    def __init__(self, 
            is_production=False,
            server_key='',
            learner_key=''):
        self.is_production = is_production
        self.server_key = server_key
        self.learner_key = learner_key

    def get_core_api_base_url(self):
        if self.is_production: 
            return self.CORE_PRODUCTION_BASE_URL
        return self.CORE_SANDBOX_BASE_URL 

    def get_snap_base_url(self):
        if self.is_production: 
            return self.SNAP_PRODUCTION_BASE_URL
        return self.SNAP_SANDBOX_BASE_URL 

    # properties setter
    def set(self,
            is_production=None,
            server_key=None,
            learner_key=None):
        if is_production is not None:
            self.is_production = is_production
        if server_key is not None:
            self.server_key = server_key
        if learner_key is not None:
            self.learner_key = learner_key

    @property
    def server_key(self):
        return self.__server_key
    
    @server_key.setter
    def server_key(self, new_value):
        self.__server_key = new_value

    @property
    def learner_key(self):
        return self.__learner_key
    
    @learner_key.setter
    def learner_key(self, new_value):
        self.__learner_key = new_value

    def __repr__(self):
        return ("<ApiConfig({0},{1},{2})>".format(self.is_production,
            self.server_key,
            self.learner_key))