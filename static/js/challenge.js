function calculatePossibleChallengeOutcomes() {
    var currentWager = parseInt($(".email-search").val(), 10);
    $("#winAmount").html(currentWager * 2);
    $("#loseAmount").html(currentWager);
}