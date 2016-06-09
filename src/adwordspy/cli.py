"""
Module that contains the command line app.

Why does this file exist, and why not put this in __main__?

  You might be tempted to import things from __main__ later, but that will cause
  problems: the code will get executed twice:

  - When you run `python -madwordspy` python will execute
    ``__main__.py`` as a script. That means there won't be any
    ``adwordspy.__main__`` in ``sys.modules``.
  - When you import __main__ it will get executed again (as a module) because
    there's no ``adwordspy.__main__`` in ``sys.modules``.

  Also see (1) from http://click.pocoo.org/5/setuptools/#setuptools-integration
"""
from __future__ import print_function

import sys

from oauth2client import client


def main(argv=sys.argv):
    """
        Retrieve and display the access and refresh token.
    """
    if len(argv) < 3:
        print('CLIENT_ID or CLIENT_SECRET is missing')
        return 0

    client_id = argv[1]
    client_secret = argv[2]
    flow = client.OAuth2WebServerFlow(
        client_id=client_id,
        client_secret=client_secret,
        scope=['https://www.googleapis.com/auth/adwords'],
        user_agent='Ads Python Client Library',
        redirect_uri='urn:ietf:wg:oauth:2.0:oob')

    authorize_url = flow.step1_get_authorize_url()

    print('Log into the Google Account you use to access your AdWords account'
          'and go to the following URL: \n{}\n'.format(authorize_url))
    print('After approving the token enter the verification code (if specified).')
    code = input('Code: ').strip()

    try:
        credential = flow.step2_exchange(code)
    except client.FlowExchangeError as e:
        print('Authentication has failed: {}'.format(e))
        sys.exit(1)
    else:
        print('OAuth 2.0 authorization successful!\n\n'
              'Your access token is:\n {}\n\nYour refresh token is:\n {}'.format(
                credential.access_token, credential.refresh_token))
