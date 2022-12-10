$(document).ready(function () {
  let socket = io('/transfer');

  let not_found = [];
  let total = 0;
  let playlist = '';

  socket.on('next_track', function (msg) {
    total = msg.data.total;
    playlist = msg.data.playlist;

    $('#track_info').text(`${msg.data.index + 1}/${total} "${msg.data.name}" by ${msg.data.artists}`);
  });

  socket.on('no_match', function (msg) {
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

  socket.on('playlist_exists', function (msg) {
    document.title = `Playlist "${msg}" already exists!`;
    $('.page-header h1').text(`Playlist "${msg}" already exists.`);
    $('#track_info').text(`Would you like to overwrite existing playlist or transfer another one?`);
    $('#track_info ~ a').removeClass('d-none');
    $('#overwrite').click(function () {
      document.title = `Transferring Spotify Playlist "${msg}"`;
      $('.page-header h1').text(`Transferring playlist "${msg}" to TIDAL...`);
      $('#info').addClass('d-none');
      $('#track_info ~ a').addClass('d-none');
      $('#track_info').text('Loading...');
      socket.emit('start_transfer', true);
    });
  });

  socket.on('playlist_empty', function (msg) {
    document.title = `Playlist "${msg}" is empty.`;
    $('.page-header h1').text(`Playlist "${msg}" doesn't contain any tracks.`);
    $('#track_info').text(`Would you like to transfer another playlist?`);
    $('#track_info ~ a:last-child').removeClass('d-none');
  });

  socket.emit('start_transfer', false);
});
