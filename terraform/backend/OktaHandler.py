import urllib.parse
import urllib.request
import json
import logging


class OktaConnector:
    def __init__(self, token: str, organization_name: str):
        self.token = token
        self.base_url = "https://{}.okta.com".format(organization_name)

    def __get_user_id(self, email_address: str) -> str:
        endpoint = "/api/v1/users/{}".format(email_address)
        params = {
            "limit": 1
        }
        request_headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': 'SSWS {}'.format(self.token)
        }
        request = urllib.request.Request(
            url="{}{}?{}".format(self.base_url, endpoint, urllib.parse.urlencode(params)),
            headers=request_headers
        )
        with urllib.request.urlopen(request) as response:
            if response.getcode() == 200:
                response_data = json.loads(response.read())
                return response_data.get("id")
            else:
                logging.error("OktaConnector.__get_user_id: {}".format(response.read()))
                return ""

    def get_user_aws_groups(self, email_address: str) -> list[str]:
        endpoint = "/api/v1/users/{}/groups".format(self.__get_user_id(email_address=email_address))
        request_headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': 'SSWS {}'.format(self.token)
        }
        request = urllib.request.Request("{}{}".format(self.base_url, endpoint), headers=request_headers)
        with urllib.request.urlopen(request) as response:
            if response.getcode() == 200:
                groups = []
                for group in json.loads(response.read()):
                    if group.get("profile").get("name").startswith("aws_"):
                        groups.append(group.get("profile").get("name"))
                return groups
            else:
                logging.error("OktaConnector.get_user_aws_groups: {}".format(response.read()))
                return []
