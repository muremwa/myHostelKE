def school_and_cookie(request):
    """Each template needs the 'cookies accepted' and 'school' added to context"""
    return {
        'school': request.session.setdefault('school', None),
        'cookie': request.session.setdefault('cookie', False)
    }
