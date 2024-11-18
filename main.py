
from pydantic import BaseModel
import os
import logging
import datetime
from openai import OpenAI, APIError,APIConnectionError,RateLimitError
import requests
import time

from slack_sdk.errors import SlackApiError

logging.basicConfig(level=logging.DEBUG)
from slack_sdk import WebClient

#get token
client = WebClient(token=os.environ.get('TOKEN'))


#define create github issue
def make_issue(title,body,owner,repos):
    url = f"https://api.github.com/repos/{owner}/{repos}/issues"
    headers = {
        "Authorization": f"Bearer {os.environ.get('Git_key')}",
        "Accept": "application/vnd.github.v3+json"
    }
    data = {
        "title": title,
        "body": body
    }
    GitResponse = requests.post(url, headers=headers, json=data)
    if GitResponse.status_code == 201:
        print("issue created!!", GitResponse.json()["html_url"])
    else:
        print("Failed to create issue:", GitResponse.status_code, GitResponse.json)


#get conversation
current_date = time.mktime(datetime.datetime.now().timetuple())
oldest_date = time.mktime((datetime.datetime.now()-datetime.timedelta(days=7)).timetuple())
try:
    result = client.conversations_history(channel='C07ST032SH3',oldest= str(oldest_date),latest = str(current_date))

    #getting message
    final_message = []
    message_text = [msg['text'] for msg in result['messages'] if 'text' in msg]
    count = 0
    for line in message_text:
        if line != "":
            if line[0] != '<':
                count += 1
                final_message.append(str(count)+line)
    str_final_message =""
    for index in range(len(final_message)):
        str_final_message = str_final_message+final_message[index] +"/n"
except SlackApiError as e:
    assert e.response["error"]

#sending to LLM
class GithubIssue(BaseModel):
    Title: str
    Description: str
openaiclient = OpenAI(api_key=os.environ.get('openai_key'))
try:
    # noinspection PyUnboundLocalVariable
    response = openaiclient.beta.chat.completions.parse(model="gpt-4o-mini-2024-07-18",messages=[
        {
            "role": "system",
            "content": "You will be provided with unstructured data of suggestion comments about a new application, and your task is to create a git hub issue from these comments with a Title and Description in markdown format. "
        },
        {
            "role": "user",
            "content":str_final_message
        }
    ],response_format=GithubIssue,
    )
    message = response.choices[0].message.parsed
    make_issue(message.Title,message.Description,"fawwaz1123","suggestor")

except APIConnectionError as e:
  #Handle connection error here
  print(f"Failed to connect to OpenAI API: {e}")
  pass
except APIError as e:
  #Handle API error here, e.g. retry or log
  print(f"OpenAI API returned an API Error: {e}")
  pass
except RateLimitError as e:
  #Handle rate limit error (we recommend using exponential backoff)
  print(f"OpenAI API request exceeded rate limit: {e}")
  pass

#define create github issue
def make_issue(title,body,owner,repos):
    url = f"https://api.github.com/repos/{owner}/{repos}/issues"
    headers = {
        "Authorization": f"Bearer {os.environ.get('Git_key')}",
        "Accept": "application/vnd.github.v3+json"
    }
    data = {
        "title": title,
        "body": body
    }
    GitResponse = requests.post(url, headers=headers, json=data)
    if GitResponse.status_code == 201:
        print("issue created!!", GitResponse.json()["html_url"])
    else:
        print("Failed to create issue:", GitResponse.status_code, GitResponse.json)

