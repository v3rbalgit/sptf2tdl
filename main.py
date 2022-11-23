import asyncio, shelve, re

import spotify, tidalapi

from dotenv import load_dotenv
from os import getenv
from difflib import SequenceMatcher

load_dotenv()

client_id = getenv('client_id')
client_secret = getenv('client_secret')
# user_id = '11124161068' # Boris Vereš
tidal_user = getenv('tidal_user')
tidal_pass = getenv('tidal_pass')


def get_user_id() -> int:
  user_id = input('\nEnter user ID: ')

  try:
    int(user_id)
    return user_id
  except ValueError:
    print(" -> User ID must be a number!")
    get_user_id()


def get_playlist_number(max) -> int:
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


def handle_tidal_token(session):
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

def tidal_crosscheck(tracks, playlist) -> None:
  session = tidalapi.Session()

  handle_tidal_token(session)

  user = session.user
  playlists = user.playlists()

  found_playlist = tuple(filter(lambda pl: pl.name == playlist.name, playlists))

  if len(found_playlist) != 0:
    print(f' -> Playlist "{playlist.name}" already exists!')
    # TODO: repeat playlist selection or update playlist
  else:
    new_playlist = user.create_playlist(playlist.name, playlist.description)
    tracks_not_found = []

    for i, track in enumerate(tracks):
      artists = [str(artist) for artist in track["artists"]]
      length_formatted = f'{int((track["length"]/1000)/60)}:{str(int((track["length"]/1000)%60)).zfill(2)}'
      filtered_name = re.sub(r'\((.*?)\)', '', track["name"]).strip().lower()  # remove everything in brackets including
      search_query = f'{filtered_name}' if len(filtered_name.split()) > 4 else f'{filtered_name} {artists[0]}' # for shorter track names use first artist name as well

      print(f' [{i + 1}/{len(tracks)}]: "{track["name"]}" by {", ".join(artists)} ({length_formatted}) ', end='')

      tracks_found = session.search(search_query, models=[tidalapi.media.Track], limit=100)
      track_isrc_found = list(filter(lambda tr: tr.isrc == track['isrc'], tracks_found['tracks']))
      track_name_found = list(filter(lambda tr: SequenceMatcher(None, tr.name.lower(), track['name'].lower()).ratio() > 0.5 and SequenceMatcher(None, [a.name for a in tr.artists], artists).ratio() > 0.5, tracks_found['tracks']))

      if len(track_isrc_found) != 0:
        new_playlist.add([track_isrc_found[0].id])        # found by isrc
        print('•')
      elif len(track_name_found) != 0:
        new_playlist.add([track_name_found[0].id])        # found by similar track name and artists
        print('¡')
      elif len(tracks_found['tracks']) != 0:
        new_playlist.add([tracks_found['tracks'][0].id])  # found first thing
        print('¿')
      else:
        tracks_not_found.append(track)                    # found nothing
        print('×')

    print()
    if len(tracks_not_found) != 0:
      print(f'Could not find following tracks on TIDAL:')

      for track in tracks_not_found:
        print(f' -> "{track["name"]}" by {", ".join([str(art) for art in track["artists"]])}')

    print(f'Successfully ported {len(tracks) - len(tracks_not_found)} out of {len(tracks)} tracks in the "{playlist.name}" playlist!')



async def main(user_id) -> None:
  async with spotify.Client(client_id,client_secret) as client:
    user = await client.get_user(user_id)
    playlists = await user.get_all_playlists()

    if len(playlists) == 0:
      print(' -> There are no public playlists for user ID ', user_id)
    else:
      print(f'\nPublic playlists by {user.display_name} (ID: {user_id}):')

      # Filter playlists based on owner
      playlists_to_select = {}
      for playlist in playlists:
        if playlist.owner == user:
          playlists_to_select[playlist.name] = playlist

      # Print a list of owner's public playlists
      for i, item in enumerate(playlists_to_select.items()):
        print(f' {i + 1}: {item[0]}')

      # Let user choose a playlist to port
      playlist_number = get_playlist_number(len(list(playlists_to_select.keys())))
      selected_playlist = list(playlists_to_select.values())[playlist_number]

      # Get and filter playlist tracks data
      # TODO: pagination above 100 responses
      playlist_tracks = await client.http.get_playlist_tracks(selected_playlist.id, limit=100)
      tracks = playlist_tracks['items']
      filtered_tracks_data = [{
        'name': track['track']['name'],
        'artists': [artist['name'] for artist in track['track']['artists']],
        # 'album': track['track']['album']['name'],
        'length': track['track']['duration_ms'],
        'isrc': track['track']['external_ids']['isrc']
      } for track in tracks]

      print(f'\nPorting playlist "{selected_playlist.name}"...')
      tidal_crosscheck(filtered_tracks_data, selected_playlist)

if __name__ == '__main__':
  print('Port your SPOTIFY playlists to TIDAL!')

  # Ask user to provide a user id to start
  user_id = get_user_id()

  asyncio.run(main(user_id))

# KNOWN ISSUES:
# - won't add the same song twice into playlist (isrc)