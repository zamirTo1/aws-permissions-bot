import base64
import urllib.parse
import urllib.request
import json
import datetime
import logging
logger = logging.getLogger()
logger.setLevel("INFO")


class GithubConnector:
    """
    A class used to represent a GitHub Connector

    ...

    Attributes
    ----------
    token : str
        a formatted string to represent the token
    base_url : str
        a formatted string to represent the base url of GitHub API
    main_branch_name : str
        a formatted string to represent the main branch name
    owner : str
        a formatted string to represent the owner
    terraform_environment_repository_name : str
        a formatted string to represent terraform environment repository name
    terraform_module_repository_name : str
        a formatted string to represent terraform module repository name
    terraform_environment_sso_account_path : str
        a formatted string to represent terraform environment sso account path

    Methods
    -------
    read_file_content(repository_name: str, file_path: str, ref=None) -> tuple[str, str]:
        Reads the content of a file in a repository
    create_full_request(
        group_name: str,
        account_name: str,
        new_content: str,
        service_name: str,
        user_name: str,
        permission: str,
        resource_name: str
    ) -> str:
        Creates a full request
    """

    def __init__(
            self,
            token: str,
            owner: str,
            terraform_environment_repository_name: str,
            terraform_module_repository_name: str,
            terraform_environment_sso_account_path: str
    ):
        """
        Constructs all the necessary attributes for the GithubConnector object.

        Parameters
        ----------
            token : str
                user's token
            owner : str
                owner's username
            terraform_environment_repository_name : str
                terraform environment repository name
            terraform_module_repository_name : str
                terraform module repository name
            terraform_environment_sso_account_path : str
                terraform environment sso account path
        """
        self.token = token
        self.base_url = "https://api.github.com"
        self.main_branch_name = "main"
        self.owner = owner
        self.terraform_environment_repository_name = terraform_environment_repository_name
        self.terraform_module_repository_name = terraform_module_repository_name
        self.terraform_environment_sso_account_path = terraform_environment_sso_account_path

    def read_file_content(self, repository_name: str, file_path: str, ref=None) -> tuple[str, str]:
        """
        Reads the content of a file in a repository.

        Parameters
        ----------
            repository_name : str
                The name of the repository
            file_path : str
                The path of the file
            ref : str, optional
                The reference to the file (default is None)

        Returns
        -------
            tuple[str, str]
                The content of the file and its sha if successful, empty strings otherwise
        """
        if ref:
            endpoint = "/repos/{}/{}/contents/{}?ref={}".format(self.owner, repository_name, file_path, ref)
        else:
            endpoint = "/repos/{}/{}/contents/{}".format(self.owner, repository_name, file_path)
        request_headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/vnd.github.audit-log-preview+json',
            'Authorization': 'Bearer {}'.format(self.token)
        }
        try:
            request = urllib.request.Request("{}{}".format(self.base_url, endpoint), headers=request_headers)
            with urllib.request.urlopen(request) as response:
                if response.status == 200:
                    data = json.loads(response.read())
                    return data.get("content"), data.get("sha")
                else:
                    logger.error("GithubConnector.read_file_content: {}".format(response.read()))
                    return "", ""
        except Exception as ex:
            logger.error("GithubConnector.read_file_content: {}".format(ex))
            return "", ""

    def __read_latest_commit_sha(self):
        endpoint = "/repos/{}/{}/git/refs/heads/{}".format(
            self.owner,
            self.terraform_environment_repository_name,
            self.main_branch_name
        )
        request_headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/vnd.github.audit-log-preview+json',
            'Authorization': 'Bearer {}'.format(self.token)
        }
        try:
            request = urllib.request.Request("{}{}".format(self.base_url, endpoint), headers=request_headers)
            with urllib.request.urlopen(request) as response:
                if response.getcode() == 200:
                    return json.loads(response.read())['object']['sha']
                else:
                    logger.error("GithubConnector.__read_latest_commit_sha: {}".format(response.read()))
                    return ""
        except Exception as ex:
            logger.error("GithubConnector.__read_latest_commit_sha: {}".format(ex))
            return ""

    def __create_new_branch(self, new_branch_name: str):
        endpoint = "/repos/{}/{}/git/refs".format(self.owner, self.terraform_environment_repository_name)
        payload = {
            "ref": "refs/heads/{}".format(new_branch_name),
            "sha": self.__read_latest_commit_sha()
        }
        request_headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/vnd.github.audit-log-preview+json',
            'Authorization': 'Bearer {}'.format(self.token)
        }
        try:
            request = urllib.request.Request(
                url="{}{}".format(self.base_url, endpoint),
                headers=request_headers,
                data=bytes(json.dumps(payload), encoding='utf-8')
            )
            with urllib.request.urlopen(request) as response:
                if response.getcode() == 201:
                    return True
                else:
                    logger.error("GithubConnector.__create_new_branch: {}".format(response.read()))
                    return False
        except Exception as ex:
            logger.error("GithubConnector.__create_new_branch: {}".format(ex))
            return False

    def __update_file(self, group_name: str, account_name: str, new_content: str, new_branch_name: str, file_sha: str):
        endpoint = "/repos/{}/{}/contents/{}/{}/{}.tf".format(
            self.owner,
            self.terraform_environment_repository_name,
            self.terraform_environment_sso_account_path,
            group_name,
            account_name
        )
        payload = {
            "message": "AWS Permissions bot - updating {}/{}.tf".format(group_name, account_name),
            "content": base64.b64encode(new_content.encode('utf-8')).decode('utf-8'),
            "sha": file_sha,
            "branch": new_branch_name
        }
        request_headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/vnd.github.audit-log-preview+json',
            'Authorization': 'Bearer {}'.format(self.token)
        }
        try:
            request = urllib.request.Request(
                url="{}{}".format(self.base_url, endpoint),
                headers=request_headers,
                data=bytes(json.dumps(payload), encoding='utf-8'),
                method='PUT'
            )
            with urllib.request.urlopen(request) as response:
                if response.getcode() == 200:
                    return True
                else:
                    logger.error("GithubConnector.__update_file: {}".format(response.read()))
                    return False
        except Exception as ex:
            logger.error("GithubConnector.__update_file: {}".format(ex))
            return False

    def create_full_request(
        self,
        group_name: str,
        account_name: str,
        new_content: str,
        service_name: str,
        user_name: str,
        permission: str,
        resource_name: str
    ) -> str:
        """
        Creates a full request.

        Parameters
        ----------
            group_name : str
                The name of the group
            account_name : str
                The name of the account
            new_content : str
                The new content
            service_name : str
                The name of the service
            user_name : str
                The name of the user
            permission : str
                The permission
            resource_name : str
                The name of the resource

        Returns
        -------
            str
                The url of the created pull request if successful, empty string otherwise
        """
        new_branch_name = "aws_permissions_bot_{}_{}_{}_in_{}_for_{}_{}".format(
            service_name,
            permission,
            resource_name,
            account_name,
            user_name,
            int(datetime.datetime.now().timestamp()*1000)
        )
        if self.__create_new_branch(new_branch_name):
            file_path_sha = self.read_file_content(
                repository_name=self.terraform_environment_repository_name,
                file_path="{}/{}/{}.tf".format(self.terraform_environment_sso_account_path, group_name, account_name)
            )[1]
            if self.__update_file(group_name, account_name, new_content, new_branch_name, file_path_sha):
                endpoint = '/repos/{}/{}/pulls'.format(self.owner, self.terraform_environment_repository_name)
                request_headers = {
                    'Content-Type': 'application/json',
                    'Accept': 'application/vnd.github.audit-log-preview+json',
                    'Authorization': 'Bearer {}'.format(self.token)
                }
                payload = {
                    "title": new_branch_name,
                    "head": new_branch_name,
                    "base": self.main_branch_name,
                    "body": "AWS Permissions bot - updating {}/{}.tf - adding {} permission for {}".format(
                        group_name,
                        account_name,
                        permission,
                        user_name
                    )
                }
                try:
                    request = urllib.request.Request(
                        url="{}{}".format(self.base_url, endpoint),
                        headers=request_headers,
                        data=bytes(json.dumps(payload), encoding='utf-8'),
                        method='POST'
                    )
                    with urllib.request.urlopen(request) as response:
                        if response.getcode() == 201:
                            return json.loads(response.read()).get("html_url")
                        else:
                            logger.error("GithubConnector.create_full_request: {}".format(response.read()))
                            return ""
                except Exception as ex:
                    logger.error("GithubConnector.create_full_request: {}".format(ex))
                    return ""
