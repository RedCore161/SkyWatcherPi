
const MAX_UI_MODE = true;


//See: http://bootstrap-notify.remabledesigns.com/
function showSuccess(txt, _delay=2500) {

    console.log(txt)

    if (MAX_UI_MODE) {

        $.notify({
            title: "Success!",
            message: txt,
            icon: 'glyphicon glyphicon-warning-sign'
        }, {
            type: "success",
            delay: _delay,
            newest_on_top: true,
            animate: {
                enter: 'animated fadeInRight',
                exit: 'animated fadeOutRight'
            }
        });
    }

}

function showError(txt, _delay=2500) {

    console.error(txt)

    if (MAX_UI_MODE) {

        $.notify({
            title: "Error!",
            message: txt,
            icon: 'glyphicon glyphicon-warning-sign'
        }, {
            type: "danger",
            delay: _delay,
            newest_on_top: true,
            animate: {
                enter: 'animated fadeInRight',
                exit: 'animated fadeOutRight'
            }
        });
    }
}

function disableAllLinks() {
    $('a, button').bind("click.disableAll", function() { return false; });
    $('.list-group-item').addClass('disabled');
    $('.customBtnNavi').addClass('disabled');
}

function enableAllLinks() {
	$('a, button').unbind("click.disableAll");
	$('.list-group-item').removeClass('disabled');
	$('.customBtnNavi').removeClass('disabled');
}
