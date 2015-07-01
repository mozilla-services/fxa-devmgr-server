import logging
import time

from pyramid.security import Everyone, Authenticated


class Creds(object):
    """Basic Credentials object"""
    def __init__(self, account_id, recent=False):
        self.account_id = account_id
        self.recent = recent


class DevMgrAuthenticationPolicy(object):
    def authenticated_userid(self, request):
        return None

    def effective_principals(self, request):
        effective_principals = [Everyone]
        if request.credentials:
            effective_principals.append(Authenticated)
            effective_principals.append(
                "account_id:%s" % request.credentials.account_id)
            if request.credentials.recent:
                effective_principals.append(
                    "recent_account_id:%s" % request.credentials.account_id
                )
        logging.info("Effective principals: %s", effective_principals)
        return effective_principals


def verify_auth(event):
    req = event.request
    req.credentials = None
    token_str = req.headers.get("Authorization")
    if not token_str:
        return

    d = token_str.strip().split()
    if len(d) != 2:
        logging.debug("Length of authorization is not 2")
        return
    typ, token = d
    if typ != "Bearer":
        logging.debug("Not a bearer token")
        return

    result = req.registry.fxa_oauth.verify_token(token)
    created = result["created_at"] / 1000
    recent = int(time.time())-created < 600
    cred = Creds(account_id=result["user"], recent=recent)
    req.credentials = cred
