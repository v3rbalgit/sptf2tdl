import re
from typing import List, Tuple
from urllib.parse import urlsplit

# Replace foreign letters with english counterparts
def replace_letters(string: str) -> str:
  foreign_letters: str  = 'àáâãäåçèéêëìíîïðñľĺšśčćďťžźřŕňńòóôõöùúûüýÿ'
  english_letters: str  = 'aaaaaaceeeeiiiidnllssccdtzzrrnnooooouuuuyy'
  new_string: List[str] = []

  for char in string.lower():
    if char in foreign_letters:
      new_string.append(english_letters[foreign_letters.find(char)])
    else:
      new_string.append(char)

  return "".join(new_string)

# Manipulate a string for searching using its words as list
def filter_name(string: str) -> List[str]:
  return re.sub(r'[\:|\;|\,|\"|\&|\(|\)|\\]',' ', replace_letters(string)).replace(" - ", " ").split()

# Check if a link is a valid Spotify URL
def check_url(url: str) -> str:
  spotify_base = 'open.spotify.com'
  url_components = urlsplit(url)

  if not isinstance(url, str):
    raise TypeError('Link URL must be of type "string"')

  if url_components.netloc != spotify_base:
    raise TypeError(f'Not a valid Spotify URL: "{url_components.netloc!r}"', url)

  resource, resource_id = url_components.path.split('/')[1:3]           # first element is an empty string

  if not resource in ('playlist'):                # can be extended to other resources if needed
    raise TypeError(f'Not a valid Spotify URL: "{url_components.path!r}"', url)

  return resource_id