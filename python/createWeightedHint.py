import sys
import json
import numpy as np
import pandas as pd
from scipy import spatial
from pathlib import Path

input = json.loads(sys.argv[1])
words = json.loads(input['words'])
minDistance = input['minCosDistance']
vectorPath = input['vectorPath']

vectorFile = Path(__file__).parent / vectorPath

embeddings = {}
with vectorFile.open() as f:
    for line in f:
        values = line.split()
        word = values[0]
        vectors = np.asarray(values[1:], "float32")
        embeddings[word] = vectors

def distance(word, reference):
    return spatial.distance.cosine(embeddings[word], embeddings[reference])

def goodness(word, answers, bad):
    return sum([distance(word, b) for b in bad]) - 4.0 * sum([distance(word, a) for a in answers])

def minimax(word, answers, bad):
    return min([distance(word, b) for b in bad]) - max([distance(word, a) for a in answers])

def candidates(answers, bad, size=1):
    best = sorted(embeddings.keys(), key=lambda w: -1 * goodness(w, answers, bad))
    res = [(str(i + 1), "{0:.2f}".format(minimax(w, answers, bad)), w) for i, w in enumerate(sorted(best[:250], key=lambda w: -1 * minimax(w, answers, bad))[:size])]
    candidates = [(c[2]) for c in res]
    return candidates[0]

blues = []
reds = []

for word in words:
    if word['color'] == 'blue':
        blues.append(word['string']);
    elif word['color'] == 'red':
        reds.append(word['string']);
    elif word['color'] == 'black':
        reds.append(word['string']);

hint = ''
ignoredWords = []
distances = {}

while hint == '' and len(blues) != 0:
    hint = candidates(blues,reds)
    for word in blues:
        dist = distance(hint, word)
        distances[word] = dist
        if dist < minDistance:
            blues.remove(word)
            hint = ''
            ignoredWords.append(word)
            break

results = json.dumps({"hint" : "null",})

results = json.dumps({
    "hint": hint,
    "count": len(blues),
    "targetWords": blues,
    "ignoredWords": ignoredWords,
    "distances": distances,
})

print(results)


sys.stdout.flush()
