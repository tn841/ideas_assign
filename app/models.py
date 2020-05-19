from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class User(db.Model):
    __table_args__ = (
        db.UniqueConstraint('email', name='unique_email_commit'),
    )
    id = db.Column(db.Integer, primary_key=True, unique=True)
    name = db.Column(db.String(20), nullable=False)
    nickname = db.Column(db.String(30), nullable=False)
    password = db.Column(db.String(128), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)
    gender = db.Column(db.String(1), nullable=True)

    def __repr__(self):
        return '<User %r>' % self.name

    def __str__(self):
        return 'id: {}, name: {}, nickname: {}, password: {}, phone: {}, email: {}, gender: {}'.\
            format(self.id, self.name, self.nickname, self.password, self.phone, self.email, self.gender)

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class Order(db.Model):
    orderid = db.Column(db.String(12), primary_key=True, unique=True)
    productname = db.Column(db.String(100), nullable=False)
    transdate = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    userid = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref=db.backref('orders', lazy=True))

    def __repr__(self):
        return '<Order %r>' % self.orderid

    def __str__(self):
        return 'orderid: {}, productname: {}, transdate: {}, userid: {}'\
            .format(self.orderid, self.productname, self.transdate, self.userid)

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}


class Token(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    userid = db.Column(db.Integer)
    refreshkey = db.Column(db.String(100), nullable=False)
    createdate = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return '<Token %r>' % self.id
