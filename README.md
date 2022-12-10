# sptf2tdl
A simple Python web appplication for porting Spotify playlists to TIDAL. 
It uses Flask, SQLAlchemy and Socket-IO for the backend and simple HTML, Bootstrap theme and jQuery for the frontend. The matching algorithm will pick master quality track versions where found.

### Usage:
0. Create `.env` file in root directory with `client_id="???"` and `client_secret="???"` values obtained via [Spotify developer portal](https://developer.spotify.com/dashboard/applications)
1. Install the requirements using `pip install -r "requirements.txt` ideally in a separate virtual environment
2. Use `flask run server.py` to start the server
3. Go to `localhost:5000` or `127.0.0.1:5000` in your web browser to use the application
4. *(First use)* After entering playlist link for the first time, you will be prompted to login to TIDAL. Please **CLICK** the link that you will be provided (don't right click and open it in a new tab) otherwise the application might not work properly

### Known issues
- does not catch errors with TIDAL login
- the matching algorithm can sometimes mismatch tracks, specifically some classical tracks which have complicated names
- will not add songs to playlist that are restricted in your market (country) - this can't be resolved
