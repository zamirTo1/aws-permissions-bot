import urllib.parse
import urllib.request
import base64
import json
import logging


class JiraConnector:
    """
    A class used to represent a Jira Connector

   ...

   Attributes
   ----------
   user : str
       a formatted string to represent the user
   token : str
       a formatted string to represent the token
   base_url : str
       a formatted string to represent the base url of Jira API

   Methods
   -------
   create_new_issue(payload: dict) -> str:
       Creates a new issue in Jira
   build_jira_ticket(project_key: str, issue_type: str, assignee_id: str, assignee_mention: str, service_name: str, resource_name: str, permission_level: str, account_name: str, github_pull_request_url: str):
       Builds the payload for a Jira ticket
   get_user_id_by_email_address(email_address: str) -> str:
       Gets the user id by email address
   """

    def __init__(self, user: str, token: str, jira_organization_name: str):
        """
        Constructs all the necessary attributes for the JiraConnector object.

        Parameters
        ----------
            user : str
                user's username
            token : str
                user's token
        """
        self.user = user
        self.token = token
        self.base_url = 'https://{}.atlassian.net/rest/api/3'.format(jira_organization_name)

    def create_new_issue(self, payload: dict) -> str:
        """
        Creates a new issue in Jira.

        Parameters
        ----------
            payload : dict
                The payload for the new issue

        Returns
        -------
            str
                The key of the created issue if successful, empty string otherwise
        """
        endpoint = "/issue"
        request_headers = {
            'Content-Type': 'application/json',
            'Authorization': "Basic {}".format(base64.b64encode("{}:{}".format(self.user, self.token).encode('utf-8')).decode('utf-8'))
        }
        try:
            request = urllib.request.Request(url="{}{}".format(self.base_url, endpoint), headers=request_headers, data=bytes(json.dumps(payload), encoding='utf-8'), method='POST')
            with urllib.request.urlopen(request) as response:
                if response.getcode() == 201:
                    jira_issue_key = json.loads(response.read()).get("key")
                    return jira_issue_key
                else:
                    logging.error("JiraConnector.create_new_issue: {}".format(response.read()))
                    return ""
        except Exception as e:
            logging.error("JiraConnector.create_new_issue: {}".format(e))
            return ""

    @staticmethod
    def build_jira_ticket(
        project_key: str,
        issue_type: str,
        assignee_id: str,
        assignee_mention: str,
        service_name: str,
        resource_name: str,
        permission_level: str,
        account_name: str,
        github_pull_request_url: str
    ):
        """
        Builds the payload for a Jira ticket.

        Parameters
        ----------
            project_key : str
                The key of the project
            issue_type : str
                The type of the issue
            assignee_id : str
                The id of the assignee
            assignee_mention : str
                The mention of the assignee
            service_name : str
                The name of the service
            resource_name : str
                The name of the resource
            permission_level : str
                The level of the permission
            account_name : str
                The name of the account
            github_pull_request_url : str
                The url of the GitHub pull request

        Returns
        -------
            dict
                The payload for the Jira ticket
        """
        jira_payload = {
            "fields": {
                "project": {
                    "key": project_key
                },
                "issuetype": {
                    "id": issue_type
                },
                "summary": "AWS SSO - grant permissions for {} - {} - {}".format(service_name, permission_level, account_name),
                "description": {
                    "version": 1,
                    "type": "doc",
                    "content": [
                        {
                            "type": "paragraph",
                            "content": [
                                {
                                    "type": "text",
                                    "text": "Hey "
                                },
                                {
                                    "type": "mention",
                                    "attrs": {
                                        "id": assignee_id,
                                        "accessLevel": ""
                                    }
                                },
                                {
                                    "type": "text",
                                    "text": ", "
                                },
                                {
                                    "type": "mention",
                                    "attrs": {
                                        "id": assignee_mention,
                                        "accessLevel": ""
                                    }
                                },
                                {
                                    "type": "text",
                                    "text": " requested new permissions for:"
                                },
                                {
                                    "type": "hardBreak"
                                },
                                {
                                    "type": "text",
                                    "text": "service: {}".format(service_name)
                                },
                                {
                                    "type": "hardBreak"
                                },
                                {
                                    "type": "text",
                                    "text": "resource: {}".format(resource_name)
                                },
                                {
                                    "type": "hardBreak"
                                },
                                {
                                    "type": "text",
                                    "text": "permission level: {}".format(permission_level)
                                },
                                {
                                    "type": "hardBreak"
                                },
                                {
                                    "type": "text",
                                    "text": "Please review and approve - "
                                },
                                {
                                    "type": "text",
                                    "text": "Pull Request",
                                    "marks": [
                                        {
                                            "type": "link",
                                            "attrs": {
                                                "href": github_pull_request_url,
                                                "title": "Github Pull Request"
                                            }
                                        }
                                    ]
                                }
                            ]
                        }
                    ]
                },
                "assignee": {
                    "id": assignee_id
                }
            },
            "update": {}
        }
        return jira_payload

    def get_user_id_by_email_address(self, email_address: str) -> str:
        """
        Gets the user id by email address.

        Parameters
        ----------
            email_address : str
                The email address of the user

        Returns
        -------
            str
                The id of the user if successful, empty string otherwise
        """
        endpoint = "/user/search"
        params = {
            "query": email_address
        }
        request_headers = {
            'Content-Type': 'application/json',
            'Authorization': "Basic {}".format(base64.b64encode("{}:{}".format(self.user, self.token).encode('utf-8')).decode('utf-8'))
        }
        try:
            request = urllib.request.Request(
                url="{}{}?{}".format(self.base_url, endpoint, urllib.parse.urlencode(params)),
                headers=request_headers,
                method='GET'
            )
            with urllib.request.urlopen(request) as response:
                if response.getcode() == 200:
                    user_id = json.loads(response.read())[0].get("accountId")
                    return user_id
                else:
                    logging.error("JiraConnector.get_user_id_by_email_address: {}".format(response.read()))
                    return ""
        except Exception as ex:
            logging.error("JiraConnector.get_user_id_by_email_address: {}".format(ex))
            return ""
