import urllib
import urllib.parse
import urllib.request
import json


def parse_slack_url(slack_url: str) -> dict:
    return urllib.parse.parse_qs(slack_url)


def response_to_slack(response_url: str, text: str):
    payload = {
        "text": text
    }
    request = urllib.request.Request(url=response_url, data=bytes(json.dumps(payload), encoding='utf-8'), method='POST')
    urllib.request.urlopen(request)
