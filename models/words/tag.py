from app import db
import models.words.constants as WordConstants


class Tag(db.Model):
    __tablename__ = WordConstants.TAG_TABLE_NAME

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True)

    def __init__(self, name):
        self.name = name

    @classmethod
    def get_by_name(cls, name):
        return cls.query.filter_by(name=name).first() or cls(name)

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def remove_from_db(self):
        db.session.delete(self)
        db.session.commit()

    @classmethod
    def save_tags_to_db(cls, tags):
        for tag in tags:
            tag.save_to_db()

    @staticmethod
    def get_tags_from_csv(tags_csv):
        """
        Method to get a list of Tag objects from a CSV input.
        This makes sure to not create duplicate tags in the database.
        :param tags_csv: the input in the form of "tag1, tag2, tag3". Whitespace is ignored.
        :return: [Tag...]
        """
        return [Tag.get_by_name(tag.strip()) for tag in tags_csv.split(",")]
