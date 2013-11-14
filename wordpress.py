import json

from rauth import OAuth2Service, OAuth2Session


class WordpressSite:
    WPAPI_REST_URL = 'https://public-api.wordpress.com/rest/v1'
    WPAPI_ACCESS_TOKEN_URL = 'https://public-api.wordpress.com/oauth2/token'
    WPAPI_AUTHORIZE_URL = 'https://public-api.wordpress.com/oauth2/authorize'

    @staticmethod
    def obtain_access_token(client_id, client_secret, redirect_uri):
        wordpress = OAuth2Service(
            client_id=client_id,
            client_secret=client_secret,
            name='wordpress',
            authorize_url=WordpressSite.WPAPI_AUTHORIZE_URL,
            access_token_url=WordpressSite.WPAPI_ACCESS_TOKEN_URL)
        params = {'response_type': 'code',
                  'redirect_uri': redirect_uri}
        authorize_url = wordpress.get_authorize_url(**params)

        print('Open this URL in the browser, if necessary log into Wordpress, and authorize the app. \
A redirect to {} will happen, with a query parameter code=<CODE>. \
Copy <CODE> and paste it to the prompt below.')
        print(authorize_url)
        code = input('code: ')

        access_token = wordpress.get_access_token(data={'code': code,
                                                        'redirect_uri': redirect_uri,
                                                        'grant_type': 'authorization_code'},
                                                  decoder=lambda response: json.loads(response.decode('utf-8')))

        return access_token


    def __init__(self, client_id, client_secret, site_url, access_token):
        self.client_id = client_id
        self.client_secret = client_secret
        self.site_url = site_url
        self.access_token = access_token

        self.session = OAuth2Session(
            client_id,
            client_secret,
            access_token=self.access_token)

    def _site_url(self):
        return 'https://public-api.wordpress.com/rest/v1/sites/{}'.format(self.site_url)

    def add_category(self, name, description):
        response = self.session.post(
            url=self._site_url() + '/categories/new',
            params={},
            data={
                'name': name,
                'description': description
            }
        )

        if not response.status_code in [200, 403]:
            raise RuntimeError(response.json()['message'])

    def get_site_info(self):
        response = self.session.get(url=self._site_url())

        if not response.status_code in [200]:
            raise RuntimeError(response.json()['message'])
        else:
            return response.json()
