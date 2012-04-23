from django.shortcuts import redirect
from functools import wraps

def group_check(required_group):
    def decorator(func):
        def inner_decorator(request, *args, **kwargs):  
            logined = request.session.get('logined', default = None)
            if not logined:
                return redirect('/login')
            groups = request.session.get('groups', default = None)
            if required_group in groups:
                return func(request, *args, **kwargs)
            else:
                return redirect('/login')
        return wraps(func)(inner_decorator)
    return decorator