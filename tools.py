import re
from typing import List

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