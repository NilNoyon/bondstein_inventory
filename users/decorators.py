from django.shortcuts import redirect
from .models import User, UserPermission
from django.contrib import messages

def login(function):
    def wrap(request, *args, **kwargs):
        if request.session.get('id'):
            return function(request, *args, **kwargs)
        else:
            messages.warning(request, "Please login first!")
            return redirect("/") #Login page url
    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__
    return wrap

def permission(request, menu_url):
    try:
        chk_privilege    = UserPermission.objects.get(user_id = int(request.session.get('id')), menu__menu_url = menu_url, menu__status = True, status = True)
        if chk_privilege: return chk_privilege
        else: 
            messages.warning(request, "You have no permission on this action!")
            return redirect("/")
    except UserPermission.DoesNotExist:
        return None