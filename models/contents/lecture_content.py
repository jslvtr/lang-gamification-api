from app import db
import models.contents.constants as ContentConstants


class LectureContent(db.Model):
    __tablename__ = ContentConstants.TABLE_NAME

    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(80))
    path = db.Column(db.String(140))
    text = db.Column(db.String)

    lecture_id = db.Column(db.Integer, db.ForeignKey('lecture.id'))
    lecture = db.relationship('Lecture',
                              backref=db.backref('content', uselist=False))

    def __init__(self, lecture, type, path="", text=u""):
        self.lecture = lecture
        self.type = type
        self.path = path
        self.text = text

    def __repr__(self):
        return "<Content ID:{}, TYPE:{} LECTURE_ID:{}>".format(self.id, self.type, self.lecture_id)

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def remove_from_db(self):
        db.session.delete(self)
        db.session.commit()

    def update_text_content(self, new_content):
        self.text = new_content
        self.save_to_db()
