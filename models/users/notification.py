import datetime

from app import db
import models.users.constants as UserConstants
from models.searchable import SearchableModel


class Notification(db.Model, SearchableModel):
    __tablename__ = UserConstants.NOTIFICATION_TABLE_NAME

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80))
    type = db.Column(db.String(40))
    data = db.Column(db.String(10))
    read = db.Column(db.Boolean, default=False)

    created_date = db.Column(db.DateTime)

    student_id = db.Column(db.Integer, db.ForeignKey('student.id'))
    user = db.relationship('User',
                           backref=db.backref('notifications', lazy='dynamic'))

    def __init__(self, name, type, data, user):
        self.name = name
        self.type = type
        self.data = data
        self.user = user
        self.created_date = datetime.datetime.utcnow()

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def remove_from_db(self):
        db.session.delete(self)
        db.session.commit()

    @property
    def age(self):
        datetime_age_seconds = int((datetime.datetime.utcnow() - self.created_date).total_seconds())
        days = int(datetime_age_seconds / 86400)
        datetime_age_seconds -= days * 86400

        hours = int(datetime_age_seconds / 3600)
        datetime_age_seconds -= hours * 3600

        minutes = int(datetime_age_seconds / 60)
        datetime_age_seconds -= minutes * 60
        return {
            "days": days,
            "hours": hours,
            "minutes": minutes,
            "seconds": datetime_age_seconds
        }

