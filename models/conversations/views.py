import logging

from flask import Blueprint, redirect, url_for, request, g, render_template, jsonify

from app import db
from models.conversations.utterance import Utterance
from models.lectures.lecture import Lecture
from models.conversations.conversation import Conversation
from models.users.decorators import requires_access_level
import models.users.constants as UserConstants
from models.words.word import Word

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

__author__ = 'jslvtr'

bp = Blueprint('conversations', __name__, url_prefix='/conversations')


@bp.route('/lecture/<int:lecture_id>/new', methods=['GET', 'POST'], defaults={'conversation_id': None})
@bp.route('/lecture/<int:lecture_id>/new/<int:conversation_id>', methods=['GET', 'POST'])
@requires_access_level(UserConstants.USER_TYPES['CREATOR'])
def new(lecture_id, conversation_id):
    lecture = Lecture.query.get(lecture_id)
    module = lecture.module
    conversation = None
    if conversation_id:
        conversation = Conversation.query.get(conversation_id)
    if not g.user.is_course_creator(module):
        return redirect(url_for('modules.dashboard'))
    if request.method == 'POST':
        request_json = request.get_json(force=True, silent=True)
        if request_json is None:
            return jsonify({"message": "The request was invalid."}), 400
        conversation = Conversation(request_json['tag'], lecture,)
        conversation.save_to_db()
        utterances = [Utterance(request_json['utterances'][i]['name'],
                                i,
                                conversation,
                                request_json['utterances'][i]['hide']) for i in range(len(request_json['utterances']))]
        for utterance in utterances:
            db.session.add(utterance)
        db.session.commit()
        return jsonify({"message": "Conversation added successfully."}), 201
    return render_template('conversations/new.html',
                           lecture=lecture,
                           conversation=conversation,
                           tag_names=[tag.name for tag in lecture.tags])


@bp.route('/lecture/<int:lecture_id>', methods=['GET'])
@requires_access_level(UserConstants.USER_TYPES['USER'])
def conversation_list(lecture_id):
    lecture = Lecture.query.get(lecture_id)
    is_owner = g.user.is_course_creator(lecture.module)
    conversations = Conversation.query.filter(Conversation.lecture_id == lecture_id)
    return render_template('conversations/list.html',
                           lecture=lecture,
                           conversations=conversations,
                           is_owner=is_owner)


@bp.route('/study/<int:conversation_id>', methods=['GET'])
@requires_access_level(UserConstants.USER_TYPES['USER'])
def do_conversation(conversation_id):
    conversation = Conversation.query.get(conversation_id)
    return render_template('conversations/view.html', conversation=conversation)
