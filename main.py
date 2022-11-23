import asyncio, shelve, re

import spotify, tidalapi

from dotenv import load_dotenv
from os import getenv
from difflib import SequenceMatcher
from typing import List, Dict, Any

load_dotenv()

client_id = getenv('client_id')
client_secret = getenv('client_secret')
# user_id = '11124161068' # Boris Vereš
tidal_user = getenv('tidal_user')
tidal_pass = getenv('tidal_pass')


def get_user_id() -> str:
  user_id = input('\nEnter user ID: ')

  try:
    int(user_id)
    return user_id
  except ValueError:
    print(" -> User ID must be a number!")
    get_user_id()


def get_playlist_number(max: int) -> int:
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


FilteredTrackData = Dict[str, Any]
def filter_track_data(tracks: List[spotify.Track]) -> List[FilteredTrackData]:
  return [{
      'name': track['track']['name'],
      'artists': [artist['name'] for artist in track['track']['artists']],
      # 'album': track['track']['album']['name'],
      'length': track['track']['duration_ms'],
      'isrc': track['track']['external_ids']['isrc']
    } for track in tracks]


def tidal_crosscheck(tracks: List[FilteredTrackData], playlist: spotify.Playlist) -> None:
  session = tidalapi.Session()

  handle_tidal_token(session)

  user = session.user
  playlists = user.playlists()

  found_playlist = tuple(filter(lambda pl: pl.name == playlist.name, playlists))

  if len(found_playlist) != 0:
    print(f' -> Playlist "{playlist.name}" already exists!')
    # TODO: repeat playlist selection or update playlist
  else:
    print(f'\nPorting playlist "{playlist.name}"...')

    new_playlist = user.create_playlist(playlist.name, playlist.description)
    tracks_not_found = []
    tracks_to_check = []

    for i, track in enumerate(tracks):
      artists = [str(artist) for artist in track["artists"]]
      length_formatted = f'{int((track["length"]/1000)/60)}:{str(int((track["length"]/1000)%60)).zfill(2)}'
      filtered_name = re.sub(r'\((.*?)\)', '', track["name"]).strip().lower()  # remove everything in brackets (including)
      search_query = f'{filtered_name}' if len(filtered_name.split()) > 5 else f'{filtered_name} {artists[0]}' # for shorter track names use first artist name as well

      print(f' [{i + 1}/{len(tracks)}]: "{track["name"]}" by {", ".join(artists)} ({length_formatted}) ', end='')

      tracks_found = session.search(search_query, models=[tidalapi.media.Track], limit=100)
      track_isrc_found = tuple(filter(lambda tr: tr.isrc == track['isrc'], tracks_found['tracks']))
      track_name_found = list(filter(lambda tr: SequenceMatcher(None, tr.name.lower(), track['name'].lower()).ratio() > 0.6 and SequenceMatcher(None, [a.name for a in tr.artists], artists).ratio() > 0.4, tracks_found['tracks']))
      # track_name_found = sorted(track_name_found, key=lambda tr: (SequenceMatcher(None, tr.name.lower(), track['name'].lower()).ratio() + SequenceMatcher(None, [a.name for a in tr.artists], artists).ratio()) / 2, reverse=True)

      if len(track_isrc_found) != 0:
        new_playlist.add([track_isrc_found[0].id])        # found by isrc => 1:1 match
        print('•')
      elif len(track_name_found) != 0:
        new_playlist.add([track_name_found[0].id])        # found by similar track name and artists
        print('¡')
      elif len(tracks_found['tracks']) != 0:
        new_playlist.add([tracks_found['tracks'][0].id])  # first track that was found based on search query (might not be correct)
        tracks_to_check.append(track)
        print('¿')
      else:
        tracks_not_found.append(track)                    # found nothing
        print('×')

    # Display problems during porting
    if len(tracks_not_found) != 0:
      print(f'\nCould not find following tracks on TIDAL:')
      for track in tracks_not_found:
        print(f' -> "{track["name"]}" by {", ".join([str(art) for art in track["artists"]])}')

    if len(tracks_to_check) != 0:
      print(f'\nFollowing tracks might not have been ported correctly:')
      for track in tracks_to_check:
        print(f' -> "{track["name"]}" by {", ".join([str(art) for art in track["artists"]])}')

    print(f'\nSuccessfully ported {len(tracks) - len(tracks_not_found)} out of {len(tracks)} tracks in the "{playlist.name}" playlist!')


async def select_playlist(client: spotify.Client, playlists: List[spotify.Playlist]):
  # Print a list of owner's public playlists
  for i, item in enumerate(playlists.items()):
    print(f' {i + 1}: {item[0]}')

  # Let user choose a playlist to port
  playlist_number = get_playlist_number(len(list(playlists.keys())))
  selected_playlist = list(playlists.values())[playlist_number]

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
async def main(user_id: str):
  async with spotify.Client(client_id, client_secret) as client:
    user = await client.get_user(user_id)
    playlists = await user.get_all_playlists()

    # Filter playlists based on owner
    playlists_to_select = {}
    for playlist in playlists:
      if playlist.owner == user:
        playlists_to_select[playlist.name] = playlist

    if len(list(playlists_to_select.keys())) == 0:
      another_id = input(f' -> There are no public playlists by user {user.display_name} ({user_id}). Choose another user ID? (Y/N): ').lower()
      if another_id in ('y','yes'):
        user_id = get_user_id()
        asyncio.run(main(user_id))
      elif another_id in ('n','no'):
        print('\nThanks for using this program!')
      else:
        print('-> No valid answer provided, quitting...')
    else:
      print(f'\nPublic playlists by {user.display_name} (ID: {user_id}):')
      await select_playlist(client, playlists_to_select)


if __name__ == '__main__':
  print('Port your SPOTIFY playlists to TIDAL!'.upper())
  print('-------------------------------------')
  print("""README: This program will try to find exact matches of tracks from a selected playlist on Spotify and make a new playlist with matches found on TIDAL in the same order.
If it doesn't find any exact matches, it will try to look for closest ones based on track name and artist.
Otherwise it will grab the first one it finds. This can include unintended matches. You will get notified which matches might be bad after the process finishes.
Due to simple nature of the cross-referencing algorithm, the program may omit some matches even if they are on TIDAL. You will be notified about these cases after the process finishes.
The program does not port duplicates. If resulting TIDAL playlist is shorter than the original one on Spotify, it is due to the original playlist containing duplicates.""")

  # Ask user to provide a user id to start
  user_id = get_user_id()

  asyncio.run(main(user_id))

# KNOWN ISSUES:
# - won't add duplicates into playlist (by isrc)