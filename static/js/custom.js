

var clipboard = new Clipboard('[data-clipboard]');

clipboard.on('success', function (e) {

    var ele = e.trigger;
    ele.title = 'Copied!';

    $(ele).tooltip('show');

    e.clearSelection();
});

clipboard.on('error', function (e) {

    var ele = e.trigger;
    ele.title = 'Press Ctrl+C to copy';
    $(ele).tooltip('show');

});