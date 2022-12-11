// Button component
function Button(props) {
  return React.createElement(
    "a",
    { className: "btn btn-primary", href: props.href || '#', role: "button" },
    props.text
  );
}

// SubHeader displays additional information for user
function SubHeader(props) {
  return React.createElement(
    "div",
    { className: "row justify-content-center mt-5" },
    React.createElement(
      "p",
      { className: "text-center" },
      props.msg
    ),
    React.createElement(
      "div",
      { className: "d-flex w-50 justify-content-center mt-3" },
      React.createElement(Button, { text: "Transfer Another", href: "/" })
    )
  );
}

// Header displays information about transfer
function Header(props) {
  return React.createElement(
    "div",
    { className: "row justify-content-center" },
    React.createElement(
      "h3",
      { className: "display-4 text-center" },
      props.msg
    ),
    React.createElement(
      "div",
      { className: "mt-5 mb-2 text-center display-1 text-danger" },
      React.createElement("i", { className: "fa-regular fa-circle-xmark" })
    )
  );
}

// Main Component
function Content() {
  return React.createElement(
    "div",
    { className: "mt-5" },
    React.createElement(Header, { msg: ERR_MSG }),
    React.createElement(SubHeader, { msg: "You entered an invalid Spotify link. Check the URL and try again." })
  );
}

var root = ReactDOM.createRoot(document.getElementById('root'));
root.render(React.createElement(Content, null));