def access_token(request):
    return {'access_token': request.session.get('access_token')}
