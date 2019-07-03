# python-controlshift

Python library to interact with ControlShift application using their [Authenticated REST API](https://developers.controlshiftlabs.com/#authenticated-rest-api)

Similar to [basic example for ControlShift in Ruby](https://github.com/controlshift/oauth-api-example/blob/master/example.rb)

# Status

* Besides `member_lookup`, no custom functions yet
* Only `get(path, params)` -- i.e. no PUT, etc yet
* No good ratelimit support yet

## Basic use

```python
from controlshift.authenticated import AuthenticatedControlShift

csl = AuthenticatedControlShift(client_id='b53298.....',
                                client_secret='f897ea....',
                                base_url='https://demo.controlshiftlabs.com')

member_data = csl.member_lookup('member@example.com')
petition_data = csl.get('/api/v1/petitions/no-taxes-on-tea')

```

## settings mode (useful for e.g. Django)

```python

class settings:
    CONTROLSHIFT_CLIENT_ID = 'b53298.....'
    CONTROLSHIFT_CLIENT_SECRET = 'f897ea....'
    CONTROLSHIFT_BASEURL = 'https://demo.controlshiftlabs.com'
   
csl = AuthenticatedControlShift(settings=settings)

csl.member_lookup('member@example.com')

```

## Ratelimits

[Ratelimits are real](https://developers.controlshiftlabs.com/#rate-limits),
and you should think about how to manage/save tokens in your applications.

