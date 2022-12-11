let socket = io('/transfer');

// Button component
function Button(props) {
  if (props.onClick) {
    return (
      <a className="btn btn-primary" href={props.href || '#'} role="button" onClick={props.onClick}>
        {props.text}
      </a>
    );
  }
  return (
    <a className="btn btn-primary" href={props.href || '#'} role="button">
      {props.text}
    </a>
  );
}

// NotFoundInfo component used to display tracks that were not found on TIDAL
function NotFoundInfo(props) {
  return (
    <div className="row mt-5">
      <h4 className="mb-3">Following tracks were not found on TIDAL:</h4>
      <div>
        {props.notFound.map((track, i) => {
          return (
            <p key={i} className="text-muted">
              {track.index}/{props.total} "{track.name}" by {track.artists}
            </p>
          );
        })}
      </div>
    </div>
  );
}

// TrackInfo component displays transfer progress
function TrackInfo(props) {
  return (
    <div className="row">
      {props.nextTrack && (
        <div>
          <div className="progress">
            <div
              className="progress-bar"
              role="progressbar"
              aria-label="Transfer progress"
              style={{
                width: Math.round((props.nextTrack.index / props.total) * 100).toString() + '%',
              }}
              aria-valuenow={Math.round((props.nextTrack.index / props.total) * 100)}
              aria-valuemin="0"
              aria-valuemax="100"
            ></div>
          </div>
          <div className="justify-content-center">
            <h3 className="d-block mb-5 mt-5">
              {props.nextTrack.index}/{props.total} "{props.nextTrack.name}" by {props.nextTrack.artists}
            </h3>
            <img
              src={props.nextTrack.image}
              className="rounded mx-auto d-block mt-3 mb-3"
              alt={props.nextTrack.name + ' by ' + props.nextTrack.artists}
              width="480"
              height="480"
            />
          </div>
        </div>
      )}
      {!props.nextTrack && (
        <div className="d-flex justify-content-center align-items-center">
          <div className="spinner-border" role="status">
            <span className="visually-hidden">Loading...</span>
          </div>
        </div>
      )}
    </div>
  );
}

// SubHeader displays additional information for user
function SubHeader(props) {
  const [text, setText] = React.useState('');

  React.useEffect(() => {
    if (!props.exists && !props.empty) {
      setText(
        'Please wait until the process finishes. Depending on length of the playlist, this may take sime time...'
      );
    }
    if (props.empty) {
      setText(`Playlist you entered doesn't contain any tracks. Would you like to transfer another playlist?`);
    }
    if (props.exists) {
      setText(`This playlist already exists on your account. Would you like to overwrite it or transfer another one?`);
    }
  });

  return (
    <div className="row justify-content-center mt-5">
      <p className="text-center">{text}</p>
      <div className="d-flex w-50 justify-content-evenly mt-3">
        {props.exists && <Button text="Overwrite" onClick={props.overwriteEvent} />}
        {(props.exists || props.empty) && <Button text="Transfer Another" href="/" />}
      </div>
    </div>
  );
}

// Header displays information about transfer
function Header(props) {
  const [text, setText] = React.useState('');

  React.useEffect(() => {
    if (!props.exists && !props.empty) {
      setText(`Transferring playlist "${props.playlist}" to TIDAL`);
    }

    if (props.exists) {
      setText(`Playlist "${props.playlist}" already exists`);
    }

    if (props.empty) {
      setText(`Playlist "${props.playlist}" is empty`);
    }
    document.title = text;
  });

  return (
    <div className="row justify-content-center">
      <h3 className="display-4 text-center">{text}</h3>
      {(props.exists || props.empty) && (
        <div className="mt-5 mb-2 text-center display-1 text-danger">
          <i className="fa-regular fa-circle-xmark"></i>
        </div>
      )}
    </div>
  );
}

// Displays transfer result after it has finished
function TransferInfo(props) {
  React.useEffect(() => {
    document.title = `Playlist "${props.playlist}" successfully transferred!`;
  });

  return (
    <div>
      <div className="row justify-content-center">
        <h3 className="display-4 text-center">Transfer complete</h3>
        <div className="mt-4 mb-4 text-center display-1 text-success">
          <i className="fa-solid fa-check"></i>
        </div>
      </div>
      <div className="row mt-3">
        <p className="text-center">
          {props.notFound
            ? props.total - props.notFound.length + ' out of ' + props.total + ' tracks in'
            : 'All tracks in'}{' '}
          playlist "{props.playlist}" have been successfully transferred to your TIDAL account.
        </p>
        {props.notFound.length != 0 && <NotFoundInfo notFound={props.notFound} total={props.total} />}
      </div>
      <div className="d-flex justify-content-center mt-3">
        <Button text="Transfer Another" href="/" />
      </div>
    </div>
  );
}

// Main Component
function Content() {
  const [playlistState, updatePlaylistState] = React.useState({
    playlistExists: false,
    playlistEmpty: false,
  });

  const [playlistInfo, updatePlaylistInfo] = React.useState({
    name: PLAYLIST_NAME,
    totalTracks: 0,
  });

  const [nextTrack, updateNextTrack] = React.useState(null);

  const [notFound, updateNotFound] = React.useState([]);

  const [finished, updateFinished] = React.useState(false);

  React.useEffect(() => {
    socket.on('playlist_info', (msg) => {
      updatePlaylistInfo({
        name: msg.name,
        totalTracks: msg.total,
      });
    });

    socket.on('next_track', (msg) => {
      updateNextTrack({
        index: msg.index + 1,
        name: msg.name,
        artists: msg.artists,
        image: msg.image,
      });
    });

    socket.on('no_match', (msg) => {
      updateNotFound([
        ...notFound,
        {
          index: msg.index + 1,
          name: msg.name,
          artists: msg.artists,
        },
      ]);
    });

    socket.on('playlist_exists', () => {
      updatePlaylistState({
        ...playlistState,
        playlistExists: true,
      });
    });

    socket.on('playlist_empty', () => {
      updatePlaylistState({
        ...playlistState,
        playlistEmpty: true,
      });
    });

    socket.on('finished', () => {
      updateFinished(true);
    });

    socket.emit('start_transfer', false);

    return () => {
      socket.off('start_transfer');
      socket.off('playlist_empty');
      socket.off('playlist_exists');
      socket.off('no_match');
      socket.off('next_track');
      socket.off('finished');
    };
  }, []);

  overwrite = (event) => {
    event.preventDefault();

    updatePlaylistInfo({
      totalTracks: 0,
      name: PLAYLIST_NAME,
    });
    updatePlaylistState({
      playlistExists: false,
      playlistEmpty: false,
    });
    updateNotFound([]);
    updateNextTrack(null);

    socket.emit('start_transfer', true);
  };

  if (!finished) {
    return (
      <div className="mt-5">
        <Header
          playlist={playlistInfo.name}
          exists={playlistState.playlistExists}
          empty={playlistState.playlistEmpty}
        />
        <SubHeader
          exists={playlistState.playlistExists}
          empty={playlistState.playlistEmpty}
          overwriteEvent={overwrite}
        />
        {!playlistState.playlistExists && !playlistState.playlistEmpty && (
          <TrackInfo nextTrack={nextTrack} total={playlistInfo.totalTracks} />
        )}
      </div>
    );
  } else {
    return (
      <div className="mt-5">
        <TransferInfo playlist={playlistInfo.name} notFound={notFound} total={playlistInfo.totalTracks} />
      </div>
    );
  }
}

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(<Content />);
