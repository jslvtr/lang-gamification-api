import datetime
import uuid

import requests
from flask import url_for, request

from app import db, app
import models.users.constants as UserConstants


class EmailConfirmation(db.Model):
    __tablename__ = UserConstants.CONFIRMATION_TABLE_NAME

    id = db.Column(db.Integer, primary_key=True)
    confirmed = db.Column(db.Boolean, default=False)
    uuid = db.Column(db.String)

    created_date = db.Column(db.DateTime)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship('User')

    def __init__(self, user):
        self.user = user
        self.created_date = datetime.datetime.utcnow()
        self.uuid = uuid.uuid4().hex

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def remove_from_db(self):
        db.session.delete(self)
        db.session.commit()

    def send(self):
        email_request = requests.post(
            "https://api.mailgun.net/v3/{}/messages".format(app.config.get('MAILGUN_DOMAIN')),
            auth=("api", app.config.get('MAILGUN_API_KEY')),
            data={"from": "Jose at Build To Learn <mailgun@{}>".format(app.config.get('MAILGUN_DOMAIN')),
                  "to": [self.user.email],
                  "subject": "Please confirm your e-mail address",
                  "text": "Thank you for registering for <>.\n\n"
                          "To finalise your registration, please confirm your e-mail address by "
                          "clicking the link below or pasting it into your browser:\n\n"
                          "{base_url}{confirmation_url}\n\n"
                          "Thank you once again for taking part in this study.\n\n"
                          "Kind regards,\n"
                          "Jose".format(base_url=request.url_root[:-1],
                                        confirmation_url=url_for('users.confirm', confirmation_id=self.uuid))})
        return email_request

    def confirm(self):
        self.confirmed = True
        self.save_to_db()
