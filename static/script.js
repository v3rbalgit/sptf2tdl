$(document).ready(function () {
  // sending a connect request to the server.
  let socket = io('/transfer');
  socket.emit('track');
  socket.on('track', function (msg) {
    $('#track_info').append(
      '<br>' + $('<div/>').text(`${msg.data.index}/${msg.total} "${msg.data.name}" by ${msg.data.artists}`).html()
    );
  });
  socket.on('success', function (msg) {
    location.href = msg.url;
  });
  socket.on('error', function (msg) {
    location.href = msg.url;
  });
});
