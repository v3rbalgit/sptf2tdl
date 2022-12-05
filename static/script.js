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
    url = msg.url;
    // query_string = '?';

    // if (msg.notfound) {
    //   for (let i = 0; i < msg.notfound.length; i++) {
    //     if (i == msg.notfound.length) {
    //       query_string += `t${i}=${msg.notfound[i].track_name}&`;
    //       query_string += `a${i}=${msg.notfound[i].track_artists}`;
    //       break;
    //     }

    //     query_string += `t${i}=${msg.notfound[i].track_name}&`;
    //     query_string += `a${i}=${msg.notfound[i].track_artists}&`;
    //   }
    // }
    // location.href = msg.notfound ? msg.url + query_string : msg.url;
    location.href = msg.url;
  });
});
