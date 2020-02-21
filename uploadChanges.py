import argparse
import json

import requests

"""
This script uploads content to the defined register
  ./prodRegister

This reqires an authentication token and userID and structured
content.

The structured content is taken from the command line argument which
shall consist of a dictionary with the keys:
  'PUT', 'POST'
and each key shall provide a list of .ttl files to upload to prodRegister
based on the relative path of the .ttl file.

"""

def authenticate(session, base, userid, pss):
    auth = session.post('{}/system/security/apilogin'.format(base),
                        data={'userid':userid,
                                'password':pss})
    if not auth.status_code == 200:
        raise ValueError('auth failed')

    return session

def parse_uploads(uploads):
    result = json.loads(uploads)
    if set(result.keys()) != set(('PUT', 'POST')):
        raise ValueError("Uploads inputs should have keys"
                         " set(('PUT', 'POST')) only, not:\n"
                         "{}".format(result.keys()))
    return result

def post(session, url, payload):
    headers={'Content-type':'text/turtle'}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        raise ValueError('Cannot POST to {}, it exists.'.format(url))
    params = {'status':'Experimental'}
    res = session.post(url, headers=headers, data=payload, params=params)
    if res.status_code != 201:
        print('POST failed with {}\n{}'.format(res.status_code, res.reason))

def put(session, url, payload):
    headers={'Content-type':'text/turtle'}
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        raise ValueError('Cannot PUT to {}, it does not exist.'.format(url))
    res = session.post(url, headers=headers, data=payload)

def post_uploads(session, rootURL, uploads):
    for postfile in uploads:
        with open('.{}'.format(postfile), 'r') as pf:
            pdata = pf.read()
        url = '{}{}'.format(rootURL, postfile.rstrip('.ttl'))
        print(url)
        post(session, url, pdata)

if __name__ == '__main__':
    with open('prodRegister', 'r') as fh:
        rooturl = fh.read().split('\n')[0]
        print('Running test with respect to {}'.format(rooturl))

    parser = argparse.ArgumentParser()
    parser.add_argument('user_id')
    parser.add_argument("passcode")
    parser.add_argument('uploads')
    args = parser.parse_args()
    session = requests.Session()
    uploads = parse_uploads(args.uploads)
    session = authenticate(session, rooturl, args.user_id, args.passcode)
    print(uploads)
    post_uploads(session, rooturl, uploads['POST'])
    
