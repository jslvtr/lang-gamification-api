import datetime
import models.modules.constants as CourseConstants
import models.modules.errors as CourseErrors
from models.modules.errors import NotOwnerException
from app import db

__author__ = 'jslvtr'


class Module(db.Model):

    __tablename__ = CourseConstants.COLLECTION
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80))
    created_date = db.Column(db.DateTime)
    public = db.Column(db.Boolean)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    owner = db.relationship('User',
                            backref=db.backref('modules', lazy='dynamic'))

    def __init__(self, name, user_owner, public=False, created_date=None):
        self.name = name
        self.owner = user_owner
        self.public = public
        self.created_date = created_date or datetime.datetime.utcnow()

    def __repr__(self):
        return "<Module {}>".format(self.name)

    @classmethod
    def find(cls, **kwargs):
        query = cls.query.filter_by(**kwargs)
        elems = query.all()
        if len(elems) < 1:
            raise CourseErrors.CourseNotFoundException("The module to be found with kwargs {} cannot be found.".format(
                kwargs
            ))
        return elems

    @classmethod
    def find_public(cls, **kwargs):
        kwargs.update({'public': True})
        return cls.find(**kwargs)

    @staticmethod
    def delete(course_id, user):
        course = Module.query.filter_by(id=course_id).first()

        if user.allowed_course(course):
            course.remove_from_db()
        else:
            raise NotOwnerException("You are not the owner of this Module, so you cannot delete it.")

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def remove_from_db(self):
        db.session.delete(self)
        db.session.commit()
