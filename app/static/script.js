$(document).ready(function () {
  let socket = io('/transfer');

  let not_found = [];
  let total = 0;
  let playlist = '';

  socket.on('next_track', function (msg) {
    total = msg.data.total;
    playlist = msg.data.playlist;

    $('#track_info').text(`${msg.data.index + 1}/${msg.data.total} "${msg.data.name}" by ${msg.data.artists}`);
  });

  socket.on('not_found', function (msg) {
    not_found.push({
      index: msg.data.index,
      name: msg.data.name,
      artists: msg.data.artists,
    });
  });

  socket.on('finished', function () {
    document.title = `Playlist "${playlist}" successfully transferred!`;
    $('.page-header h1').text(`Successfully transferred "${playlist}" to TIDAL!`);
    $('#info').removeClass('d-none');
    $('#track_info').parent().addClass('d-none');
    not_found_html = not_found.map((track) => {
      return `<p class="m-1">${track.index + 1}/${total} "${track.name}" by ${track.artists}</p>`;
    });
    $('#results').html(not_found_html);
  });

  socket.on('overwrite_playlist', function (msg) {
    document.title = `Playlist "${msg}" already exists!`;
    $('.page-header h1').text(`Playlist "${msg}" already exists.`);
    $('#track_info').text(`Would you like to overwrite existing playlist or transfer another one?`);
    $('#track_info ~ a').removeClass('d-none');
    $('#overwrite').click(function () {
      document.title = `Transferring Spotify Playlist "${msg}"`;
      $('.page-header h1').text(`Transferring playlist "${msg}" to TIDAL...`);
      $('#info').addClass('d-none');
      $('#track_info').text('Loading...');
      $('#track_info ~ a').addClass('d-none');
      socket.emit('start_transfer', true);
    });
  });

  socket.emit('start_transfer', false);
});
