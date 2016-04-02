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
        onRadioClick(evt);
    });
});

function onRadioClick(evt) {
    $(".active-label").removeClass('active-label');
    var radio = $(".active-radio");
    radio.addClass('inactive-radio-anim');
    radio.addClass('inactive-radio');
    radio.removeClass('active-radio');
    $(evt.target).parent().prop('class', 'active-label');
    radio = $(evt.target).parent().parent().parent();
    radio.removeClass('inactive-radio');
    radio.addClass('active-radio');
}

function nextQuestionHTML() {
    var question = generator.next();
    if (!question.done) {
        $(".question").html(createQuestion(question.value));
    } else {
        finishQuiz();
    }
    setQuestionTimeouts();
}

function createQuestion(question) {
    return '<div class="progress">' +
        '<div class="progress-bar" id="countdown" role="progressbar" aria-valuenow="100" aria-valuemin="0" aria-valuemax="100">' +
        '</div>' +
        '</div>' +
        '<p class="question-title" id="' + question.id + '">' + question.title + '</p>' +
        '<p class="question-help" style="display: none">Please select one of the options</p>' +
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
    return '<div class="inactive-radio"><div class="radio">' +
        '<label>' +
        '<input type="radio" name="optionsRadios" id="' + i + '" value="' + answer + '">' +
        answer +
        '</label>' +
        '</div></div>';
}

function checkSelectedAnswer(check_url) {
    var selected = $(":checked");
    if (selected.html() == undefined) {
        vibrateCheckButton();
    } else {
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
                    $(".quiz").addClass("correct-question-border");
                    window.setTimeout(function () {
                        $(".quiz").removeClass("correct-question-border");
                    }, 1000);
                } else {
                    showMessage(false);
                    $(".quiz").addClass("wrong-question-border");
                    window.setTimeout(function () {
                        $(".quiz").removeClass("wrong-question-border");
                    }, 1000);
                }
                nextQuestionHTML();
                $("input[type=radio]").on('click', function (evt) {
                    onRadioClick(evt);
                });
            },
            error: function () {
                console.log("Error!");
            }
        })
    }
}

function setQuestionTimeouts() {
    window.setTimeout(function () {
            var checkedButton = $(".check");
            if (checkedButton) {
                checkedButton.html("Check");
                checkedButton.removeClass("check");
                var continueButton = $("#continueButton");
                continueButton.removeClass('animate-border');
                continueButton.removeClass('vibrate');
                continueButton.removeClass('incorrect-check');
            }
        },
        1250
    );

    window.setTimeout(function () {
        if ($("#countdown").width() == 0) {
            skipQuestion(false);
        }
    }, 5100);
}

function showMessage(correct) {
    var continueButton = $("#continueButton");
    continueButton.addClass('check');
    var ht = "";
    if (correct) {
        ht = "<span id='high-z' class='glyphicon glyphicon-ok'></span>";
    } else {
        continueButton.addClass('incorrect-check');
        ht = "<span id='high-z' class='glyphicon glyphicon-remove'></span>";
    }
    continueButton.html(ht);
    continueButton.addClass('animate-border')
}

function vibrateCheckButton() {
    var continueButton = $("#continueButton");
    continueButton.addClass('vibrate');
    $(".question-help").css({
        display: "block"
    })
}

function skipQuestion(buttonClicked) {
    $.ajax({
        url: skip_url,
        type: 'POST',
        data: JSON.stringify({
            "question_id": $('.question-title').prop('id')
        }),
        dataType: "json",
        success: function (result) {
            nextQuestionHTML();
            $("input[type=radio]").on('click', function (evt) {
                onRadioClick(evt);
            });
        },
        error: function () {
            console.log("Error!");
        }
    })
}

function finishQuiz() {
    window.setTimeout(function () {
            var continueButton = $("#continueButton");
            continueButton.html("Finish");
        },
        1250
    );
    $.ajax({
        url: finish_url,
        type: 'GET',
        success: function (result) {
            $(".question").html(scoreDivHTML(result));
            $("#continueButton").css({display: "none"});
            $("#skipButton").css({display: "none"});
            var finishButton = $("#finishButton");
            changeUserGold(result);
            finishButton.css({left: "calc(50% - " + ((finishButton.width() / 2) + 10) + "px)", display: "block"})
        },
        error: function () {
            console.log("Error!");
        }
    });
}

function scoreDivHTML(scores) {
    if (scores['challenge'] === undefined) {
        return '<div class="score"><h2>Well done!</h2>' +
            '<p>You scored <span class="score-total">' + scores.score + '</span> out of ' + scores.num_questions + '!</p>' +
            '<p>You have earned <i class="fa fa-circle fa-lg" style="color: #FFD409"></i> <span class="gold">' + scores.gold_earned + '</span> gold</p></div>';
    } else {
            return '<div class="score"><span class="icon fa fa-2x fa-' + scores.icon + '"></span><h2>' + scores.message + '</h2>' +
                '<p>' + scores.submessage + '</p></div>';
    }
}

function changeUserGold(scores) {
    var userGoldSpan = $("#userGold");
    var currentUserGold = parseInt(userGoldSpan.html(), 10);
    if (scores.win == true) {
        userGoldSpan.html(currentUserGold + scores.gold_earned);
    } else if (scores.draw == true) {
        userGoldSpan.html(currentUserGold + scores.wager);
    }
}