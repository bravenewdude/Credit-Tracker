var loader = '<img src="images/ajaxloadersmall.gif" />';

function Email(element, field) {
  var email = element.text();
  var newemail = prompt("Enter email address: ", email);
  if (newemail==null || newemail=='' || newemail==email) { return false; }
  $('#message').html(loader);
  $.ajax({
    type: 'PUT',
    url: '/User',
    data: { userid: userid, field: field, data: newemail },
    success: function(response) {
      element.text(newemail);
      $('#message').html('').text(response);
    }
  });
  return false;
}
function Update(addminutes) {
  minutes = minutes + addminutes;
  credits = parseInt(minutes/60);
  $('#numcredits').text(credits);
}
function Minutes() {
  var addminutes = parseInt($('#minutes').val());
  $('#minutes').val('').focus();
  $('#message').html(loader);
  $.ajax({
    type: 'PUT',
    url: '/User',
    data: { userid: userid, field: 'minutes', data: addminutes },
    success: function(response) {
      minutestoday += addminutes;
      Update(addminutes);
      $('#message').html('').text(response);
      $('#minutestoday').text(minutestoday);
    }
  });
  return false;
}
function Exercise() {
  $('#message').html(loader);
  $('input').blur();
  $.ajax({
    type: 'PUT',
    url: '/User',
    data: { userid: userid, field: 'exercise', data: $('#exercise').is(':checked') },
    success: function(response) {
      $('#message').html('').text(response);
    }
  });
}
function Reward(index, title) {
  if(index == 'a') {
    data = $('#newreward').val()+'__s__'+$('#newprice').val();
  }
  else {
    if(!confirm('Are you sure you would like to delete "'+title+'"?')) { return false; }
    data = '__delete____s__'+index;
  }
  $('#message').html(loader);
  $('input').blur();
  $.ajax({
    type: 'PUT',
    url: '/User',
    data: { userid: userid, field: 'reward', data: data },
    success: function(response) {
      $('#message').html('').text(response);
      location.reload(true);
    }
  });
  return false;
}
function Delete() {
  if (confirm("Are you sure you would like to DELETE your account?")) {
    $('#message').html(loader);
    $.ajax({
      type: 'DELETE',
      url: '/User',
      data: { userid: userid },
      success: function(response) {
        $('#message').html('').text(response);
        window.location = "/?about=t";
      }
    });
  }
  return false;
}
function Purchase(title,price) {
  if (title == "__donate__") {
    price = parseInt($('#donate').val());
    mystring = "donate ";
    $('#donate').val('').blur();
  }
  else mystring = "purchase " + title + " for ";
  if (minutes < 60*price) {
    alert("You do not have enough credits.");
    return false;
  }
  if (confirm("Are you sure you would like to " + mystring + price + " credits?")) {
    $('#message').html(loader);
    $.ajax({
      type: 'POST',
      url: '/User',
      data: { userid: userid, title: title, cost: 60*price },
      success: function(response) {
        Update(-60*price);
        $('#message').html('').text(response);
      }
    });
  }
  return false;
}
