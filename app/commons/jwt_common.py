from datetime import datetime, timedelta

import jwt
from ..models import db, Token


def create_jwt_access_token(userid):
    """
    JWT access token 생성

    :param userid:
    :return:
    """

    expired_minute = 3
    secret = 'ideas_assign_sccret_key_!@#!@#'

    payload = {
        'aud': 'assign',
        'exp': datetime.utcnow() + timedelta(minutes=expired_minute),
        'userid': userid
    }

    token = jwt.encode(payload, secret, algorithm='HS256')
    return token.decode('utf-8')

def create_jwt_refresh_token(userid):
    """
    JWT refresh token 생성

    :param userid:
    :return:
    """

    expired_hours = 24
    secret = 'ideas_assign_sccret_key_!@#!@#'

    import uuid
    refreshkey = str(uuid.uuid4())

    # DB에 refreshKey저장
    try:
        db.session.add(Token(userid=userid, refreshkey=refreshkey))
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(e.orig.args)
        if e.orig.args[0] == 1062:
            issued_token = Token.query.filter_by(userid=userid).first()
            print("issued_token : {}".format(issued_token.refreshkey))
            refreshkey = issued_token.refreshkey
        else:
            return ''

    payload = {
        'aud': 'assign',
        'exp': datetime.utcnow() + timedelta(hours=expired_hours),
        'userid': userid,
        'refresh': refreshkey
    }

    token = jwt.encode(payload, secret, algorithm='HS256')
    return token.decode('utf-8')


def parse_jwt_token(token):
    """
    JWT token 파싱

    :param token:
    :return:
    """

    secret = 'ideas_assign_sccret_key_!@#!@#'

    try:
        decoded = jwt.decode(token, secret, algorithms=['HS256'], audience='assign')
        print(decoded)
        return decoded
    except jwt.ExpiredSignatureError as e:
        return {'error': e}
    except Exception as e:
        return None