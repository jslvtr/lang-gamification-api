import datetime
import models.modules.constants as CourseConstants
import models.modules.errors as CourseErrors
from models.modules.errors import NotOwnerException
import common.helper_tables as HelperTables
from app import db
from models.searchable import SearchableModel

__author__ = 'jslvtr'


class Module(db.Model, SearchableModel):
    __tablename__ = CourseConstants.TABLE_NAME
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80))
    created_date = db.Column(db.DateTime)
    public = db.Column(db.Boolean)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    owner = db.relationship('User',
                            backref=db.backref('modules', lazy='dynamic'))
    students = db.relationship('User', secondary=HelperTables.students,
                               backref=db.backref('studying', lazy='dynamic'))

    def __init__(self, name, user_owner, students=None, public=False, created_date=None):
        self.name = name
        self.owner = user_owner
        self.public = public
        self.students = students or [user_owner]
        self.created_date = created_date or datetime.datetime.utcnow()

    def __repr__(self):
        return "<Module {}>".format(self.name)

    @classmethod
    def find(cls, **kwargs):
        query = cls.query.filter_by(**kwargs)
        return query.all()

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

    def add_student(self, user):
        self.students.append(user)
        db.session.add(self)
        db.session.commit()

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def remove_from_db(self):
        db.session.delete(self)
        db.session.commit()

