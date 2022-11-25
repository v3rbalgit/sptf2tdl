import asyncio, nest_asyncio, shelve, re, pprint

import spotify, tidalapi

from dotenv import load_dotenv
from os import getenv
from difflib import SequenceMatcher
from typing import List, Dict, Any
from time import sleep
from collections import OrderedDict
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

# Manipulate a string for searching using its words
def filter_name(string: str) -> List[str]:
  return re.sub(r'[\:|\;|\,|\&|\(|\)|\\]',' ', replace_letters(string)).replace(" - ", " ").split()


# Track comparison algorithm
def compare_tracks(tracks: List[tidalapi.Track], track_name: str, artists: List[str], album_name: str) -> None | tidalapi.Track:
  track_scores = {}
  selected_tracks = []

  # Filter every track in search results by common track name words and artist name words
  for track in tracks:
    common_name = list(set(track.name.split()) & set(track_name.split()))
    if len(common_name) != 0:
      common_artists = list(set(chain.from_iterable([artist.name.split() for artist in track.artists])) & set(chain.from_iterable([a.split() for a in artists])))
      if len(common_artists) != 0:
        selected_tracks.append(track)

  # If there are no tracks after filtering, the searched track does not exist on TIDAL
  if len(selected_tracks) == 0:
    return None

  # Order tracks by similarity(taking album name, artists' names and track name into consideration) and return closest match
  for track in selected_tracks:
    key = SequenceMatcher(None, filter_name(track.name), filter_name(track_name)).ratio()
    key += SequenceMatcher(None, [" ".join(filter_name(a.name)) for a in track.artists], [" ".join(filter_name(a)) for a in artists]).ratio()
    key += SequenceMatcher(None, filter_name(track.album.name), filter_name(album_name)).ratio()
    track_scores[key/3] = track

  ordered_tracks = OrderedDict(sorted(track_scores.items(), reverse=True))
  return list(ordered_tracks.values())[0]


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

  if len(found_playlist) != 0:
    overwrite_playlist = input(f' -> Playlist "{playlist.name}" already exists! Do you want to overwrite it? (Y/N): ').lower()
    if overwrite_playlist in ('y','yes'):
      found_playlist[0].delete()
      sleep(1)  # Allow extra time for playlist to get deleted from TIDAL
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
      length = f'{int((track["length"]/1000)/60)}:{str(int((track["length"]/1000)%60)).zfill(2)}'
      album = track['album']

      print(f' [{i + 1}/{len(tracks)}]: "{track_name}" by {", ".join(artists)} ({length}) ', end='')

      tracks_found = []
      whole_phrase = filter_name(track_name) + list(chain.from_iterable(filter_name(artist) for artist in artists))

      # Use words in track's and artists' names to search
      for i, word in enumerate(whole_phrase):
        if i == 0: continue   # skip using just one word (too vague)
        search_result = session.search(" ".join(whole_phrase[:i+1]), models=[tidalapi.media.Track], limit=i * 5)
        isrc_found = tuple(filter(lambda tr: tr.isrc == track['isrc'], search_result['tracks']))

        # Check for exact match
        if len(isrc_found) != 0:
          new_playlist.add([isrc_found[0].id])          # found by isrc => 1:1 match
          print('•')
          break
        else:
          # Fill list with all search results
          tracks_found.extend(search_result['tracks'])

          # When we're on the last word and no exact match was found, use the comparison algorithm
          if word == whole_phrase[-1]:
            found_track = compare_tracks(tracks_found, track_name, artists, album)

            if found_track:
              new_playlist.add([found_track.id])          # found by similar name and artists
              print('•')
              break
            else:
              tracks_not_found.append(track)              # found nothing (extremely rare)
              print('×')


    # Display problems during porting
    if len(tracks_not_found) != 0:
      print(f'\nCould not find following tracks on TIDAL:')
      for track in tracks_not_found:
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
async def main():
  async with spotify.Client(client_id, client_secret) as client:
    global user_id
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
        set_user_id()
        loop = asyncio.get_event_loop()
        loop.run_until_complete(main())
      elif another_id in ('n','no'):
        print('\nThanks for using this program!')
      else:
        print('-> No valid answer provided, quitting...')
    else:
      print(f'\nPublic Spotify playlists by {user.display_name} (ID: {user_id}):')
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
  set_user_id()

  asyncio.run(main())

# KNOWN ISSUES:
# - won't add duplicates into playlist (by isrc)
# - the search query can probably be optimized for better accuracy