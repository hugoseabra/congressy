from core.helper.account.middleware import UserContext


def user_context(request):
    uc = UserContext(request.session)
    return {
        'user_context': uc.__dict__
    }
