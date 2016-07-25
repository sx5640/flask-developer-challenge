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
import pdb
import re


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
    result['matches'] = []

    # BONUS: Validate the arguments?
    if (not post_data['username']) & (not post_data['pattern']):
        result['status'] = 'failure'
        result['errormessage'] = 'missing username or pattern to match'
        return jsonify(result)

    username = post_data['username']
    pattern = post_data['pattern']

    gists = gists_for_user(username)
    # BONUS: Handle invalid users?

    for gist in gists:
        # REQUIRED: Fetch each gist and check for the pattern
        # search every file contained in the gist and
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


    result['status'] = 'success'
    result['username'] = username
    result['pattern'] = pattern


    return jsonify(result)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8000)
