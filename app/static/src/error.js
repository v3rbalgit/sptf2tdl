// Button component
function Button(props) {
  return (
    <a className="btn btn-primary" href={props.href || '#'} role="button">
      {props.text}
    </a>
  );
}

// SubHeader displays additional information for user
function SubHeader(props) {
  return (
    <div className="row justify-content-center mt-5">
      <p className="text-center">{props.msg}</p>
      <div className="d-flex w-50 justify-content-center mt-3">
        <Button text="Transfer Another" href="/" />
      </div>
    </div>
  );
}

// Header displays information about transfer
function Header(props) {
  return (
    <div className="row justify-content-center">
      <h3 className="display-4 text-center">{props.msg}</h3>
      <div className="mt-5 mb-2 text-center display-1 text-danger">
        <i className="fa-regular fa-circle-xmark"></i>
      </div>
    </div>
  );
}

// Main Component
function Content() {
  return (
    <div className="mt-5">
      <Header msg={ERR_MSG} />
      <SubHeader msg="You entered an invalid Spotify link. Check the URL and try again." />
    </div>
  );
}

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(<Content />);
