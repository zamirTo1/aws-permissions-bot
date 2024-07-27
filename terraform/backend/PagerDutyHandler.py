import urllib.parse
import urllib.request
import json
import logging
logger = logging.getLogger()
logger.setLevel("INFO")


class PagerDutyConnector:
    """
    A class used to represent a PagerDuty Connector

    ...

    Attributes
    ----------
    base_url : str
        a formatted string specifying the base url of the PagerDuty API
    headers : dict
        a dictionary representing the headers to be sent in the API request

    Methods
    -------
    get_on_call_email_address(schedule_ids: str) -> str:
        Returns the email address of the on-call user for the given schedule_ids

    __get_users_email(user_id) -> str:
        Returns the email address of the user with the given user_id
    """

    def __init__(self, token):
        """
        Constructs all the necessary attributes for the PagerDutyConnector object.

        Parameters
        ----------
            token : str
                the PagerDuty API token
        """
        self.base_url = "https://api.pagerduty.com"
        self.headers = {
            'Authorization': 'Token token={}'.format(token)
        }

    def get_on_call_email_address(self, schedule_ids: str) -> str:
        """
        Returns the email address of the on-call user for the given schedule_ids

        Parameters
        ----------
            schedule_ids : str
                the schedule_ids for which to get the on-call user's email address

        Returns
        -------
            str
                the email address of the on-call user, or an empty string if an error occurs
        """
        endpoint = "/oncalls"
        params = {
            "schedule_ids[]": schedule_ids,
            "limit": 1
        }
        try:
            request = urllib.request.Request(
                url="{}{}?{}".format(self.base_url, endpoint, urllib.parse.urlencode(params)),
                headers=self.headers
            )
            with urllib.request.urlopen(request) as response:
                if response.getcode() == 200:
                    response_data = json.loads(response.read())
                    on_call_user_id = response_data.get("oncalls")[0].get("user").get("id")
                    return self.__get_users_email(user_id=on_call_user_id)
                else:
                    logger.error("PagerDutyHandler.get_on_call_email_address: {}".format(response.read()))
                    return ""
        except Exception as ex:
            logger.error("PagerDutyHandler.get_on_call_email_address: {}".format(ex))
            return ""

    def __get_users_email(self, user_id) -> str:
        """
        Returns the email address of the user with the given user_id

        Parameters
        ----------
            user_id : str
                the user_id for which to get the email address

        Returns
        -------
            str
                the email address of the user, or an empty string if an error occurs
        """
        endpoint = "/users/{}".format(user_id)
        try:
            request = urllib.request.Request(
                url="{}{}".format(self.base_url, endpoint),
                headers=self.headers
            )
            with urllib.request.urlopen(request) as response:
                if response.getcode() == 200:
                    return json.loads(response.read()).get("user").get("email")
                else:
                    logger.error("PagerDutyHandler.get_users_email: {}".format(response.read()))
                    return ""
        except Exception as ex:
            logger.error("PagerDutyHandler.get_users_email: {}".format(ex))
            return ""
