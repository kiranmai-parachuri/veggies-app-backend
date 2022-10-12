import json

from flask import request, make_response

from veggies_service.service_apis_handler import otp_handler
from veggies_service.utils.exceptions import InternalServerError
from veggies_service.utils.resource import BaseResource
from veggies_service.views.user import UserBasicView


class OTP(BaseResource):
    def get(self):
        pass

    def post(self):
        request_data = request.get_json(force=True)
        status = otp_handler.verify_and_send_otp(request_data)
        if status:
            return {}
        else:
            raise InternalServerError()

    post.authenticated = False

    def put(self):
        data = request.args
        token = request.headers.get('token')
        if not token:
            token = request.cookies.get('token')
        if 'action' in data and data['action'] == 'logout':
            return otp_handler.handle_logout(token)
        if 'action' in data and data['action'] == 'resent':
            return otp_handler.handle_resend_otp(token)
        request_data = request.get_json(force=True)
        login_object = otp_handler.get_user_for_otp(request_data)
        view = UserBasicView()
        res = {
            'responseData':
                {'login':
                    {
                        "user": view.render(login_object.user),
                        "token": login_object.token,
                    }
                },
            "message": "Operation Successful",
            "status": True

        }

        response = make_response(json.dumps(res, indent=4), 200)
        response.mimetype = 'application/json'
        response.set_cookie("token", login_object.token)
        response.set_cookie("mobile", login_object.user.mobile)
        response.set_cookie("role", login_object.user.role)

        # return Response("TEST",content_type='text/html;charset=utf-8',status=500)
        return response
