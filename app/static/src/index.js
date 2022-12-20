'use strict';

class Warning extends React.Component {
  handleClick = () => {
    location.href = `${location.href}transfer`;
  };
  render() {
    return (
      <div className="m-5 w-50">
        <p className="bg-warning rounded p-3 text-center">
          Please <a href={LOGIN_URI} target="_blank" id="tidal-link" onClick={this.handleClick}>
            <strong>CLICK HERE</strong>
          </a>{' '}
          to login to TIDAL
        </p>
      </div>
    );
  }
}

class PlaylistForm extends React.Component {
  render() {
    return (
      <div className="mt-3 col-6">
        <form action="/" method="POST">
          <div className="row mt-5">
            <input type="text" className="form-control" id="playlistLink" name="link" required />
          </div>
          <div className="d-grid gap-2 col-4 mx-auto mt-5">
            <input type="submit" className="btn btn-primary" id="submit" name="submit" value="Transfer" />
          </div>
        </form>
      </div>
    );
  }
}

class Content extends React.Component {
  render() {
    return (
      <div className="row justify-content-center mt-5">
        <div className="col-8">
          <h3 className="display-4 text-center">Transfer your favourite Spotify playlists to TIDAL</h3>
        </div>
        <div className="col-9 mt-5">
          <p className="text-center">
            Enter link to your desired Spotify playlist, press Transfer, login to your TIDAL account <br /> and watch
            the magic happen
          </p>
        </div>
        <PlaylistForm />
        {LOGIN_URI != '' && <Warning />}
      </div>
    );
  }
}

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(<Content />);
