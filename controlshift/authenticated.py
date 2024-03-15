import requests
from requests_oauthlib import OAuth2Session
from oauthlib.oauth2 import BackendApplicationClient, TokenExpiredError


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

        self.client_class = client_class
        self.debug = params.get('debug', False)

    def refresh_token(self):
        oauth_token_url = '{}/oauth/token'.format(self.base_url)
        client = self.client_class(client_id=self.client_id)
        oauth = OAuth2Session(client=client)
        self._token = oauth.fetch_token(
            token_url=oauth_token_url,
            client_id=self.client_id,
            client_secret=self.client_secret)

    def create_session(self):
        client = self.client_class(client_id=self.client_id, token=self._token)
        session = OAuth2Session(self.client_id, token=self._token, client=client)
        return session

    def get(self, path, **params):
        if not self._token:
            self.refresh_token()
        session = self.create_session()
        try:
            r = session.get('{}{}'.format(self.base_url, path), params=params)
        except (TokenExpiredError, ConnectionError) as e:
            print(e)
            self.refresh_token()
            session = self.create_session()
            r = session.get('{}{}'.format(self.base_url, path), params=params)
        return r

    def member_lookup(self, email):
        res = self.get('/api/v1/members/lookup', email=email)
        return res.json()

    def petition(self, slug, authenticated=True):
        """
        returns data about a petition. We need to get a hybrid of info from
        authenticated and unauthenticated sources (e.g. 'id' is only in unauthenticated)
        Passing authenticated=False will just get the public one
        -- useful to reduce ratelimited API calls
        """
        data = {'petition': {}}
        unauthenticated = requests.get('{}/petitions/{}.json'.format(self.base_url, slug))
        if unauthenticated.status_code == 200:
            data['petition'].update(unauthenticated.json())

        if authenticated:
            res = self.get('/api/v1/petitions/{}'.format(slug))
            if res.status_code != 200:
                return {'error': 'request error', 'res': res}
            authenticated_data = res.json()
            if authenticated_data and authenticated_data.get('petition'):
                data['petition'].update(authenticated_data['petition'])
        return data
