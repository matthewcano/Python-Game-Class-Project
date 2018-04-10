
var socket = io();

// This initializes health bar on load
$(window).on('load', function() {
    // Set up health bars
    var p1_health = Number($('#p1-health-value').html());
    var p2_health = Number($('#p2-health-value').html());
    healthBar('#p1-health', p1_health);
    healthBar('#p2-health', p2_health);

    // Determine if action has been made by user
    var userAction = $('#action_exist').val;
    if (userAction != "Nah") {
        $(userAction).addClass('chosen-one');
        $('.combat-action').attr('disabled', 'true');
    }
});

// This function readjusts the health bar
function healthBar(elementName, health) {
    var i;
    for (i = 0; i < health; i++) {
        $(elementName).append('<img src="/static/health.png" class="health" />');
    }
}

// This triggers when they select an action
$('.combat-action').on('click', function() {
    $('.combat-action').attr('disabled', 'true');
    $(this).addClass('chosen-one');

    var action = $(this).id;
    var u_name = $('#fight_username').html;
    var key = $('#chat_key').value;

    socket.emit('incoming_action', {'action_name': action, 'user_name': u_name, 'key': key});
});

// Receive emit from server. Both users have acted!
socket.on('successful_action', function(data) {
    // Display proper message
    var user_act = data['user_action'];
    var opponent_act = data['opponent_action'];
    var me_dmg = data['me_dmg'];
    var you_dmg = data['you_dmg'];

    if (user_act == 'attack') {
        $('#combat_log').html = "You attacked!";
    }
    if (user_act == 'defense') {
        $('#combat_log').html = "You defended valliantly!";
    }
    if (user_act == 'p_attack') {
        $('#combat_log').html = "You attacked with all of your strength!!";
    }
    $('#combat_log').append('<br>');
    if (opponent_act == 'attack') {
        $('#combat_log').append('They attacked you!');
    }
    if (opponent_act == 'p_attack') {
        $('#combat_log').append('They attacked you with all of their strength!!');
    }
    if (opponent_act == 'defend') {
        $('#combat_log').append('They defended against your attack!');
    }
    $('#combat_log').append('<br>');
    if (you_dmg == 0) {
        $('#combat_log').append('They took no damage!');
    }
    if (you_dmg != 0) {
        $('#combat_log').append('They took ');
        $('#combat_log').append(you_dmg);
        $('#combat_log').append(' damage!');
    }
    $('#combat_log').append('<br>');
    if (me_dmg == 0) {
        $('#combat_log').append('You took no damage!');
    }
    if (me_dmg != 0) {
        $('#combat_log').append('You took ');
        $('#combat_log').append(me_dmg);
        $('#combat_log').append(' damage!');
    }

    //Adjust Health
    var user_hp = data['user_hp'];
    var opponent_hp = data['opponent_hp'];
    $('#p1-health').html = user_hp;
    $('#p2-health').html = opponent_hp;
    // Fix Health Bars
    $('.health').remove();
    healthBar('#p1-health', user_hp);
    healthBar('#p2-health', opponent_hp);

    // Reset Buttons to neutral positions
    $('.combat-action').attr('disabled', 'false');
    $('.combat-action').removeClass('chosen-one');

});