var _slicedToArray = function () { function sliceIterator(arr, i) { var _arr = []; var _n = true; var _d = false; var _e = undefined; try { for (var _i = arr[Symbol.iterator](), _s; !(_n = (_s = _i.next()).done); _n = true) { _arr.push(_s.value); if (i && _arr.length === i) break; } } catch (err) { _d = true; _e = err; } finally { try { if (!_n && _i["return"]) _i["return"](); } finally { if (_d) throw _e; } } return _arr; } return function (arr, i) { if (Array.isArray(arr)) { return arr; } else if (Symbol.iterator in Object(arr)) { return sliceIterator(arr, i); } else { throw new TypeError("Invalid attempt to destructure non-iterable instance"); } }; }();

function _toConsumableArray(arr) { if (Array.isArray(arr)) { for (var i = 0, arr2 = Array(arr.length); i < arr.length; i++) { arr2[i] = arr[i]; } return arr2; } else { return Array.from(arr); } }

var socket = io('/transfer');

// Button component
function Button(props) {
  if (props.onClick) {
    return React.createElement(
      'a',
      { className: 'btn btn-primary', href: props.href || '#', role: 'button', onClick: props.onClick },
      props.text
    );
  }
  return React.createElement(
    'a',
    { className: 'btn btn-primary', href: props.href || '#', role: 'button' },
    props.text
  );
}

// NotFoundInfo component used to display tracks that were not found on TIDAL
function NotFoundInfo(props) {
  return React.createElement(
    'div',
    { className: 'row mt-5' },
    React.createElement(
      'h4',
      { className: 'mb-3' },
      'Following tracks were not found on TIDAL:'
    ),
    React.createElement(
      'div',
      null,
      props.notFound.map(function (track, i) {
        return React.createElement(
          'p',
          { key: i, className: 'text-muted' },
          track.index,
          '/',
          props.total,
          ' "',
          track.name,
          '" by ',
          track.artists
        );
      })
    )
  );
}

// TrackInfo component displays transfer progress
function TrackInfo(props) {
  return React.createElement(
    'div',
    { className: 'row' },
    props.nextTrack && React.createElement(
      'div',
      null,
      React.createElement(
        'div',
        { className: 'progress' },
        React.createElement('div', {
          className: 'progress-bar',
          role: 'progressbar',
          'aria-label': 'Transfer progress',
          style: {
            width: Math.round(props.nextTrack.index / props.total * 100).toString() + '%'
          },
          'aria-valuenow': Math.round(props.nextTrack.index / props.total * 100),
          'aria-valuemin': '0',
          'aria-valuemax': '100'
        })
      ),
      React.createElement(
        'div',
        { className: 'justify-content-center' },
        React.createElement(
          'h3',
          { className: 'd-block mb-5 mt-5' },
          props.nextTrack.index,
          '/',
          props.total,
          ' "',
          props.nextTrack.name,
          '" by ',
          props.nextTrack.artists
        ),
        React.createElement('img', {
          src: props.nextTrack.image,
          className: 'rounded mx-auto d-block mt-3 mb-3',
          alt: props.nextTrack.name + ' by ' + props.nextTrack.artists,
          width: '480',
          height: '480'
        })
      )
    ),
    !props.nextTrack && React.createElement(
      'div',
      { className: 'd-flex justify-content-center align-items-center' },
      React.createElement(
        'div',
        { className: 'spinner-border', role: 'status' },
        React.createElement(
          'span',
          { className: 'visually-hidden' },
          'Loading...'
        )
      )
    )
  );
}

// SubHeader displays additional information for user
function SubHeader(props) {
  var _React$useState = React.useState(''),
      _React$useState2 = _slicedToArray(_React$useState, 2),
      text = _React$useState2[0],
      setText = _React$useState2[1];

  React.useEffect(function () {
    if (!props.exists && !props.empty) {
      setText('Please wait until the process finishes. Depending on length of the playlist, this may take sime time...');
    }
    if (props.empty) {
      setText('Playlist you entered doesn\'t contain any tracks. Would you like to transfer another playlist?');
    }
    if (props.exists) {
      setText('This playlist already exists on your account. Would you like to overwrite it or transfer another one?');
    }
  });

  return React.createElement(
    'div',
    { className: 'row justify-content-center mt-5' },
    React.createElement(
      'p',
      { className: 'text-center' },
      text
    ),
    React.createElement(
      'div',
      { className: 'd-flex w-50 justify-content-evenly mt-3' },
      props.exists && React.createElement(Button, { text: 'Overwrite', onClick: props.overwriteEvent }),
      (props.exists || props.empty) && React.createElement(Button, { text: 'Transfer Another', href: '/' })
    )
  );
}

// Header displays information about transfer
function Header(props) {
  var _React$useState3 = React.useState(''),
      _React$useState4 = _slicedToArray(_React$useState3, 2),
      text = _React$useState4[0],
      setText = _React$useState4[1];

  React.useEffect(function () {
    if (!props.exists && !props.empty) {
      setText('Transferring playlist "' + props.playlist + '" to TIDAL');
    }

    if (props.exists) {
      setText('Playlist "' + props.playlist + '" already exists');
    }

    if (props.empty) {
      setText('Playlist "' + props.playlist + '" is empty');
    }
    document.title = text;
  });

  return React.createElement(
    'div',
    { className: 'row justify-content-center' },
    React.createElement(
      'h3',
      { className: 'display-4 text-center' },
      text
    ),
    (props.exists || props.empty) && React.createElement(
      'div',
      { className: 'mt-5 mb-2 text-center display-1 text-danger' },
      React.createElement('i', { className: 'fa-regular fa-circle-xmark' })
    )
  );
}

// Displays transfer result after it has finished
function TransferInfo(props) {
  React.useEffect(function () {
    document.title = 'Playlist "' + props.playlist + '" successfully transferred!';
  });

  return React.createElement(
    'div',
    null,
    React.createElement(
      'div',
      { className: 'row justify-content-center' },
      React.createElement(
        'h3',
        { className: 'display-4 text-center' },
        'Transfer complete'
      ),
      React.createElement(
        'div',
        { className: 'mt-4 mb-4 text-center display-1 text-success' },
        React.createElement('i', { className: 'fa-solid fa-check' })
      )
    ),
    React.createElement(
      'div',
      { className: 'row mt-3' },
      React.createElement(
        'p',
        { className: 'text-center' },
        props.notFound ? props.total - props.notFound.length + ' out of ' + props.total + ' tracks in' : 'All tracks in',
        ' ',
        'playlist "',
        props.playlist,
        '" have been successfully transferred to your TIDAL account.'
      ),
      props.notFound.length != 0 && React.createElement(NotFoundInfo, { notFound: props.notFound, total: props.total })
    ),
    React.createElement(
      'div',
      { className: 'd-flex justify-content-center mt-3' },
      React.createElement(Button, { text: 'Transfer Another', href: '/' })
    )
  );
}

// Main Component
function Content() {
  var _React$useState5 = React.useState({
    playlistExists: false,
    playlistEmpty: false
  }),
      _React$useState6 = _slicedToArray(_React$useState5, 2),
      playlistState = _React$useState6[0],
      updatePlaylistState = _React$useState6[1];

  var _React$useState7 = React.useState({
    name: PLAYLIST_NAME,
    totalTracks: 0
  }),
      _React$useState8 = _slicedToArray(_React$useState7, 2),
      playlistInfo = _React$useState8[0],
      updatePlaylistInfo = _React$useState8[1];

  var _React$useState9 = React.useState(null),
      _React$useState10 = _slicedToArray(_React$useState9, 2),
      nextTrack = _React$useState10[0],
      updateNextTrack = _React$useState10[1];

  var _React$useState11 = React.useState([]),
      _React$useState12 = _slicedToArray(_React$useState11, 2),
      notFound = _React$useState12[0],
      updateNotFound = _React$useState12[1];

  var _React$useState13 = React.useState(false),
      _React$useState14 = _slicedToArray(_React$useState13, 2),
      finished = _React$useState14[0],
      updateFinished = _React$useState14[1];

  React.useEffect(function () {
    socket.on('playlist_info', function (msg) {
      updatePlaylistInfo({
        name: msg.name,
        totalTracks: msg.total
      });
    });

    socket.on('next_track', function (msg) {
      updateNextTrack({
        index: msg.data.index + 1,
        name: msg.data.name,
        artists: msg.data.artists,
        image: msg.data.image
      });
    });

    socket.on('no_match', function (msg) {
      updateNotFound([].concat(_toConsumableArray(notFound), [{
        index: msg.data.index + 1,
        name: msg.data.name,
        artists: msg.data.artists
      }]));
    });

    socket.on('playlist_exists', function () {
      updatePlaylistState(Object.assign({}, playlistState, {
        playlistExists: true
      }));
    });

    socket.on('playlist_empty', function () {
      updatePlaylistState(Object.assign({}, playlistState, {
        playlistEmpty: true
      }));
    });

    socket.on('finished', function () {
      updateFinished(true);
    });

    socket.emit('start_transfer', false);

    return function () {
      socket.off('start_transfer');
      socket.off('playlist_empty');
      socket.off('playlist_exists');
      socket.off('no_match');
      socket.off('next_track');
      socket.off('finished');
    };
  }, []);

  overwrite = function overwrite(event) {
    event.preventDefault();

    updatePlaylistInfo({
      totalTracks: 0,
      name: PLAYLIST_NAME
    });
    updatePlaylistState({
      playlistExists: false,
      playlistEmpty: false
    });
    updateNotFound([]);
    updateNextTrack(null);

    socket.emit('start_transfer', true);
  };

  if (!finished) {
    return React.createElement(
      'div',
      { className: 'mt-5' },
      React.createElement(Header, {
        playlist: playlistInfo.name,
        exists: playlistState.playlistExists,
        empty: playlistState.playlistEmpty
      }),
      React.createElement(SubHeader, {
        exists: playlistState.playlistExists,
        empty: playlistState.playlistEmpty,
        overwriteEvent: overwrite
      }),
      !playlistState.playlistExists && !playlistState.playlistEmpty && React.createElement(TrackInfo, { nextTrack: nextTrack, total: playlistInfo.totalTracks })
    );
  } else {
    return React.createElement(
      'div',
      { className: 'mt-5' },
      React.createElement(TransferInfo, { playlist: playlistInfo.name, notFound: notFound, total: playlistInfo.totalTracks })
    );
  }
}

var root = ReactDOM.createRoot(document.getElementById('root'));
root.render(React.createElement(Content, null));