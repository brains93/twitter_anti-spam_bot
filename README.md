# Twitter reply bot
This bot will pull a stream of tweets based on rules you set and automatically reply to them. 

I built this bot in order to help combat scam bots in twitter, I am using this to look for the scam messages on the Tiktok support page and warn the original poster that it may be a scam.

## Setup
In order to use this bot you will need to have a Twitter developer account, this can be requested from here https://developer.twitter.com/


once made you will need your API key, secret and generate a Bearer token. 
The bearer token is used to pull down the livestream of tweets but in order to post tweets it also requires the API key and Secret 

this code only requires one module install but to ensure you have the correct version I recommend installing from the requirements file using the command below

```
python -m pip install -r requirements.txt
```

When you run the code it will provide a Twitter authorisation link and ask for a pin. When going to this link it will prompt you to allow the app access to the twitter account. This is how it authenticates for posting the reply's and it will use the account you authorise for the posts. 
This prompt will happen every time you run the code allowing to to easily change which account posts the replies. 

#### NOTE: make sure to check which account you are authorising to post. I have accidentally used my personal account while testing this by not paying attention at this stage 


## Setting rules
The bot will reply to any message that match on the rules list within the code (This is under the Main function at the bottom)

Below is the rule set that I used to test against the Tiktok Support twitter looking for scam messages 
```
  sample_rules = [
        {"value": "TikTokSupport DM Instagram -from:cybersafetybot1"},
        {"value": "TikTokSupport on Instagram helped me -from:cybersafetybot1"},
        {"value": "TikTokSupport via IG -from:cybersafetybot1"},
        {"value": "TikTokSupport inbox recover -from:cybersafetybot1"},
        {"value": "TikTokSupport referred to unbanned -from:cybersafetybot1"},
        {"value": "TikTokSupport send a message to -from:cybersafetybot1"},
        {"value": "TikTokSupport recovered my account for me -from:cybersafetybot1"},
        {"value": "TikTokSupport my account got same issues -from:cybersafetybot1"},
    ]
```

The each line is a separate rule and works independantly from each other. the stream will find tweets that contain any of the words within the value section. the flag -from:cybersafteybot1 means that it will ignore messaged from the account CyberSafteybot1 
Ensure to add your account into this field so that the bot doesnt flag your replies. For more information on Rule Operators and constructs see here https://developer.twitter.com/en/docs/twitter-api/tweets/filtered-stream/integrate/build-a-rule



