def user_context( request ):
    session = request.session

    context = {}
    if 'user_context' in session:
        context = session['user_context']

    return {
        'user_context': context
    }
