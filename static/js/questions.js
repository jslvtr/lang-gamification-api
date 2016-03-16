function addQuestion(tags, url, submit_url) {
    $("#addQuestion").html(createQuestionHTML(tags));
    getWordsForSelectedTag("#tagName", "#answerSelect", url);
    $("#tagName").on('change', function () {
        getWordsForSelectedTag("#tagName", "#answerSelect", url);
    });
    $("#create-button").on('click', function () {
        sendQuestionPOST(submit_url);
    })
}

function createQuestionHTML(tags) {
    return '<div class="question-form">' +
        '<div class="form-group"><label for="tagName">Tag:</label> <select id="tagName" class="form-control">' + createOptionsFromArray(tags) + '</select></div> ' +
        '<div class="form-group"><label for="answerSelect">Answer: </label> <select id="answerSelect" class="form-control"></select></div>' +
        '<btn class="btn btn-info" id="create-button">Create</btn>' +
        '</div>'
}

function createOptionsFromArray(tags) {
    if (tags.length > 0) {
        var optionString = "";
        for (var index = 0; index < tags.length; index++) {
            optionString += option(tags[index]);
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
                $("#create-button").prop('disabled', true);
            } else {
                $(answer_id).removeAttr('disabled');
                $("#create-button").removeAttr('disabled');
            }
        }
    })
}

function sendQuestionPOST(submit_url) {
    $.ajax({
        url: submit_url,
        type: 'POST',
        data: JSON.stringify({
            "tag": $('#tagName').val(),
            "answer": $('#answerSelect').val()
        }),
        dataType: "json",
        success: function (result) {
            console.log("Success!");
            addQuestionToPanelAsCreated(result['question_url']);
            $("#addQuestion").html('');
        },
        error: function () {
            console.log("Error!");
        }
    })
}

function addQuestionToPanelAsCreated(question_url) {
    var questionsElement = $("#questions");
    var currentQuestions = questionsElement.html();
    var newQuestions = currentQuestions;
    if (currentQuestions == '') {
        newQuestions = '<ul class="list-group">' + questionListItem(question_url) + '</ul>';
    } else {
        newQuestions = currentQuestions + questionListItem(question_url);
    }
    questionsElement.html(newQuestions);
}

function questionListItem(question_url) {
    return '<a href="' + question_url + '" class="list-group-item">' +
        '<h4 class="list-group-item-heading">Question asking for meaning of ' + $("#answerSelect").val() + '</h4>' +
        '<p class="list-group-item-text">Belongs to tag ' + $("#tagName").val() + '</p>' +
        '</a>'
}
