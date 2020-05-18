import json

from flask import Blueprint, jsonify, request
from werkzeug.security import generate_password_hash, check_password_hash

from .models import User, Order, db

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
        return jsonify({'msg': '필수파라미터 누락.'}), 200

    if req_data.get('name'):
        # 한글,영문 대소문자 만허용, 20
        pass

    if req_data.get('nickname'):
        # 영문 소문자만 허용, 30
        pass

    if req_data.get('password'):
        # 최소 10자 이상, 영문 대소문자, 특수문자, 숫자 각 1개 이상씩 포함

        hashed_passwd = generate_password_hash(req_data.get('password'))
        pass

    if req_data.get('phone'):
        # 숫자, 20
        pass

    if req_data.get('email'):
        # 이메일형식, 100자
        pass

    new_user = User(name=req_data.get('name'), nickname=req_data.get('nickname'), password=hashed_passwd,
                phone=req_data.get('phone'), email=req_data.get('email'), gender=req_data.get('gender', ''))
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'data': '{}'.format(new_user)}), 200


@api_views.route('/login', methods=['POST'])
def login_api():
    """
    로그인
    :return:
    """
    print('{}'.format(request.form))
    req_data = request.form

    if len(set(req_data.keys()).intersection(set(['password', 'email']))) != 2:
        return jsonify({'msg': '필수파라미터 누락.'}), 200

    login_user = User.query.filter_by(email=req_data.get('email')).first()
    print(login_user.password)
    if not check_password_hash(login_user.password, req_data.get('password')):
        return jsonify({'msg': '비밀번호 오류'})


    # todo : access-token, refrest-token 발급
    return jsonify({'data': '{}'.format(login_user)}), 200


@api_views.route('/logout', methods=['POST'])
def logout_api():
    """
    로그아웃

    :return:
    """
    print('{}'.format(request.form))
    return jsonify(request.form), 200


@api_views.route('/user/<string:userid>', methods=['GET'])
def user_api(userid=None):
    if userid:
        print('userid : {}'.format(userid))
        user = User.query.filter_by(id=userid).first()
        if user:
            return jsonify({'msg': 'success.', 'data': '{}'.format(user)})
        else:
            return jsonify({'msg': 'search fail.'})
    else:
        return jsonify({'msg': 'fail'})


@api_views.route('/orders/<string:userid>')
def order_api(userid=None):
    if userid:
        print("userid : {}".format(userid))
        orders = Order.query.filter_by(userid=userid).all()
        for order in orders:
            print(order)
        return jsonify({'orders': '{}'.format(len(orders))})
    else:
        return jsonify({'msg': 'fail'})


@api_views.route('/users', methods=['GET'])
def get_users():
    req_data = request.form
    per_page = 5
    page = 1
    if req_data.get('per_page', None):
        per_page = int(req_data.get('per_page'))

    if req_data.get('page', None):
        page = int(req_data.get('page'))

    query = User.query
    if req_data.get('name', None):
        name = req_data.get('name')
        query.filter(User.name == name)

    if req_data.get('email', None):
        email = req_data.get('email')
        query.filter(User.email == email)

    users = User.query.order_by(User.id).all()

    print('users : {}'.format(users))
    res = {}
    for idx, user in enumerate(users):
        res.update({idx: str(user)})

    # ObjectRes.query.order_by('-id').first()

    return jsonify({'msg': 'success', 'users': res})


@api_views.route('/order', methods=['POST'])
def create_order():

    order = Order(productname='productname', userid=1)  # orderid는 12자리, 유니크해야함 => autoincrement = 100000000000 부터 시작
    db.session.add(order)
    db.session.commit()

    return jsonify({'msg': 'success', 'data': '{}'.format(order)}), 200
