
from flask import jsonify


class APIResponse:
    """
    api 응답 객체 정의
    """
    code = None
    msg = ''
    data = None

    def __init__(self, msg='', code=200, data=None):
        self.code = code
        self.data = data
        self.msg = msg

    def to_dict(self):
        res = {}
        res["msg"] = self.msg
        res["code"] = self.code
        if self.data:
            res["data"] = self.data
        print("res : {}".format(res))
        return res

    def json(self):
        return jsonify(self.to_dict()), self.code



