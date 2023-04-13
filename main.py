import sys
from api_communication import *
import math
import requests
from api_secrets import API_KEY_DICTIONARY, APP_ID_DICT
import itertools
import imageio
from create_frames import distribute_frames_word

filename = sys.argv[1]
symbols = "aäɑɒæbḇβcčɔɕçdḏḍðeəɚɛɝfgḡhʰḥḫẖiɪỉɨjʲǰkḳḵlḷɬɫmnŋṇɲɴoŏɸθpp̅þqrɹɾʀʁṛsšśṣʃtṭṯʨtʂuʊŭüvʌɣwʍxχyʸʎzẓžʒ’‘ʔʕ"
sym_let = {
  'ɒɔo' : 'o',
  'uʊŭüɨŏo͝o': 'u',
  'aäɑɒæʌ': 'a',
  'eəɛɝ': 'e',
  'ɪi': 'ee',
  'f' : 'f',
  'ðθ': 'th',
  'ʃ': 'sh',
  'z': 'z',
  'm': 'm',
  'nŋṇɲɴ': 'n',
  'tṭṯʨt': 't',
  'l': 'l',
  'd': 'd',
  'kḳḵ': 'k',
  'jʒ': 'j',
  'pp̅þ': 'p',
  'sšśṣ': 's',
  'rɹɾʀʁṛ': 'r',
  'gḡɚ': 'g',
  'hʰḥḫẖ': 'h',
  'bḇβ': 'b',
  'w': 'w',
  'v': 'v',
}

# dictionary API
app_key = API_KEY_DICTIONARY
app_id = APP_ID_DICT
dict_endpoint = "https://od-api.oxforddictionaries.com/api/v2/entries/"
sec_dict_endpoint = "https://api.dictionaryapi.dev/api/v2/entries/en/"

audio_url = upload(filename)
words_duration, words_pauses = save_transcript(audio_url, filename)
# words_duration = {1: ['Often', 250], 2: ['times', 537], 3: ["I'll", 302], 4: ['pull', 235], 5: ['down', 252], 6: ['all', 162], 7: ['the', 132], 8: ['shades', 377], 9: ['like', 160], 10: ['I', 132], 11: ['used', 177], 12: ['to.', 95]}
words = {}

for i in range(1, len(words_duration) + 1):
  language = "en-gb"
  # calculate number of frames for each word
  frames_per_word = math.ceil((words_duration[i][1] / 1000) * 24)
  word_id = words_duration[i][0].replace(".", "")
  url = dict_endpoint + language + "/" + word_id.lower()
  phonetic_response = requests.get(url, headers={'app_id': app_id, 'app_key': app_key})
  try:
    phonetic = phonetic_response.json()["results"][0]["lexicalEntries"][0]["entries"][0]["pronunciations"][0]["phoneticSpelling"]
  except Exception:
    try:
      phonetic_response = requests.get(sec_dict_endpoint + word_id)
      phonetic = phonetic_response.json()[0]["phonetic"]
      if phonetic == "":
        language = "en-us"
        url = dict_endpoint + language + "/" + word_id.lower()
        phonetic_response = requests.get(url, headers={'app_id': app_id, 'app_key': app_key})
        phonetic = phonetic_response.json()["results"][0]["lexicalEntries"][0]["entries"][0]["pronunciations"][0]["phoneticSpelling"]
    except Exception:
      language = "en-us"
      url = dict_endpoint + language + "/" + word_id.lower()
      phonetic_response = requests.get(url, headers={'app_id': app_id, 'app_key': app_key})
      phonetic = phonetic_response.json()["results"][0]["lexicalEntries"][0]["entries"][0]["pronunciations"][0]["phoneticSpelling"]
      if phonetic == "":
        phonetic = "NOT_FOUND"

  res = ""
  for smb in phonetic:
    if smb in symbols:
      res += smb
  words[i] = [frames_per_word, res]


print("Phonetic retrieved 🗣")

final_words = {}
k = 1

for word_key in words.keys():
  word = words[word_key][1]
  add_word = []
  for symbol in word:
    # go through each symbol
    for sym in sym_let:
      # if symbol in a key of dict
      if symbol in sym:
        add_word.append(sym_let[sym])
        break
  final_words[word_key] = [words[word_key][0], add_word]

final_frames = {}

for i in range(1, len(words_duration)*2 + 1):
  if i % 2 == 0:
    final_frames[i] = final_words[i/2]
  else:
    final_frames[i] = [math.ceil((words_pauses[math.ceil(i/2)]/1000)*24), "-"]

list_result = []
for frame in final_frames:
  amount, letters = final_frames[frame][0], final_frames[frame][1]
  list_result.append(distribute_frames_word(amount, letters))

result = list(itertools.chain.from_iterable(list_result))

print("Frame letters prepared 🎞")

# create gif
with imageio.get_writer('animation.gif', mode='I', duration=1/24) as writer:
  for frame_l in result:
    image = imageio.imread('letters_frames/' + frame_l + '.png')
    writer.append_data(image)

print("All done! GIF created (animation.gif) 🎬")