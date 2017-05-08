def user_context( request ):
    return {
        'user_context': request.session.get('user_context', {})
    }
