# pos/decorators.py
from django.shortcuts import redirect
from functools import wraps

def rol_requerido(*roles):
    def decorator(view_func):
        @wraps(view_func)
        def wrapped(request, *args, **kwargs):
            if request.user.is_authenticated and request.user.rol in roles:
                return view_func(request, *args, **kwargs)
            return redirect('dashboard')
        return wrapped
    return decorator