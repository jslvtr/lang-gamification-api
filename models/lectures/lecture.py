from sqlalchemy import and_

from app import db
import models.lectures.constants as LectureConstants
from models.searchable import SearchableModel


class Lecture(db.Model, SearchableModel):
    __tablename__ = LectureConstants.TABLE_NAME

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80))
    description = db.Column(db.String(140))
    order = db.Column(db.Integer)

    module_id = db.Column(db.Integer, db.ForeignKey('module.id'))
    module = db.relationship('Module',
                             backref=db.backref('lectures', lazy='dynamic'))

    def __init__(self, name, module, description, order=None):
        self.name = name
        self.order = order or len(module.lectures.all()) + 1
        self.description = description
        self.module = module

    def __repr__(self):
        return "<Lecture ID:{}, ORDER:{}, MODULE_ID:{}>".format(self.id, self.order, self.module_id)

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def remove_from_db(self):
        db.session.delete(self)
        db.session.commit()

    @staticmethod
    def change_order(lecture_id, module_id, new_position):
        # Get every lecture in 'new_order' and over and shift them down by one.
        # Move 'lecture_id' into 'new_order' as you get to it.
        changed_lecture = Lecture.query.get(lecture_id)
        if changed_lecture.order == new_position:
            return
        elif changed_lecture.order < new_position:
            # The lecture has moved from low position to high (later) position
            lectures = Lecture.query.filter(and_(Lecture.module_id == module_id, Lecture.order <= new_position, Lecture.order >= changed_lecture.order)).order_by(Lecture.order.asc()).all()
            for lecture in lectures:
                if lecture.id == lecture_id:
                    lecture.order = new_position
                else:
                    lecture.order -= 1
                db.session.add(lecture)
        else:
            # The lecture has been moved from a high position to a low (earlier) position
            lectures = Lecture.query.filter(and_(Lecture.module_id == module_id, Lecture.order >= new_position, Lecture.order <= changed_lecture.order)).order_by(Lecture.order.asc()).all()
            for lecture in lectures:
                if lecture.id == lecture_id:
                    lecture.order = new_position
                else:
                    lecture.order += 1
                db.session.add(lecture)
        db.session.commit()

    def reorder(self, new_position):
        Lecture.change_order(self.id, self.module_id, new_position)
