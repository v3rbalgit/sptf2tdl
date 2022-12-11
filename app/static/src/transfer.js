// Button component
function Button(props) {
  if (props.onClick) {
    return (
      <a
        className={'btn btn-primary ' + props.className}
        href={props.href || '#'}
        role="button"
        onClick={props.onClick}
      >
        {props.text}
      </a>
    );
  }
  return (
    <a className={'btn btn-primary ' + props.className} href={props.href || '#'} role="button">
      {props.text}
    </a>
  );
}

// NotFoundInfo component used to display tracks that were not found on TIDAL
function NotFoundInfo(props) {
  return (
    <div className="row mt-5">
      <h3 className="mb-3">Following tracks were not found on TIDAL:</h3>
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
    <div className="row mt-5 h-75">
      {props.nextTrack && (
        <div>
          <div className="progress">
            <div
              className="progress-bar"
              role="progressbar"
              aria-label="Transfer progress"
              style={{ width: Math.round((props.nextTrack.index / props.total) * 100).toString() + '%' }}
              aria-valuenow={Math.round((props.nextTrack.index / props.total) * 100)}
              aria-valuemin="0"
              aria-valuemax="100"
            ></div>
          </div>
          <div className="justify-content-center">
            <h3 className="display-6 d-block mb-5 mt-5">
              {props.nextTrack.index}/{props.total} "{props.nextTrack.name}" by {props.nextTrack.artists}
            </h3>
            <img
              src={props.nextTrack.image}
              className="rounded mx-auto d-block mt-3 mb-3"
              alt={props.nextTrack.name + ' by ' + props.nextTrack.artists}
              width="500"
              height="500"
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
    <div className="col-9 mt-5">
      <p className="text-center">{text}</p>
      <div className="d-grid gap-2 col-4 mx-auto mt-5">
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
    <div className="col-8 mt-5">
      <h3 className="display-4 text-center">{text}</h3>
    </div>
  );
}

function TransferInfo(props) {
  React.useEffect(() => {
    document.title = `Playlist "${props.playlist}" successfully transferred!`;
  });

  return (
    <div className="row justify-content-center mt-5">
      <div className="col-8 mt-5">
        <h3 className="display-4 text-center">Transfer complete</h3>
      </div>
      <div className="col-9 mt-5">
        <p className="text-center">
          {props.notFound
            ? props.total - props.notFound.length + ' out of ' + props.total + ' tracks in'
            : 'All tracks in'}{' '}
          playlist "{props.playlist}" have been successfully transferred to your TIDAL account.
        </p>
        {props.notFound && <NotFoundInfo notFound={props.notFound} total={props.total} />}
      </div>
      <div className="d-grid gap-2 col-4 mx-auto mt-5">
        <Button text="Transfer Another" href="/" />
      </div>
    </div>
  );
}

// Main Component
function Content() {
  let socket = io('/transfer');

  const [state, setState] = React.useState({
    total: 0,
    playlist: PLAYLIST_NAME,
    nextTrack: null,
    playlistExists: false,
    playlistEmpty: false,
  });

  const [nextTrack, setNextTrack] = React.useState(null);

  const [notFound, setNotFound] = React.useState([]);

  const [finished, setFinished] = React.useState(false);

  overwrite = (event) => {
    event.preventDefault();

    setState(...state);

    setNextTrack(null);

    socket.emit('start_transfer', true);
  };

  React.useEffect(() => {
    socket.on('next_track', (msg) => {
      setNextTrack({
        index: msg.data.index + 1,
        name: msg.data.name,
        artists: msg.data.artists,
        image: msg.data.image,
      });

      setState({
        ...state,
        total: msg.data.total,
        playlist: msg.data.playlist,
      });
    });

    socket.on('no_match', (msg) => {
      setNotFound([
        ...notFound,
        {
          index: msg.data.index + 1,
          name: msg.data.name,
          artists: msg.data.artists,
        },
      ]);
    });

    socket.on('playlist_exists', () => {
      setState({
        ...state,
        playlistExists: true,
      });
    });

    socket.on('playlist_empty', () => {
      setState({
        ...state,
        playlistEmpty: true,
      });
    });

    socket.on('finished', () => {
      setFinished(true);
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

  if (!finished) {
    return (
      <div className="row justify-content-center mt-5">
        <Header playlist={state.playlist} exists={state.playlistExists} empty={state.playlistEmpty} />
        <SubHeader exists={state.playlistExists} empty={state.playlistEmpty} overwriteEvent={overwrite} />
        {!state.playlistExists && !state.playlistEmpty && <TrackInfo nextTrack={nextTrack} total={state.total} />}
      </div>
    );
  } else {
    return <TransferInfo playlist={state.playlist} notFound={notFound} total={state.total} />;
  }
}

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(<Content />);
