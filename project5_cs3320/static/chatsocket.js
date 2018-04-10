
var socket = io();

var $cont = $('.chats');
$cont[0].scrollTop = $cont[0].scrollHeight;


socket.on('connect', function(){
    var name = document.getElementById('username').value;
    var chat_topic = document.getElementById('chat_key').value;
    socket.emit('join_room', {'username': name, 'topic': chat_topic});
});

//socket.on('disconnect', function(){
//    var chat_topic = document.getElementById('chat_key').value;
//    socket.emit('leave_room', {'topic': chat_topic});
//});

//This function is called when the send button of the chat is pressed
$('form').submit(function(){
    var input_message = document.getElementById('chat-input').value;
    document.getElementById('chat-input').value = "";
    $cont[0].scrollTop = $cont[0].scrollHeight;
    //Emit to server
    //socket.emit('message', input_message);
    var user = document.getElementById('username').value;
    var topic = document.getElementById('chat_key').value;
    socket.emit('json', {'msg': input_message, 'username': user, 'room': topic});
    return false;
});


// Receive emit from server
socket.on('message', function(msg) {
    console.log('received message %s', msg);
    $('#messages').append($('<li>').text(msg));
    //addMessage(msg);
});

// Receive emit from server
socket.on('json', function(data) {
    console.log('received message %s', data);
});

socket.on('join_room', function(data) {
    var user = data['username']
    var room_name = data['room']
   console.log(user + ' joined ' + room_name + ' room')
    $('#user-list').append($('<li>').text(user));

});


//This function adds a message to the chat page
function addMessage(message){
    var list_item = document.createElement("li");
    var node = document.createTextNode(message);
    list_item.appendChild(node);
    var element = document.getElementById("messages");
    element.appendChild(list_item);
}



