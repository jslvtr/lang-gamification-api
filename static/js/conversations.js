$(document).ready(function() {
    if (newConversation) {
        $("#tagName").html(createOptionsFromArray(tag_names));
        getWordsForSelectedTag("#tagName", "#answerSelect", answer_url);
        $("#tagName").on('change', function () {
            getWordsForSelectedTag("#tagName", "#answerSelect", answer_url);
        });
    }
});

function addUtterance() {
    var addUtteranceElement = $("#addUtterance");
    addUtteranceElement.html(createUtteranceHTML());
    $("#create-button").on('click', function() {
        addQuestionToPanelAsCreated($(".utterance").length, $("#utteranceField").val());
    });
    addUtteranceElement.html();
}

function createUtteranceHTML() {
    return '<div class="question-form">' +
        '<div class="form-group"><label for="utteranceField">Utterance: </label> <input type="text" id="utteranceField" class="form-control"></div>' +
            '<btn class="btn btn-info" id="create-button">Add</btn>' +
        '</div>'
}

function createOptionsFromArray(arr) {
    if (arr.length > 0) {
        var optionString = "";
        for (var index = 0; index < arr.length; index++) {
            optionString += option(arr[index]);
        }
        return optionString;
    }
    return option('None available')
}

function option(val) {
    return '<option value="' + val + '">' + val + '</option>';
}

function getWordsForSelectedTag(tag_id, answer_id, url) {
    var selectedTag = $(tag_id).val();
    $.ajax({
        url: url.replace(encodeURIComponent("{}"), selectedTag),
        type: 'GET',
        success: function (result) {
            var answers = result['answers'];
            $(answer_id).html(createOptionsFromArray(answers));
            if (answers.length == 0) {
                $(answer_id).prop('disabled', true);
            } else {
                $(answer_id).removeAttr('disabled');
            }
        }
    })
}

function saveConversation(submit_url) {
    var utterance_contents = $(".utterance");
    utterance_contents = $.map(utterance_contents, function(a) {
        return a.textContent;
    });
    $.ajax({
        url: submit_url,
        type: 'POST',
        data: JSON.stringify({
            "tag": $('#tagName').val(),
            "answer": $('#answerSelect').val(),
            "utterances": utterance_contents
        }),
        dataType: "json",
        success: function () {
            console.log("Success!");
            $("#addQuestion").html('');
        },
        error: function () {
            console.log("Error!");
        }
    })
}

function addQuestionToPanelAsCreated(number_questions, utterance) {
    var questionsElement = $("#questions");
    var currentQuestions = questionsElement.html();
    if (currentQuestions == '') {
        questionsElement.html('<ul class="list-group">' + questionListItem(number_questions, utterance) + '</ul>');
    } else {
        questionsElement.html(currentQuestions + questionListItem(number_questions, utterance));
    }
}

function questionListItem(number_questions, utterance) {
    return '<a href="#" class="list-group-item">' +
        '<h4 class="list-group-item-heading">Speaker ' + ((number_questions % 2) + 1) + '</h4>' +
        '<p class="list-group-item-text utterance">' + utterance + '</p>' +
        '</a>'
}
