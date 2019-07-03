from requests_oauthlib import OAuth2Session
from oauthlib.oauth2 import BackendApplicationClient


class AuthenticatedControlShiftError(Exception):
    pass


class AuthenticatedControlShift:
    """
    Params:
    @settings: object where CONTROLSHIFT_CLIENT_ID and other
               SETTINGS_MAP keys below are mapped to the appropriate object
    @token: existing token (dict) -- see ratelimits below and make sure your
            application will abide by them
    @client_class: default is BackendApplicationClient, but if you have a
                   webapplication, use oauthlib.oauth2.WebApplication
    If you skip the settings= parameter you can also
    pass the SETTINGS_MAP values in by argument, e.g. client_id=....
    @debug: by default will print token saving event

    RateLimits:
    * Oauth tokens requests: 10 requests per minute
    * Oauth API requests: 1000 per minute
    * Oauth token (default) duration: 2 hours

    Override:
    def token_saver(self, token)
      to store a token in your application context for new instantiations
    """

    SETTINGS_MAP = {
        'CONTROLSHIFT_CLIENT_ID': 'client_id',
        'CONTROLSHIFT_CLIENT_SECRET': 'client_secret',
        'CONTROLSHIFT_BASEURL': 'base_url'
    }

    _session = None
    _token = None
    client = None

    def __init__(self,
                 settings=None,
                 client_class=BackendApplicationClient,
                 **params):
        if settings:
            for settings_key, attr in self.SETTINGS_MAP.items():
                setattr(self, attr, getattr(settings, settings_key, None))

        for attr in self.SETTINGS_MAP.values():
            if attr in params:
                setattr(self, attr, params.get(attr))
            elif not getattr(self, attr, None):
                raise AuthenticatedControlShiftError(
                    'AuthenticatedControlShift requires parameter {}'
                    .format(attr))

        if 'token' in params:
            self._token = params['token']
        self.client_class = client_class
        self.debug = params.get('debug', False)

    def token_saver(self, token):
        """
        Override this method,
        if you have a place to save auth tokens in your application
        """
        if self.debug:
            print('SAVING TOKEN', token)

    def _token_save_inner(self, token):
        self._token = token
        self.token_saver(token)

    def session(self):
        if not self._session:
            def _save_token(token, inner=self):
                inner._token_save_inner(token)
            oauth_token_url = '{}/oauth/token'.format(self.base_url)
            if not self._token:
                client = self.client_class(client_id=self.client_id)
                oauth = OAuth2Session(client=client)
                token = oauth.fetch_token(
                    token_url=oauth_token_url,
                    client_id=self.client_id,
                    client_secret=self.client_secret)
                _save_token(token)

            client = self.client_class(client_id=self.client_id,
                                       token=self._token)
            self._session = OAuth2Session(
                self.client_id,
                token=self._token,
                client=client,
                auto_refresh_url=oauth_token_url,
                auto_refresh_kwargs={'client_id': self.client_id,
                                     'client_secret': self.client_secret},
                token_updater=_save_token)
        return self._session

    def get(self, path, **params):
        sess = self.session()
        return sess.get('{}{}'.format(self.base_url, path), params=params)

    def member_lookup(self, email):
        res = self.get('/api/v1/members/lookup', email=email)
        return res.json()
