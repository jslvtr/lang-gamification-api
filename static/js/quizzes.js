var generator;

$(document).ready(function () {
    generator = quizQuestionGenerator();
    nextQuestionHTML();
    $("#skipButton").on('click', function () {
        console.log("Skipped");
    });
    $("#quitButton").on('click', function () {
        console.log("Quit");
    });
    $("input[type=radio]").on('click', function (evt) {
        $(".active-label").removeClass('active-label');
        $(evt.target).parent().prop('class', 'active-label');
    });
});

function nextQuestionHTML() {
    var question = generator.next();
    if (!question.done) {
        $(".question").html(createQuestion(question.value));
    }
}

function createQuestion(question) {
    return '<p class="question-title" id="' + question.id + '">' + question.title + '</p>' +
        '<div class="question-body">' +
        createAnswers(question.answers) +
        '<span class="target" id="' + question.meaning + '"></span>' +
        '</div>';
}

function createAnswers(answers) {
    var i = 0;
    var ret = "";
    while (i < answers.length) {
        ret += createAnswerRadio(i, answers[i]);
        i++;
    }
    return ret;
}

function createAnswerRadio(i, answer) {
    return '<div class="radio">' +
        '<label>' +
        '<input type="radio" name="optionsRadios" id="' + i + '" value="' + answer + '">' +
        answer +
        '</label>' +
        '</div>';
}

function checkSelectedAnswer(check_url) {
    var selected = $(":checked");
    $.ajax({
        url: check_url,
        type: 'POST',
        data: JSON.stringify({
            "question_id": $('.question-title').prop('id'),
            "meaning": $('.target').prop('id'),
            "answer": selected.val()
        }),
        dataType: "json",
        success: function (result) {
            if (result.value == true) {
                showMessage(true);
            } else {
                showMessage(false);
            }
            nextQuestionHTML();
            $("input[type=radio]").on('click', function (evt) {
                $(".active-label").removeClass('active-label');
                $(evt.target).parent().prop('class', 'active-label');
            });
            window.setTimeout(function () {
                    var checkedButton = $(".check");
                    if (checkedButton) {
                        checkedButton.html("Check");
                        checkedButton.removeClass("check");
                        $("#continueButton").removeClass('animate-border');
                    }
                },
                1250
            );


        },
        error: function () {
            console.log("Error!");
        }
    })
}

function showMessage(correct) {
    var continueButton = $("#continueButton");
    continueButton.addClass('check');
    var ht = "";
    if (correct) {
        ht = "<span id='continueBackgroundAnimator' style='background-color: #3498DB'></span>";
        ht += "<span id='high-z' class='glyphicon glyphicon-ok'></span>";
    } else {
        ht = "<span id='continueBackgroundAnimator' style='background-color: #dd6b6b'></span>";
        ht += "<span id='high-z' class='glyphicon glyphicon-remove'></span>";
    }
    continueButton.html(ht);
    continueButton.addClass('animate-border')
}