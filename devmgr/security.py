import logging

from pyramid.security import Everyone, Authenticated


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
