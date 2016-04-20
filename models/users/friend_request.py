import models.users.errors as UserErrors
import models.users.constants as UserConstants
from app import db

__author__ = 'jslvtr'


class FriendRequest(db.Model):
    __tablename__ = UserConstants.FRIEND_REQUESTS_TABLE_NAME
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('{}.id'.format(UserConstants.TABLE_NAME)))
    new_friend_id = db.Column(db.Integer, db.ForeignKey('{}.id'.format(UserConstants.TABLE_NAME)))

    user = db.relationship('User', foreign_keys=[student_id])
    new_friend = db.relationship('User', foreign_keys=[new_friend_id])

    def __init__(self, user, new_friend):
        if user.id == new_friend.id:
            raise UserErrors.FriendAddingError("You tried to add yourself as a friend!")
        self.user = user
        self.new_friend = new_friend

    def __repr__(self):
        return "<FriendRequest {}>".format(self.id)

    @classmethod
    def pending_requests_for_user(cls, user):
        return cls.query.filter(cls.new_friend_id == user.id).all()

    def notify_new_friend(self):
        print("Sending e-mail to friend...")
        pass

    def remove_from_db(self):
        db.session.delete(self)
        db.session.commit()

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

