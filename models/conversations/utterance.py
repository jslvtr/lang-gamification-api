from app import db
import models.conversations.constants as ConversationConstants


class Utterance(db.Model):
    __tablename__ = ConversationConstants.UTTERANCE_TABLE_NAME

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    order = db.Column(db.Integer)

    conversation_id = db.Column(db.Integer, db.ForeignKey('conversation.id'))
    conversation = db.relationship("Conversation")

    def __init__(self, name, order, conversation):
        self.order = order
        self.name = name
        self.conversation = conversation

    def save_to_db(self):
        db.session.add(self)
        db.session.commit()

    def remove_from_db(self):
        db.session.delete(self)
        db.session.commit()