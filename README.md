# sptf2tdl
A simple script to port Spotify playlists to TIDAL. It saves a lot of time especially for larger playlists. It is not perfect, but it works well for 95% of songs.


### How to run

1. In order to run the program you will need to create an **.env** file with `client_id="XYZ"` and `client_secret="XYZ"` values in order to access the Spotify API. You can generate these via the [Spotify developer portal](https://developer.spotify.com/dashboard/applications)  
2. After you run the program for the first time, you will be asked to login to TIDAL with the link provided.  
3. You will be asked to input a Spotify User ID (an 11-digit number) which you can find in your Spotify account. 

### Quirks and known issues
 - this program will try to find exact matches of tracks from a selected playlist on Spotify and make a new playlist with matches found on TIDAL in the same order.  
 - if it doesn't find any exact matches, it will try to look for closest ones based on track name and artist. Otherwise it will grab the first one it finds. This can include unintended matches. You will get notified which matches might be bad after the process finishes.  
 - due to simple nature of the cross-referencing algorithm, the program may omit some matches even if they are on TIDAL. You will be notified about these cases after the process finishes.  
 - the program does not port duplicates. If resulting TIDAL playlist is shorter than the original one on Spotify, it is due to the original playlist containing duplicates.  

If you would like to improve the cross-referencing algorithm to produce more accurate search results on TIDAL, please have a look at the code.
