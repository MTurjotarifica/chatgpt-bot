from flask import Flask, request, make_response, redirect, render_template
import json
from slack_bolt import App
from slackeventsapi import SlackEventAdapter
from slack_sdk.errors import SlackApiError
from slack_bolt.adapter.flask import SlackRequestHandler
from slack_sdk import WebClient
import os
import openai
from dotenv import load_dotenv 
from pathlib import Path  
import requests 

load_dotenv()

app = Flask(__name__)

slack_app = App(
    token=os.environ["SLACK_BOT_TOKEN"],
    signing_secret=os.environ["SLACK_SIGNING_SECRET"]
)

slack_client = slack_app.client
client = slack_app.client

slack_client_id = os.environ["SLACK_CLIENT_ID"]
slack_client_secret = os.environ["SLACK_CLIENT_SECRET"]

openai.api_key = os.environ["OPENAI_API_KEY"]

# ... your existing routes and code ...

@app.route('/slack/callback', methods=['GET', 'POST'])
def slack_callback():
    code = request.args.get('code')
    state = request.args.get('state')

    # Make a request to exchange the code for an access token
    response = requests.post(
        'https://slack.com/api/oauth.v2.access',
        params={
            'code': code,
            'client_id': slack_client_id,
            'client_secret': slack_client_secret
        }
    )

    if response.status_code == 200:
        # Access token obtained successfully
        access_token = response.json()['access_token']
        # Process the access token as needed
        # ...
        # Redirect the user to the desired page after authentication
        return redirect('/success')
    else:
        # Error handling for token exchange failure
        # ...
        # Redirect the user to an error page
        return redirect('/error')

# ... your existing code ...

if __name__ == "__main__":
    app.run(debug=True)
