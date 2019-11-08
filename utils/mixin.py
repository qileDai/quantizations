
from utils import restful
from django.contrib.sessions.models import Session


# 用户登录装饰器
def is_login(func):
    def wrapper(request, *args, **kwargs):
        try:
            # request.session.clear_expired()
            sessionid = request.META.get("HTTP_SESSIONID")
            session_data = Session.objects.get(session_key=sessionid)
            time = session_data.expire_date
            is_login = session_data.get_decoded().get('is_login')
            if is_login is True:
                res = func(request, *args, **kwargs)
                return res
            else:
                return restful.unauth(message="session失效，请重新登录！")
        except:
            import traceback
            traceback.print_exc()
            return restful.unauth(message="session失效，请重新登录！！")
    return wrapper


class LoginRequireMixin(object):
    @classmethod
    def as_view(cls, **initkwargs):
        view = super().as_view(**initkwargs)
        return is_login(view)

