import asyncio, nest_asyncio, shelve, re

import spotify, tidalapi

from dotenv import load_dotenv
from os import getenv
from typing import List, Dict, Any
from itertools import chain

load_dotenv()
nest_asyncio.apply() # work-around for recurrent async functions

client_id = getenv('client_id')
client_secret = getenv('client_secret')
user_id = '' # 11124161068


def set_user_id():
  global user_id
  user_id = input('\nEnter user ID: ')

  try:
    int(user_id)
  except ValueError:
    print(" -> User ID must be a number!")
    set_user_id()


def get_playlist_number(max: str) -> int:
  playlist_number = input('\nSelect a playlist number: ')

  try:
    if (int(playlist_number) > int(max)) or (int(playlist_number) < 1):
      print(' -> Playlist number must be between 1 and ', max)
      get_playlist_number(max)
    else:
      playlist_number = int(playlist_number) - 1
      return playlist_number
  except ValueError:
    print(" -> Playlist number cannot be a string!")
    get_playlist_number(max)

# Get and set token for TIDAL API
def handle_tidal_token(session: tidalapi.Session):
  with shelve.open('tidal_login') as tidal_login:
    if 'access_token' not in tidal_login.keys():
      session.login_oauth_simple()
      tidal_login['token_type'] = session.token_type
      tidal_login['access_token'] = session.access_token
      tidal_login['refresh_token'] = session.refresh_token
      tidal_login['expiry_time'] = session.expiry_time
    else:
      # TODO: check expiry and request new access token if necessary
      session.load_oauth_session(
        token_type=tidal_login['token_type'],
        access_token=tidal_login['access_token'],
        refresh_token=tidal_login['refresh_token'],
        expiry_time=tidal_login['expiry_time'])

# Replace foreign letters with english counterparts
def replace_letters(string: str) -> str:
  foreign_letters = 'àáâãäåçèéêëìíîïðñľĺšśčćďťžźřŕňńòóôõöùúûüýÿ'
  english_letters = 'aaaaaaceeeeiiiidnllssccdtzzrrnnooooouuuuyy'
  new_string = []

  for char in string.lower():
    if char in foreign_letters:
      new_string.append(english_letters[foreign_letters.find(char)])
    else:
      new_string.append(char)

  return "".join(new_string)

# Manipulate a string for searching using its words as list
def filter_name(string: str) -> List[str]:
  return re.sub(r'[\:|\;|\,|\"|\&|\(|\)|\\]',' ', replace_letters(string)).replace(" - ", " ").split()


# Track comparison algorithm
def compare_tracks(tracks: List[tidalapi.Track], track_name: str, artists: List[str], album_name: str, track_duration: int) -> None | tidalapi.Track:
  selected_tracks = []

  # Filter every track in search results by common track name words and artist name words
  for track in tracks:
    common_names = list(set(filter_name(track.name)) & set(filter_name(track_name)))
    if common_names:
      common_artists = list(set(chain.from_iterable(filter_name(artist.name) for artist in track.artists)) & set(chain.from_iterable(filter_name(a) for a in artists)))
      if common_artists:
        selected_tracks.append({
          'track': track,
          'common_names': common_names,
          'common_artists': common_artists,
          'common_album': list(set(filter_name(track.album.name)) & set(filter_name(album_name))),
          'duration_score': 1 - (abs(track_duration - (track.duration * 1000)) / track_duration)
        })

  if len(selected_tracks) == 0:
    return None

  # Further filtering
  for key in ['common_names', 'common_artists', 'common_album']:
    selected_tracks.sort(key=lambda x: len(x[key]), reverse=True)
    selected_tracks = list(filter(lambda x: len(x[key]) == len(selected_tracks[0][key]), selected_tracks))
  selected_tracks.sort(key=lambda x: x['duration_score'], reverse=True)

  # Prefer master quality tracks
  master_tracks = list(filter(lambda x: x['track'].audio_quality == tidalapi.Quality.master, selected_tracks))

  return master_tracks[0]['track'] if master_tracks else selected_tracks[0]['track']

# Filter relevant data from Spotify to use for searching on TIDAL
def filter_track_data(tracks: List[spotify.Track]) -> List[Dict[str, Any]]:
  return [{
      'name': track['track']['name'],
      'artists': [artist['name'] for artist in track['track']['artists']],
      'album': track['track']['album']['name'],
      'length': track['track']['duration_ms'],
      'isrc': track['track']['external_ids']['isrc']
    } for track in tracks]


def tidal_crosscheck(tracks: List[Dict[str, Any]], playlist: spotify.Playlist) -> None:
  session = tidalapi.Session()

  handle_tidal_token(session)

  user = session.user
  playlists = user.playlists()

  found_playlist = tuple(filter(lambda pl: pl.name == playlist.name, playlists))

  if found_playlist:
    overwrite_playlist = input(f' -> Playlist "{playlist.name}" already exists! Do you want to overwrite it? (Y/N): ').lower()
    if overwrite_playlist in ('y','yes'):
      found_playlist[0].delete()
      tidal_crosscheck(tracks, playlist)
    elif overwrite_playlist in ('n','no'):
      choose_another_playlist = input('\nDo you want to choose another playlist? (Y/N): ').lower()
      if choose_another_playlist in ('y', 'yes'):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(main())
      elif choose_another_playlist in ('n', 'no'):
        print('\nThanks for using this program!')
      else:
        print('-> No valid answer provided, quitting...')
    else:
      print('-> No valid answer provided, quitting...')
  else:
    print(f'\nPorting playlist "{playlist.name}"...')

    new_playlist = user.create_playlist(playlist.name, playlist.description)
    tracks_not_found = []

    for i, track in enumerate(tracks):
      track_name = track['name']
      artists = [str(artist) for artist in track["artists"]]
      album = track['album']
      track_duration = track["length"]
      length = f'{int((track_duration/1000)/60)}:{str(int((track_duration/1000)%60)).zfill(2)}'

      print(f' [{i + 1}/{len(tracks)}]: "{track_name}" by {", ".join(artists)} ({length}) ', end='')

      tracks_found = []
      artist_list = list(chain.from_iterable(filter_name(artist) for artist in artists))
      whole_phrase = filter_name(track_name) + artist_list

      # Use words in track's and artists' names to search
      for i, word in enumerate(whole_phrase):
        if i == 0: continue   # skip using just one word (too vague)

        search_result = session.search(" ".join(whole_phrase[:i+1]), models=[tidalapi.media.Track], limit=4 + len(whole_phrase) - i)
        isrc_found = tuple(filter(lambda tr: tr.isrc == track['isrc'], search_result['tracks']))

        # Check for exact match
        if isrc_found:
          # Prefer master quality tracks
          master_tracks = list(filter(lambda x: x.audio_quality == tidalapi.Quality.master, isrc_found))
          new_playlist.add([master_tracks[0].id if master_tracks else isrc_found[0].id])            # found by isrc => 1:1 match
          print('•')
          break
        else:
          # Fill list with all search results
          tracks_found.extend(search_result['tracks'])

          # When we're on the last word and no exact match was found, use the comparison algorithm
          if len(whole_phrase) - 1 == i:
            found_track = compare_tracks(tracks_found, track_name, artists, album, track_duration)

            if found_track:
              new_playlist.add([found_track.id])          # found by similar name and artists
              print('•')
            else:
              tracks_not_found.append(track)              # found nothing (extremely rare)
              print('×')


    # Display problems during porting
    if tracks_not_found:
      print(f'\nCould not find following tracks on TIDAL:')
      for track in tracks_not_found:
        print(f' -> "{track["name"]}" by {", ".join([str(art) for art in track["artists"]])}')

    print(f'\nSuccessfully ported {len(tracks) - len(tracks_not_found)} out of {len(tracks)} tracks in the "{playlist.name}" playlist!')


async def select_playlist(client: spotify.Client, playlists: List[spotify.Playlist]):
  # Print a list of owner's public playlists
  for i, playlist in enumerate(playlists):
    print(f' {i + 1}: {playlist.name}')

  # Let user choose a playlist to port
  playlist_number = get_playlist_number(len(playlists))
  selected_playlist = playlists[playlist_number]

  # Get and filter playlist tracks data
  playlist_tracks = await client.http.get_playlist_tracks(selected_playlist.id, limit=100)
  tracks = playlist_tracks['items']

  if len(tracks) == 0:
    another_playlist = input(f' -> Playlist "{selected_playlist.name}" is empty! Choose another playlist? (Y/N): ').lower()
    if another_playlist in ('y','yes'):
      print()
      await select_playlist(client, playlists)
    elif another_playlist in ('n','no'):
      print('\nThanks for using this program!')
    else:
      print('-> No valid answer provided, quitting...')
  elif len(tracks) == 100:
    offset_accum = len(tracks)
    while offset_accum == len(tracks):
      more_playlist_tracks = await client.http.get_playlist_tracks(selected_playlist.id, offset=offset_accum, limit=100)
      tracks.extend(more_playlist_tracks['items'])
      offset_accum += 100
    tidal_crosscheck(filter_track_data(tracks), selected_playlist)
  else:
    tidal_crosscheck(filter_track_data(tracks), selected_playlist)

#################
# MAIN FUNCTION #
#################
async def main():
  async with spotify.Client(client_id, client_secret) as client:
    global user_id
    user = await client.get_user(user_id)
    playlists = await user.get_all_playlists()

    # Filter playlists based on owner
    playlists = list(filter(lambda x: x.owner == user, playlists))

    if len(playlists) == 0:
      another_id = input(f' -> There are no public playlists by user {user.display_name} ({user_id}). Choose another user ID? (Y/N): ').lower()
      if another_id in ('y','yes'):
        set_user_id()
        loop = asyncio.get_event_loop()
        loop.run_until_complete(main())
      elif another_id in ('n','no'):
        print('\nThanks for using this program!')
      else:
        print('-> No valid answer provided, quitting...')
    else:
      print(f'\nPublic Spotify playlists by {user.display_name} (ID: {user_id}):')
      await select_playlist(client, playlists)


if __name__ == '__main__':
  print('Port your SPOTIFY playlists to TIDAL!'.upper())
  print('-------------------------------------')
  print("""
  README: This program will try to find exact matches of tracks from a selected playlist on Spotify and make a new playlist with matches found on TIDAL in the same order.
If it doesn't find any exact matches, it will try to look for closest ones based on track name, artist names, album name and track duration.
Any market restricted tracks will not appear on the resulting TIDAL playlist.
""")

  # Ask user to provide a user id to start
  set_user_id()

  asyncio.run(main())

# KNOWN ISSUES:
# - will not add market restricted tracks to playlist