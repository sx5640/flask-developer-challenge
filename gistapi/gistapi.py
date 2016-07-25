# coding=utf-8
"""
Exposes a simple HTTP API to search a users Gists via a regular expression.

Github provides the Gist service as a pastebin analog for sharing code and
other develpment artifacts.  See http://gist.github.com for details.  This
module implements a Flask server exposing two endpoints: a simple ping
endpoint to verify the server is up and responding and a search endpoint
providing a search across all public Gists for a given Github account.
"""

import requests
from flask import Flask, jsonify, request
import re
from werkzeug.contrib.cache import SimpleCache
cache = SimpleCache()
cache.clear()



# *The* app object
app = Flask(__name__)


@app.route("/ping")
def ping():
    """Provide a static response to a simple GET request."""
    return "pong"


def gists_for_user(username, page_number = 1):
    """Provides the list of gist metadata for a given user.

    This abstracts the /users/:username/gist endpoint from the Github API.
    See https://developer.github.com/v3/gists/#list-a-users-gists for
    more information.

    Args:
        username (string): the user to query gists for

    Returns:
        The dict parsed from the json response from the Github API.  See
        the above URL for details of the expected structure.
    """
    gists_url = 'https://api.github.com/users/{username}/gists?page={page_number}&per_page=10'.format(
            username=username, page_number=page_number)
    response = requests.get(gists_url)
    # BONUS: What failures could happen?


    # BONUS: Paging? How does this work for users with tons of gists?
    # the function is modified to include paging. the user now have the option to also input a page number.
    # if the page number is not found in the input, the function will return page 1 by default
    # each page will contains 1-10 gists

    return response.json()


@app.route("/api/v1/search", methods=['POST'])
def search():
    """Provides matches for a single pattern across a single users gists.

    Pulls down a list of all gists for a given user and then searches
    each gist for a given regular expression.

    Returns:
        A Flask Response object of type application/json.  The result
        object contains the list of matches along with a 'status' key
        indicating any failure conditions.
    """
    post_data = request.get_json()

    result = {}


    # BONUS: Validate the arguments?
    # if there is no username or pattern given, return status failure
    if ('username' not in post_data.keys()) | ('pattern' not in post_data.keys()):
        result['status'] = 'failure'
        result['errormessage'] = 'missing username or pattern to match'
        return jsonify(result)


    username = post_data['username']
    pattern = post_data['pattern']

    gists = gists_for_user(username)
    # BONUS: Handle invalid users?
    if type(gists) == dict:
        result['status'] = 'failure'
        result['errormessage'] = gists['message']
        return jsonify(result)

    # at this point, we are getting some gist from the API, so status should be set to success.
    result['status'] = 'success'
    result['username'] = username
    result['pattern'] = pattern
    # first assume we found nothing
    result['matches'] = []

    # REQUIRED: Fetch each gist and check for the pattern
    for gist in gists:
        # search every file contained in the gist and look for the pattern
        files = gist['files']
        for file_name in files.keys():

            # send a get request to the url of the gist text,
            text_url = files[file_name]['raw_url']
            response = requests.get(text_url).text
            # pattern matching
            m = re.search(pattern, response)
            # if there is a match, return the matched string
            if m:
                result['matches'] += ['https://gist.github.com/{username}/{id}'.format(
                username = username, id = gist['id']
                )]


                # BONUS: What about huge gists?

                # BONUS: Can we cache results in a datastore/db?
                rv = cache.get(pattern)
                if rv is None:
                    rv = result
                    cache.set(pattern, rv, timeout=5 * 60)


    return jsonify(result)

# adding a route only for testing the caching functionality
@app.route("/cache", methods=['POST'])
def search_cache():
    post_data = request.get_json()
    if 'pattern' not in post_data.keys():
        result['status'] = 'failure'
        result['errormessage'] = 'search_cache: pattern not inputted'
        return jsonify(result)

    pattern = post_data['pattern']
    result = cache.get(pattern)

    if result:
        return jsonify(result)
    else:
        result = {}
        result['status'] = 'failure'
        result['errormessage'] = 'search_cache: pattern not found'
        return jsonify(result)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8000)
