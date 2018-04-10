console.log('got to waitingroom');
var socket = io();
socket.on('two in waitinglist', function (urlToRedirectTo) {
    console.log('received message %s', urlToRedirectTo);
    console.log('redirecting...')
    window.location.replace(urlToRedirectTo);
});