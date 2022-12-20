'use strict';

var _createClass = function () { function defineProperties(target, props) { for (var i = 0; i < props.length; i++) { var descriptor = props[i]; descriptor.enumerable = descriptor.enumerable || false; descriptor.configurable = true; if ("value" in descriptor) descriptor.writable = true; Object.defineProperty(target, descriptor.key, descriptor); } } return function (Constructor, protoProps, staticProps) { if (protoProps) defineProperties(Constructor.prototype, protoProps); if (staticProps) defineProperties(Constructor, staticProps); return Constructor; }; }();

function _classCallCheck(instance, Constructor) { if (!(instance instanceof Constructor)) { throw new TypeError("Cannot call a class as a function"); } }

function _possibleConstructorReturn(self, call) { if (!self) { throw new ReferenceError("this hasn't been initialised - super() hasn't been called"); } return call && (typeof call === "object" || typeof call === "function") ? call : self; }

function _inherits(subClass, superClass) { if (typeof superClass !== "function" && superClass !== null) { throw new TypeError("Super expression must either be null or a function, not " + typeof superClass); } subClass.prototype = Object.create(superClass && superClass.prototype, { constructor: { value: subClass, enumerable: false, writable: true, configurable: true } }); if (superClass) Object.setPrototypeOf ? Object.setPrototypeOf(subClass, superClass) : subClass.__proto__ = superClass; }

var Warning = function (_React$Component) {
  _inherits(Warning, _React$Component);

  function Warning() {
    var _ref;

    var _temp, _this, _ret;

    _classCallCheck(this, Warning);

    for (var _len = arguments.length, args = Array(_len), _key = 0; _key < _len; _key++) {
      args[_key] = arguments[_key];
    }

    return _ret = (_temp = (_this = _possibleConstructorReturn(this, (_ref = Warning.__proto__ || Object.getPrototypeOf(Warning)).call.apply(_ref, [this].concat(args))), _this), _this.handleClick = function () {
      location.href = location.href + "transfer";
    }, _temp), _possibleConstructorReturn(_this, _ret);
  }

  _createClass(Warning, [{
    key: "render",
    value: function render() {
      return React.createElement(
        "div",
        { className: "m-5 w-50" },
        React.createElement(
          "p",
          { className: "bg-warning rounded p-3 text-center" },
          "Please ",
          React.createElement(
            "a",
            { href: LOGIN_URI, target: "_blank", id: "tidal-link", onClick: this.handleClick },
            React.createElement(
              "strong",
              null,
              "CLICK HERE"
            )
          ),
          ' ',
          "to login to TIDAL"
        )
      );
    }
  }]);

  return Warning;
}(React.Component);

var PlaylistForm = function (_React$Component2) {
  _inherits(PlaylistForm, _React$Component2);

  function PlaylistForm() {
    _classCallCheck(this, PlaylistForm);

    return _possibleConstructorReturn(this, (PlaylistForm.__proto__ || Object.getPrototypeOf(PlaylistForm)).apply(this, arguments));
  }

  _createClass(PlaylistForm, [{
    key: "render",
    value: function render() {
      return React.createElement(
        "div",
        { className: "mt-3 col-6" },
        React.createElement(
          "form",
          { action: "/", method: "POST" },
          React.createElement(
            "div",
            { className: "row mt-5" },
            React.createElement("input", { type: "text", className: "form-control", id: "playlistLink", name: "link", required: true })
          ),
          React.createElement(
            "div",
            { className: "d-grid gap-2 col-4 mx-auto mt-5" },
            React.createElement("input", { type: "submit", className: "btn btn-primary", id: "submit", name: "submit", value: "Transfer" })
          )
        )
      );
    }
  }]);

  return PlaylistForm;
}(React.Component);

var Content = function (_React$Component3) {
  _inherits(Content, _React$Component3);

  function Content() {
    _classCallCheck(this, Content);

    return _possibleConstructorReturn(this, (Content.__proto__ || Object.getPrototypeOf(Content)).apply(this, arguments));
  }

  _createClass(Content, [{
    key: "render",
    value: function render() {
      return React.createElement(
        "div",
        { className: "row justify-content-center mt-5" },
        React.createElement(
          "div",
          { className: "col-8" },
          React.createElement(
            "h3",
            { className: "display-4 text-center" },
            "Transfer your favourite Spotify playlists to TIDAL"
          )
        ),
        React.createElement(
          "div",
          { className: "col-9 mt-5" },
          React.createElement(
            "p",
            { className: "text-center" },
            "Enter link to your desired Spotify playlist, press Transfer, login to your TIDAL account ",
            React.createElement("br", null),
            " and watch the magic happen"
          )
        ),
        React.createElement(PlaylistForm, null),
        LOGIN_URI != '' && React.createElement(Warning, null)
      );
    }
  }]);

  return Content;
}(React.Component);

var root = ReactDOM.createRoot(document.getElementById('root'));
root.render(React.createElement(Content, null));