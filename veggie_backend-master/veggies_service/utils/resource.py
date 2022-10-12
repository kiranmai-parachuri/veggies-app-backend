import traceback
from datetime import datetime
from functools import wraps

from flask import request, session, current_app as app, Response
from flask_restful import Resource

from veggies_service.conf.error_object import ErrorObject
from veggies_service.utils.exceptions import UnauthorisedException, ValidationException, NotFoundException, \
    GenericCustomException, AlreadyExist, BadRequest


def sanitize_response(response):
    data = None
    status = 200
    headers = {}

    if isinstance(response, tuple) and len(response) is 3:
        (data, status, headers) = response
    else:
        data = response
    return (data, status, headers)


def authenticate(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not getattr(func, 'authenticated', True):
            return func(*args, **kwargs)

        if session.get('username', False):
            return func(*args, **kwargs)

        app.logger.error("Unauthorized request from %s", request.remote_addr)
        return ErrorObject(errorCode=401, errorMessage='Unauthorized')

    return wrapper


def format_response(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        data, status, headers = sanitize_response(func(*args, **kwargs))
        message = "Operation Successful"
        is_successful = True
        if isinstance(data, ErrorObject):
            print(data.__dict__)
            status = data.errorCode
            message = data.errorMessage
            data = {}
            is_successful = False

        if status == 302:
            return data, status, headers
        if isinstance(data, Response):
            return data
        data = {
            "responseData": data,
            "message": message,
            "status": is_successful
        }

        return (data, status, headers)

    return wrapper


def cors(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        data, status, headers = sanitize_response(func(*args, **kwargs))

        cors_allow_headers = ', '.join(app.config.get('CORS_ALLOW_HEADERS', []))
        cors_allow_origins = ', '.join(app.config.get('CORS_ALLOW_ORIGINS', []))
        cors_allow_methods = ', '.join(app.config.get('CORS_ALLOW_METHODS', []))

        headers.update({
            'Access-Control-Allow-Headers': cors_allow_headers,
            'Access-Control-Allow-Origin': cors_allow_origins,
            'Access-Control-Allow-Methods': cors_allow_methods
        })

        return (data, status, headers)

    return wrapper


def handle_validation_exception(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            start = datetime.now()
            response = func(*args, **kwargs)
            # here is something to remember me by
            end = datetime.now()
            print("API request took {}".format(end - start))
        except UnauthorisedException as kon_hai_be_tu:
            print(traceback.print_exc())
            end = datetime.now()
            print("API request took {}".format(end - start))
            return kon_hai_be_tu.errorObject
        except ValidationException as faltugiri_mat_kar:
            print(traceback.print_exc())
            end = datetime.now()
            print("API request took {}".format(end - start))
            return faltugiri_mat_kar.errorObject
        except NotFoundException as ghanta_milega:
            print(traceback.print_exc())
            end = datetime.now()
            print("API request took {}".format(end - start))
            return ghanta_milega.errorObject
        except BadRequest as bad:
            print(traceback.print_exc())
            end = datetime.now()
            print("API request took {}".format(end - start))
            return bad.errorObject
        except GenericCustomException as e:
            print(traceback.print_exc())
            end = datetime.now()
            print("API request took {}".format(end - start))
            return e.errorObject
        except AlreadyExist as land:
            return land.errorObject
        except Exception as ex:
            print("uncaught exception")
            print(ex.message)
            print(traceback.print_exc())
            end = datetime.now()
            print("API request took {}".format(end - start))
            return ErrorObject(errorMessage="Something went wrong",
                               errorCode=400)
        return response

    return wrapper


def gzip(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        data, status, headers = sanitize_response(func(*args, **kwargs))


class BaseResource(Resource):
    method_decorators = [handle_validation_exception,
                         format_response]
