from datetime import datetime
from flask_login import UserMixin
from weight_tracker import db, login_manager


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

friendship = db.Table('friendship',
    db.Column('added_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('adder_id', db.Integer, db.ForeignKey('user.id'))
    )

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    username = db.Column(db.String(50), index=True, nullable=False, unique=True)
    name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(100), index=True, nullable=False, unique=True)
    profile_picture = db.Column(db.String(50), nullable=False, default='default.jpg')
    hashed = db.Column(db.String(60), nullable=False)
    weights = db.relationship('Weight', backref='user', lazy='dynamic')
    friends = db.relationship('User',
                            secondary=friendship,
                            primaryjoin=(friendship.c.added_id == id),
                            secondaryjoin=(friendship.c.adder_id == id),
                            backref=db.backref('friendship', lazy='dynamic'),
                            lazy='dynamic')

    def __repr__(self):
        return f"User('{self.username}', '{self.name}', '{self.email}', '{self.profile_picture}')"

    def add_friend(self, user):
        if not self.is_added(user):
            self.friends.append(user)
    
    def unfriend(self, user):
        if self.is_added(user):
            # remove the 'right' side
            self.friends.remove(user)
            # remove the 'left' side
            user.friends.remove(self)

    def is_added(self, user):
        return self.friends.filter(friendship.c.adder_id == user.id).count() > 0

    def is_friend(self, user):
        if self.is_added(user):
            # check from the 'right' side
            return user.friends.filter(friendship.c.adder_id == self.id).count() > 0
        # meaning has added friend but not confirmed yet
        return False


class Weight(db.Model):
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False) 
    weight = db.Column(db.Integer, nullable=False)
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return f"Weight('{self.user_id}', '{self.weight}', '{self.date}')"