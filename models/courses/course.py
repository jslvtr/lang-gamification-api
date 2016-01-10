import datetime
import models.courses.constants as CourseConstants
import models.courses.errors as CourseErrors
from models.courses.errors import NotOwnerException
from app import db

__author__ = 'jslvtr'


class Course(db.Model):

    __tablename__ = CourseConstants.COLLECTION
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80))
    created_date = db.Column(db.DateTime)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    owner = db.relationship('User',
                            backref=db.backref('courses', lazy='dynamic'))

    def __init__(self, name, user_owner, created_date=None):
        self.name = name
        self.owner = user_owner
        self.created_date = created_date or datetime.datetime.utcnow()

    def __repr__(self):
        return "<Course {}>".format(self.name)

    @classmethod
    def find(cls, **kwargs):
        query = cls.query.filter_by(**kwargs)
        if not query.first():
            raise CourseErrors.CourseNotFoundException("The course to be found with kwargs {} cannot be found.".format(
                kwargs
            ))
        return query

    @staticmethod
    def allowed(course_id, user):
        return course_id in [course.id for course in user.courses.all()]

    @staticmethod
    def delete(course_id, user):
        course = Course.query.filter_by(id=course_id).first()

        if Course.allowed(course_id, user):
            course.remove_from_db()
        else:
            raise NotOwnerException("You are not the owner of this Course, so you cannot delete it.")

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def remove_from_db(self):
        db.session.delete(self)
        db.session.commit()
