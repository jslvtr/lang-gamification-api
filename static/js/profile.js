function showFriendControls(target) {
    var controls = $(".list-group-item.white.show");
    for (var i = 0; i < controls.length; i++){
        if (!$(controls[i]).hasClass('retracted')) {
            $(controls[i]).addClass('retract');
        }
    }
    var next_control = $(target).next();
    var isShowing = next_control.hasClass('show');
    controls.removeClass('show');

    next_control = $(target).next();
    if (isShowing) {
        next_control.addClass('retract');
        next_control.removeClass('show');
    } else {
        next_control.removeClass('retracted');
        next_control.removeClass('retract');
        next_control.addClass('show');
    }
}