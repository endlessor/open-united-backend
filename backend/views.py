from django.conf import settings
from django.contrib.auth import logout, login as auth_login
from django.contrib.auth.models import User
from django.shortcuts import redirect
from django.views import View

from api.auth.authmachine_client import AuthMachineClient
from backend.services import update_user, sign_up, update_user_permissions
from talent.models import Person


class OIDCallbackView(View):

    def get(self, request):
        client = AuthMachineClient(request)
        a_resp = client.get_authorization_response()
        token = client.get_access_token(a_resp)
        request.session["token"] = token.to_json()
        user_info = client.get_userinfo(a_resp)
        user_email = user_info["email"]
        is_exists_person_by_email = Person.objects.filter(email_address=user_email).exists()
        is_exists_user_by_email = User.objects.filter(email=user_email).first()
        user = update_user(user_info, is_exists_user_by_email) \
            if is_exists_person_by_email and is_exists_user_by_email \
            else sign_up(user_info, 0)

        update_user_permissions(request, user, user_info["id"])

        auth_login(request, user)
        return redirect(settings.FRONT_END_SERVER)


class OIDCallbackLogoutView(View):

    def get(self, request):
        logout(request)
        return redirect(settings.FRONT_END_SERVER)
