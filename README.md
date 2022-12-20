# sptf2tdl
A simple Python web appplication for transferring Spotify playlists to TIDAL.
It uses Flask, SQLAlchemy and Socket-IO for the backend and simple HTML, Bootstrap theme and React for the frontend. The matching algorithm will pick master quality track versions where found.

### Usage:
0. Create `.env` file in root directory with `client_id="???"` and `client_secret="???"` values obtained via [Spotify developer portal](https://developer.spotify.com/dashboard/applications)

**Option 1:**
1. Install the requirements using `pip install -r "requirements.txt` (ideally in a separate virtual environment)
2. Use `flask run server.py` to start the server
3. Go to `localhost:5000` or `127.0.0.1:5000` in your web browser to use the application
4. *(First use)* After entering playlist link for the first time, you will be prompted to login to TIDAL. Please **CLICK** the link that you will be provided (don't right click and open it in a new tab) otherwise the application might not work properly

**Option 2:**
1. Use the provided *Dockerfile* to run the app in your Docker

### Known issues/limitations
- Spotify playlists must be **public** in order to transfer them
- the matching algorithm will sometimes mismatch tracks, specifically some classical tracks which have complicated names
- tracks which are restricted in your market (country) will not be added to the TIDAL playlist
- *(NOTE)* node.js is used only for Babel conversion of React JSX in the static/src directory

![home](https://user-images.githubusercontent.com/38385475/207037038-4e074684-105b-41b4-98ab-2d516e880a5c.png)
![error](https://user-images.githubusercontent.com/38385475/207037032-5cfbeb60-e170-48f1-b8bd-77da43e37743.png)
![transfer](https://user-images.githubusercontent.com/38385475/207037041-7b85170a-41d2-4b02-a383-9efcd88299a3.png)
![success](https://user-images.githubusercontent.com/38385475/207037040-fc88ef55-aaad-4898-b67d-9804b78df07d.png)
