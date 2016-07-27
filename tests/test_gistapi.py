import os
import json
import tempfile

import pytest

import gistapi


@pytest.fixture
def client(request):
    #db_fd, gistapi.app.config['DATABASE'] = tempfile.mkstemp()
    gistapi.app.config['TESTING'] = True
    client = gistapi.app.test_client()

    #with gistapi.app.app_context():
    #    gistapi.init_db()

    #def teardown():
    #    os.close(db_fd)
    #    os.unlink(flaskr.app.config['DATABASE'])
    #request.addfinalizer(teardown)

    return client


def test_ping(client):
    """Start with a sanity check."""
    rv = client.get('/ping')
    assert b'pong' in rv.data


def test_search(client):
    """Start with a passing test."""
    post_data = {'username': 'justdionysus', 'pattern': 'TerbiumLabsChallenge_[0-9]+'}
    rv = client.post('/api/v1/search',
                     data=json.dumps(post_data),
                     headers={'content-type':'application/json'})
    result_dict = json.loads(rv.data.decode('utf-8'))
    expected_dict = {'status': 'success',
                     'username': 'justdionysus',
                     'pattern': 'TerbiumLabsChallenge_[0-9]+',
                     'matches': ['https://gist.github.com/justdionysus/6b2972aa971dd605f524']}
    assert result_dict == expected_dict

def test_search(client):
    """Start with a passing test."""
    post_data = {'username': 'justdionysus', 'pattern': 'abcdefg'}
    rv = client.post('/api/v1/search',
                     data=json.dumps(post_data),
                     headers={'content-type':'application/json'})
    result_dict = json.loads(rv.data.decode('utf-8'))
    expected_dict = {'status': 'success',
                     'username': 'justdionysus',
                     'pattern': 'abcdefg',
                     'matches': []}
    assert result_dict == expected_dict

def test_validation_username(client):
    """validation test on username."""
    post_data = {'pattern': 'TerbiumLabsChallenge_[0-9]+'}
    rv = client.post('/api/v1/search',
                     data=json.dumps(post_data),
                     headers={'content-type':'application/json'})
    result_dict = json.loads(rv.data.decode('utf-8'))
    expected_dict = {'status': 'failure',
                     'errormessage': 'missing username or pattern to match'}
    assert result_dict == expected_dict

def test_validation_pattern(client):
    """validation test on pattern."""
    post_data = {'username': 'justdionysus'}
    rv = client.post('/api/v1/search',
                     data=json.dumps(post_data),
                     headers={'content-type':'application/json'})
    result_dict = json.loads(rv.data.decode('utf-8'))
    expected_dict = {'status': 'failure',
                     'errormessage': 'missing username or pattern to match'}
    assert result_dict == expected_dict

def test_validation_both(client):
    """validation test on username and pattern."""
    post_data = {}
    rv = client.post('/api/v1/search',
                     data=json.dumps(post_data),
                     headers={'content-type':'application/json'})
    result_dict = json.loads(rv.data.decode('utf-8'))
    expected_dict = {'status': 'failure',
                     'errormessage': 'missing username or pattern to match'}
    assert result_dict == expected_dict

def test_invalid_username(client):
    """invalid username test."""
    post_data = {'username': '', 'pattern': 'TerbiumLabsChallenge_[0-9]+'}
    rv = client.post('/api/v1/search',
                     data=json.dumps(post_data),
                     headers={'content-type':'application/json'})
    result_dict = json.loads(rv.data.decode('utf-8'))
    expected_dict = {'status': 'failure',
                     'errormessage': 'Not Found'}
    assert result_dict == expected_dict


def test_cache(client):
    """cache test."""
    post_data = {'username': 'justdionysus', 'pattern': 'TerbiumLabsChallenge_[0-9]+'}
    rv = client.post('/api/v1/search',
                     data=json.dumps(post_data),
                     headers={'content-type':'application/json'})
    result_dict = json.loads(rv.data.decode('utf-8'))
    expected_dict = {'status': 'success',
                     'username': 'justdionysus',
                     'pattern': 'TerbiumLabsChallenge_[0-9]+',
                     'matches': ['https://gist.github.com/justdionysus/6b2972aa971dd605f524'],
                     'cache': True}
    assert result_dict == expected_dict
