# sptf2tdl
A simple Python web appplication for transferring Spotify playlists to TIDAL.
It uses Flask, SQLAlchemy and Socket-IO for the backend and simple HTML, Bootstrap theme and React for the frontend. The matching algorithm will pick master quality track versions where found.

### Usage:

0. Create an `.env` file in root directory with `client_id=XYZ` and `client_secret=XYZ` values obtained from [Spotify developer portal](https://developer.spotify.com/dashboard/applications/)
1. Run the application using `docker compose up -d` and access the application in your web browser at `localhost`
2. *(First use)* After entering playlist link for the first time, you will be prompted to login to TIDAL. Please **CLICK** the link that you will be provided (don't right click and open it in a new tab) otherwise the application might not work properly. You may have to enable browser pop-ups temporarily.

### Known issues/limitations
- Spotify playlists must be **public** in order to transfer them
- the matching algorithm will sometimes mismatch tracks, specifically some classical tracks which have complicated names
- tracks which are restricted in your market (country) will not be added to the TIDAL playlist


![home](https://user-images.githubusercontent.com/38385475/207037038-4e074684-105b-41b4-98ab-2d516e880a5c.png)
![error](https://user-images.githubusercontent.com/38385475/207037032-5cfbeb60-e170-48f1-b8bd-77da43e37743.png)
![transfer](https://user-images.githubusercontent.com/38385475/207037041-7b85170a-41d2-4b02-a383-9efcd88299a3.png)
![success](https://user-images.githubusercontent.com/38385475/207037040-fc88ef55-aaad-4898-b67d-9804b78df07d.png)
