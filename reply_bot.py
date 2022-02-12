from requests_oauthlib import OAuth1Session
import requests
import os
import json

# To set your enviornment variables in Linux run the following line:
# export 'BEARER_TOKEN'='<your_bearer_token>'
# export 'CONSUMER_KEY'='<your_consumer_key>'
# export 'CONSUMER_SECRET'='<your_consumer_secret>'
# For Windows run:
# $env:BEARER_TOKEN = '<your_bearer_token>'
consumer_key = os.environ.get("CONSUMER_KEY")
consumer_secret = os.environ.get("CONSUMER_SECRET")
bearer_token = os.environ.get("BEARER_TOKEN")

# Get request token
def get_oauth(consumer_key, consumer_secret):
    '''
    Oauth authentication requrired to Post tweets via the Twitter API 
    INPUT
    consumer_key: Your Twitter API key  
    consumer_secret: Your Twitter API secret 
    '''

    request_token_url = "https://api.twitter.com/oauth/request_token?oauth_callback=oob&x_auth_access_type=write"
    oauth = OAuth1Session(consumer_key, client_secret=consumer_secret)

    try:
        fetch_response = oauth.fetch_request_token(request_token_url)
    except ValueError:
        print(
            "There may have been an issue with the consumer_key or consumer_secret you entered."
        )

    resource_owner_key = fetch_response.get("oauth_token")
    resource_owner_secret = fetch_response.get("oauth_token_secret")
    print("Got OAuth token: %s" % resource_owner_key)

    # Get authorization
    base_authorization_url = "https://api.twitter.com/oauth/authorize"
    authorization_url = oauth.authorization_url(base_authorization_url)
    print("Please go here and authorize: %s" % authorization_url)
    verifier = input("Paste the PIN here: ")

    # Get the access token
    access_token_url = "https://api.twitter.com/oauth/access_token"
    oauth = OAuth1Session(
        consumer_key,
        client_secret=consumer_secret,
        resource_owner_key=resource_owner_key,
        resource_owner_secret=resource_owner_secret,
        verifier=verifier,
    )
    oauth_tokens = oauth.fetch_access_token(access_token_url)

    access_token = oauth_tokens["oauth_token"]
    access_token_secret = oauth_tokens["oauth_token_secret"]

    # Make the request
    oauth = OAuth1Session(
        consumer_key,
        client_secret=consumer_secret,
        resource_owner_key=access_token,
        resource_owner_secret=access_token_secret,
    )
    return oauth

def bearer_oauth(r):
    """
    Method required by bearer token authentication.
    """
    r.headers["Authorization"] = f"Bearer {bearer_token}"
    r.headers["User-Agent"] = "v2FilteredStreamPython"
    return r

def reply(message, id, oauth):
    '''
    Replys to the given tweet
    INPUT 
    message: The message you want to post
    id: The ID of the tweet you wish to reply to 
    oauth: this uses the get_oauth function to authenticate to twitter

    '''
    payload = {"text": message,"reply":{"in_reply_to_tweet_id":id}}
    response = oauth.post(
        "https://api.twitter.com/2/tweets",
        json=payload,
    )

    if response.status_code != 201:
        print(
            "Request returned an error: {} {}".format(response.status_code, response.text)
        )

    print("Response code: {}".format(response.status_code))

    # Saving the response as JSON
    json_response = response.json()
    print(json.dumps(json_response, indent=4, sort_keys=True))

def get_rules():
    '''
    Gets the current twitter stream rules you have in place
    uses the bearer_oauth function to authenticate 
    OUTPUT: Json dict of current rules
    '''
    response = requests.get(
        "https://api.twitter.com/2/tweets/search/stream/rules", auth=bearer_oauth
    )
    if response.status_code != 200:
        raise Exception(
            "Cannot get rules (HTTP {}): {}".format(response.status_code, response.text)
        )
    print(json.dumps(response.json()))
    return response.json()


def delete_all_rules(rules):
    '''
    Deletes the exisitng rules for your twitter stream filter. This keeps the rules clean
    INPUT
    rules: Json output from the get_rules function
    '''
    if rules is None or "data" not in rules:
        return None

    ids = list(map(lambda rule: rule["id"], rules["data"]))
    payload = {"delete": {"ids": ids}}
    response = requests.post(
        "https://api.twitter.com/2/tweets/search/stream/rules",
        auth=bearer_oauth,
        json=payload
    )
    if response.status_code != 200:
        raise Exception(
            "Cannot delete rules (HTTP {}): {}".format(
                response.status_code, response.text
            )
        )
    print(json.dumps(response.json()))


def set_rules(delete, rules):
    '''
    Sets the rules for the twitter stream
    INPUT
    delete: passes the delete_all_rules function to clear the stored rules before posting new ones
    rules: a list of dicts containing the filter rules for the twitter stream
    '''
    payload = {"add": rules}
    response = requests.post(
        "https://api.twitter.com/2/tweets/search/stream/rules",
        auth=bearer_oauth,
        json=payload,
    )
    if response.status_code != 201:
        raise Exception(
            "Cannot add rules (HTTP {}): {}".format(response.status_code, response.text)
        )
    print(json.dumps(response.json()))


def get_stream(set, oauth, message):
    '''
    Starts a realtime stream of tweets that match on your rules
    INPUT
    set: takes the set_rules output to setup rules
    oauth: bearer token oauth to get the twitter stream
    message: the message you want to reply to the tweet this is passed to the Reply function 
    OUPUT
    streams any Tweets that match on your rules. 

    '''
    response = requests.get(
        "https://api.twitter.com/2/tweets/search/stream", auth=bearer_oauth, stream=True,
    )
    print(response.status_code)
    if response.status_code != 200:
        raise Exception(
            "Cannot get stream (HTTP {}): {}".format(
                response.status_code, response.text
            )
        )
    for response_line in response.iter_lines(): # Here is where the information on each tweet can be pulled out Tweet ID for example
        if response_line:
            json_response = json.loads(response_line)
            message_id = json_response["data"]["id"]
            print(json.dumps(json_response, indent=4, sort_keys=True))
            reply(message, message_id, oauth) # replys to any tweets which come in via the stream 


def main():

    # Message you want to send as a reply 
    message = "The Above message may be a scam. Please do not try to recover accounts via 'hackers' they are usually scams"

    # below are some sample rules. it will match if the tweet contains any words of each line. 
    # The -from operator indicates to ignore tweets from the account specified after it
    sample_rules = [
        #################################
        ##INSERT RULES HERE. SEE README##
        #################################
    ]
    oauth = get_oauth(consumer_key, consumer_secret) # generates the Oauth required to send a tweet
    rules = get_rules() # gets current stored rules
    delete = delete_all_rules(rules) # deletes stored rules to ensure a clean stream each time
    set = set_rules(delete, sample_rules) # sets filter rules with the above list
    stream = get_stream(set, oauth, message) # starts stream and replys to any matching tweets


if __name__ == "__main__":
    main()
