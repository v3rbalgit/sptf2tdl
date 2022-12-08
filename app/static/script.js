$(document).ready(function () {
  let socket = io('/transfer');

  let not_found = [];
  let total = 0;
  let playlist = '';

  socket.on('track', function (msg) {
    if (msg.data.found == false) {
      not_found.push({
        index: msg.data.index,
        name: msg.data.name,
        artists: msg.data.artists,
      });
    }
    total = msg.data.total;
    playlist = msg.data.playlist;

    $('#track_info').text(`${msg.data.index + 1}/${msg.data.total} "${msg.data.name}" by ${msg.data.artists}`);

    if (msg.data.index + 1 == msg.data.total) {
      document.title = `Playlist "${playlist}" Successfully Transferred!`;
      $('.page-header h1').text(`Successfully transfered ${playlist} to TIDAL!`);
      $('.d-none').removeClass('d-none');
      $('#track_info').parent().addClass('d-none');
      not_found_html = not_found.map((track) => {
        return `<p class="m-1">${track.index + 1}/${total} "${track.name}" by ${track.artists}</p>`;
      });
      $('#results').html(not_found_html);
    } else {
      socket.emit('track', { index: msg.data.index + 1 });
    }
  });

  socket.emit('track', { index: 0 });
});
