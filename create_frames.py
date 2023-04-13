import itertools

def calculate_amount(word):
  summ = 0
  for i in word:
    summ += len(i)
  return summ

def distribute_frames_word(amount, letters):
  if '-' in letters:
    arr = [['-']*amount]
  else:
    arr = []
    for i in letters:
      arr.append([i])
    while calculate_amount(arr) < amount:
      for i in range(len(arr)):
        if calculate_amount(arr) < amount:
          letter = arr[i][0]
          arr[i].append(letter)
        else:
          break
  res = list(itertools.chain.from_iterable(arr))
  return res