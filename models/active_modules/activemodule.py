from sqlalchemy import and_

from app import db
import models.active_modules.constants as ActiveModuleConstants
import models.active_modules.errors as ActiveModuleErrors
import common.helper_tables as HelperTables
from models.lectures.lecture import Lecture


class ActiveModule(db.Model):
    __tablename__ = ActiveModuleConstants.TABLE_NAME

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80))
    experience = db.Column(db.Integer, unique=False)
    level = db.Column(db.Integer, unique=False)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    owner = db.relationship('User',
                            backref=db.backref('active_modules', lazy='dynamic'))
    module_id = db.Column(db.Integer, db.ForeignKey('module.id'))
    module = db.relationship('Module', secondary=HelperTables.active_to_modules, uselist=False)
    completed_lectures = db.relationship('Lecture', secondary=HelperTables.completed_lectures, lazy='dynamic')

    def __init__(self, name, user_owner, module, experience=0, level=1):
        self.name = name
        self.owner = user_owner
        self.module = module
        self.module_id = module.id
        self.experience = experience
        self.level = level

    def next_level_experience(self):
        return (self.level+1) * 50 + max(0, ((self.level+1) - 199) * 450)

    def starting_experience_for_current_level(self):
        return self.level * 50 + max(0, (self.level - 199) * 450)

    def experience_required_to_level_up(self):
        return self.next_level_experience() - self.experience

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def remove_from_db(self):
        db.session.delete(self)
        db.session.commit()

    def complete_lecture(self, lecture_id):
        lecture = Lecture.query.get(lecture_id)
        if lecture in self.completed_lectures:
            raise ActiveModuleErrors.LectureAlreadyCompletedException("You have already completed this lecture!")
        self.completed_lectures.append(Lecture.query.get(lecture_id))
        self.save_to_db()

    def next_uncompleted_lecture(self):
        lecture = Lecture.query.filter(and_(Lecture.module_id == self.module.id, ~Lecture.completed_cities.contains(ActiveModule.query.get(self.id)))).first()
        return lecture

    @classmethod
    def get_by_user_id(cls, module_id, user_id):
        return cls.query.filter(cls.user_id == user_id, cls.module_id == module_id).first()

    def get_all_questions_in_completed_lectures(self):
        questions = []
        for lecture in self.completed_lectures:
            questions.extend(lecture.get_all_questions_in_quizzes())
        return questions

    def increase_experience(self, amount, reason):
        if amount >= self.experience_required_to_level_up():
            self.experience = amount - self.experience_required_to_level_up()
            self.level += 1
            self.owner.add_notification("Level up! " + reason, "experience", None)
        else:
            self.experience += amount
            self.owner.add_notification(reason, "experience", None)
