from flask import Blueprint, jsonify, request

from .models import User

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

    return jsonify({}), 200


@api_views.route('/login', methods=['POST'])
def login_api():
    """
    로그인
    :return:
    """
    print('{}'.format(request.form))
    return jsonify(request.form), 200


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
        pass

    else:
        return jsonify({'msg': 'fail'})


@api_views.route('/users', methods=['GET'])
def get_users():
    users = User.query.order_by(User.id).all()
    print('users : {}'.format(users))
    return jsonify({'msg': 'success', 'len' : len(users)})
