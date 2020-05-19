import re
from random import randrange

from flask import Blueprint, jsonify, request, g
from werkzeug.security import generate_password_hash, check_password_hash

from .commons.APIResponse import APIResponse
from .commons.decorators import access_token_required, refresh_token_required
from .commons.jwt_common import create_jwt_access_token, create_jwt_refresh_token
from .models import User, Order, db, Token

api_views = Blueprint('api_views', __name__, url_prefix='/api/v1')


@api_views.route('/', methods=['GET'])
def api_v1_index():
    return "api v1 index"


@api_views.route('/user', methods=['POST'])
def user_register():
    """
    회원가입 api

    :return:
    """
    req_data = request.form

    if len(set(req_data.keys()).intersection(set(['name', 'nickname', 'password', 'phone', 'email']))) != 5:
        return APIResponse('필수파라미터 누락').json()

    if req_data.get('name'):
        # 한글,영문 대소문자 만허용, 20
        if not re.match('^[가-힣a-zA-Z]{0,20}$', req_data.get('name')):
            return APIResponse('이름 조건 미충족.').json()

    if req_data.get('nickname'):
        # 영문 소문자만 허용, 30
        if not re.match('^[a-z]{0,30}$', req_data.get('nickname')):
            return APIResponse('닉네임 조건 미충족.').json()

    if req_data.get('password'):
        # 최소 10자 이상, 영문 대소문자, 특수문자, 숫자 각 1개 이상씩 포함
        if re.match(r"^(?=.*[A-Za-z])(?=.*\d)(?=.*[~!@#$%^&?*])[A-Za-z\d~!@#$%^&?*]{10,}$", req_data.get('password')):
            hashed_passwd = generate_password_hash(req_data.get('password'))
        else:
            return APIResponse('비밀번호 조건 미충족.').json()

    if req_data.get('phone'):
        # 숫자, 20
        if not re.match('^[\d]{0,20}$', req_data.get('phone')):
            return APIResponse('전화번호 조건 미충족.').json()

    if req_data.get('email'):
        # 이메일형식, 100자
        if not re.match("[\w\-\._]+@[\w\-\._]+\.\w{2,10}", req_data.get('email')):
            return APIResponse('이메일 조건 미충족.').json()
    try:
        new_user = User(name=req_data.get('name'), nickname=req_data.get('nickname'), password=hashed_passwd,
                    phone=req_data.get('phone'), email=req_data.get('email'), gender=req_data.get('gender', ''))
        db.session.add(new_user)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        if e.orig.args[0] == 1062:
            return APIResponse('중복된 이메일 입니다.').json()
        else:
            return APIResponse('DB에러 입니다.', 500, str(e)).json()

    new_user = new_user.as_dict()
    del new_user['password']
    return APIResponse('success', 200, new_user).json()


@api_views.route('/login', methods=['POST'])
def login_api():
    """
    로그인
    :return:
    """
    print('{}'.format(request.form))
    req_data = request.form

    if len(set(req_data.keys()).intersection(set(['password', 'email']))) != 2:
        return APIResponse('필수파라미터 누락.', 422).json()

    login_user = User.query.filter_by(email=req_data.get('email')).first()
    if not login_user:
        return APIResponse('id/pw 오류', 401, ).json()

    if not check_password_hash(login_user.password, req_data.get('password')):
        return APIResponse('id/pw 오류', 401,).json()

    a_token = create_jwt_access_token(login_user.id)
    r_token = create_jwt_refresh_token(login_user.id)

    if a_token and r_token:
        print("access_token : {}".format(a_token))
        print("refresh_token : {}".format(r_token))
        return APIResponse('success', 200, data={'access_token': a_token, 'refresh_token': r_token}).json()
    else:
        return APIResponse('fail', 500).json()


@api_views.route('/access-token', methods=['GET'])
@refresh_token_required
def access_token_api():
    """
    refresh으로 access token 재발행
    :return:
    """
    access_token = create_jwt_access_token(g.userid)

    return APIResponse('success', 200, data={'access_token': access_token}).json()


@api_views.route('/logout', methods=['POST'])
@access_token_required
def logout_api():
    """
    로그아웃

    :return:
    """
    from flask import g
    print('g.userid : {}'.format(g.userid))

    result = Token.query.filter_by(userid=g.userid).delete()
    print("result : {}".format(result))
    if result:
        db.session.commit()
        return APIResponse('logout success.', 200, {'userid': g.userid}).json()
    else:
        return APIResponse('logout fail', 200, {'userid': g.userid}).json()


@api_views.route('/user/<string:userid>', methods=['GET'])
@access_token_required
def user_api(userid=None):
    if userid:
        print('userid : {}'.format(userid))
        user = User.query.filter_by(id=userid).first()
        if user:
            user = user.as_dict()
            del user['password']
            return APIResponse('success', 200, user).json()
        else:
            return APIResponse('search fail', 200).json()
    else:
        return APIResponse('필수 파라미터 누락', 422).json()


@api_views.route('/orders/<string:userid>')
@access_token_required
def order_api(userid=None):
    if userid:
        print("userid : {}".format(userid))
        orders = Order.query.filter_by(userid=userid).all()
        res = []
        for order in orders:
            res.append(order.as_dict())

        return APIResponse('success', 200, res).json()
    else:
        return APIResponse('필수 파라미터 누락', 422).json()


@api_views.route('/users', methods=['GET'])
@access_token_required
def get_users():
    req_data = request.form
    print(req_data)
    per_page = 5
    page = 1
    if req_data.get('per_page', None):
        per_page = int(req_data.get('per_page'))

    if req_data.get('page', None):
        page = int(req_data.get('page'))


    ###
    last_orders = db.session.query(Order.userid, db.func.max(Order.transdate).label('last_order_date'), Order.productname, Order.orderid)\
        .group_by(Order.userid).subquery()

    query = User.query.outerjoin(last_orders, User.id == last_orders.c.userid) \
        .add_columns(User.id, User.name, User.nickname, User.email, last_orders.c.orderid,last_orders.c.last_order_date, last_orders.c.productname)

    if req_data.get('name', None):
        query = query.filter(User.name==req_data.get('name'))

    if req_data.get('email', None):
        query = query.filter(User.email==req_data.get('email'))

    users = query.paginate(page, per_page, False).items
    ###

    res = {}
    for idx, user in enumerate(users):
        res.update({idx: user.__str__()})

    return APIResponse('success', 200, res).json()


@api_views.route('/order', methods=['POST'])
@access_token_required
def create_order():
    req_data = request.form
    print("req_data : {}".format(req_data))

    # orderid는 12자리, 중복이 불가능한 임의의 영문 대문자, 숫자 조합
    text = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
    orderid = ''
    for i in range(12):
        orderid += text[randrange(36)] # 언젠가는 중복이 발생할 수 있다..

    try:
        order = Order(orderid=orderid, productname=req_data.get('productname', 'p_name'), userid=req_data.get('userid'))
        db.session.add(order)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return APIResponse('주문 번호 생성에 실패하였습니다.', 500, e).json()



    return APIResponse('success', 200, order.as_dict()).json()
