from django.shortcuts import render, redirect
from django.conf import settings
from utils import restful


def is_login(func):
    def wrapper(request, *args, **kwargs):
        if 'is_login' in request.session:
            res = func(request, *args, **kwargs)
            return res
        else:
            print(request.session.session_key)
            print(request.session)
            return restful.params_error(message='用户未登录，请登录！')
    return wrapper


class LoginRequireMixin(object):
    @classmethod
    def as_view(cls, **initkwargs):
        view = super().as_view(**initkwargs)
        return is_login(view)

