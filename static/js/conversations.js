$(document).ready(function () {
    if (newConversation) {
        $("#tagName").html(createOptionsFromArray(tag_names));
    } else {
        $(".fill-in").on('click', function(e) {
            var target = $(e.target);
            target.removeClass('fill-in');
            target.css('display', 'none');
            target.next('.utterance-content').css('display', 'block');
        })
    }
});

function addUtterance() {
    var addUtteranceElement = $("#addUtterance");
    addUtteranceElement.html(createUtteranceHTML());
    $("#create-button").on('click', function () {
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

function saveConversation(submit_url) {
    var utterance_contents = $(".utterance");
    utterance_contents = $.map(utterance_contents, function (a) {
        return {
            name: $(a).children("p").html(),
            hide: $(a).children(":checked").length == 1
        };
    });
    $.ajax({
        url: submit_url,
        type: 'POST',
        data: JSON.stringify({
            "tag": $('#tagName').val(),
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
    return '<a href="#" class="list-group-item utterance">' +
        '<h4 class="list-group-item-heading">Speaker ' + ((number_questions % 2) + 1) + '</h4>' +
        '<p class="list-group-item-text">' + utterance + '</p>' +
        '<label for="hideInConversation">Hide in conversation: </label><input type="checkbox" id="hideInConversation">' +
        '</a>'
}

function nextUtterance() {
    var firstHiddenUtterance = $(".invisible")[0];
    if (firstHiddenUtterance !== undefined) {
        $(firstHiddenUtterance).removeClass('invisible');
        $(firstHiddenUtterance).addClass('visible')
    } else {
        $("#nextUtterance").prop('disabled', true);
        $("#endMessage").css('display', 'inline');
    }
}