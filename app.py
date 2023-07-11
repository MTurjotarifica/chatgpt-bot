from flask import Flask, request, make_response, redirect
from slack_bolt import App
from slack_sdk.oauth.installation_store import FileInstallationStore
from slack_sdk.oauth.state_store import FileOAuthStateStore
from slack_sdk import WebClient
import os
import openai
from dotenv import load_dotenv 
from pathlib import Path   

load_dotenv()

# Initialize the Flask app and the Slack app
app = Flask(__name__)

# Create instances of the installation and state stores
installation_store = FileInstallationStore()
oauth_state_store = FileOAuthStateStore(expiration_seconds=300, base_dir="./oauth_state")

slack_app = App(
    token=os.environ["SLACK_BOT_TOKEN"],
    signing_secret=os.environ["SLACK_SIGNING_SECRET"],
    installation_store=installation_store,
    # oauth_state_store=oauth_state_store
)

slack_client = WebClient(token=None, installation_store=installation_store)
client = slack_client

# Set up the OpenAI API key
openai.api_key = os.environ["OPENAI_API_KEY"]

@app.route('/slack/interactive-endpoint', methods=['GET','POST'])
def interactive_trigger():
    data = request.form
    data2 = request.form.to_dict()
    channel_id = json.loads(data2['payload'])['container']['channel_id']
    action_id = json.loads(data2['payload'])['actions'][0]['action_id']
    
    if action_id == "chatgpt":
        command_text = json.loads(data2['payload'])['actions'][0]['value']
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=command_text,
            max_tokens=60,
            n=1,
            stop=None,
            temperature=0.8,
        )
        
        try:
            client.chat_postMessage(
                channel=channel_id,
                text=response.choices[0].text
            )
        except SlackApiError as e:
            print(f"Error sending message: {e}")
        
        return make_response("", 200)


@app.route("/chatgpt", methods=["POST"])
def handle_chatgpt():
    data = request.form
    channel_id = data.get('channel_id')

    gptquery = [
        {
           "type": "divider"
        },
        {
            "dispatch_action": True,
            "type": "input",
            "element": {
                "type": "plain_text_input",
                "action_id": "chatgpt"
            },
            "label": {
                "type": "plain_text",
                "text": "Please type the keyword for the Chatgpt",
                "emoji": True
            }
        }
    ]

    client.chat_postMessage(channel=channel_id, 
                            text="Query:  ",
                            blocks = gptquery
    )

    return '', 200

@app.route("/hello3", methods=["POST"])
def handle_hello_request():
    data = request.form
    channel_id = data.get('channel_id')
    client.chat_postMessage(response_type= "in_channel", channel=channel_id, text=" 2nd it works!33!" )
    return "Hello world3", 200

# OAuth installation endpoint
@app.route("/slack/install", methods=["GET"])
def install():
    try:
        callback_url = request.base_url + "/callback"
        return redirect(slack_app.oauth.install_url(callback_url=callback_url))
    except Exception as e:
        return make_response("Installation failed", 500)

# OAuth callback endpoint
@app.route("/slack/install/callback", methods=["GET"])
def callback():
    try:
        if "code" in request.args:
            oauth_response = slack_app.oauth.v2_access(
                code=request.args["code"],
                callback_url=request.base_url
            )
            # Store the installation details, including the access token
            installation_store.save(installation=oauth_response["installation"])
            return make_response("Installation successful!")
        else:
            return make_response("Authorization denied")
    except Exception as e:
        return make_response("Callback failed", 500)

if __name__ == "__main__":
    app.run(debug=True)
