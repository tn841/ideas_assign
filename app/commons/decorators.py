from functools import wraps

from flask import request

from .APIResponse import APIResponse
from .jwt_common import parse_jwt_token
from ..models import Token


def access_token_required(func):
    """
    access-token에 대한 검증

    :param func:
    :return:
    """

    @wraps(func)
    def deco_func(*args, **kwargs):
        access_token = None

        for header, value in request.headers.items():
            if header.upper() == "X-ACCESS-TOKEN":
                access_token = value

        if access_token:
            jwt_payload = parse_jwt_token(access_token)
            print('jwt_payload : {}'.format(jwt_payload))
            if jwt_payload:
                if jwt_payload.get('error', None):
                    return APIResponse('401', 'token_expired').json()
                else:
                    from flask import g
                    g.userid = jwt_payload.get('userid')
                    return func(*args, **kwargs)
            else:
                return APIResponse('401', 'token_error').json()
        else:
            return APIResponse('401', 'token_required').json()

    return deco_func


def refresh_token_required(func):
    """
    refresh_token에 대한 검증

    :param func:
    :return:
    """

    @wraps(func)
    def deco_func(*args, **kwargs):
        refresh_token = None

        for header, value in request.headers.items():
            if header.upper() == "X-REFRESH-TOKEN":
                refresh_token = value

        if refresh_token:
            jwt_payload = parse_jwt_token(refresh_token)
            print("jwt_payload : {}".format(jwt_payload))
            if jwt_payload:
                if jwt_payload.get('error', None):
                    return APIResponse('401', 'token_expired').json()
                else:
                    # DB에 있는 refreshkey 값과 비교
                    token_obj = Token.query.filter_by(refreshkey=jwt_payload.get('refresh')).first()
                    print("token_obj : {}".format(token_obj))

                    if token_obj:
                        from flask import g
                        g.userid = jwt_payload.get('userid')

                        return func(*args, **kwargs)
                    else:
                        return APIResponse('401', 'token_invalid').json()
            else:
                return APIResponse('401', 'token_error').json()
        else:
            return APIResponse('401', 'token_required').json()

    return deco_func