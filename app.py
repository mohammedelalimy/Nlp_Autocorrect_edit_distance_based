from flask import Flask, request, jsonify, render_template
import re
from collections import Counter

app = Flask(__name__)


def processData(fileName):
    words = []
    with open(fileName) as f:
        fileNameData = f.read()
    fileNameData = fileNameData.lower()
    words = re.findall(r'\w+', fileNameData)
    return words


wordList = processData("text_data.txt")
vocabulary = set(wordList)


def getCount(wordList):
    wordCountDictionary = {}
    wordCountDictionary = Counter(wordList)
    return wordCountDictionary


wordCountDictionary = getCount(wordList)


def deleteLetter(word):
    deleteList = []
    splitList = []
    for i in range(len(word)):
        splitList.append([word[:i], word[i:]])
    for a, b in splitList:
        deleteList.append(a + b[1:])
    return deleteList


def replaceLetter(word):
    letter = 'abcdefghijklmnopqrstuvwxyz'
    replaceList = []
    splitList = []
    for c in range(len(word)):
        splitList.append((word[0:c], word[c:]))
    replaceList = [a + l + (b[1:] if len(b) > 1 else '') for a, b in splitList if b for l in letter]
    replaceSet = set(replaceList)
    replaceSet.remove(word)
    return replaceList


def insertLetter(word):
    letter = 'abcdefghijklmnopqrstuvwxyz'
    insertList = []
    splitList = []
    for c in range(len(word) + 1):
        splitList.append((word[0:c], word[c:]))
    insertList = [a + l + b for a, b in splitList for l in letter]
    return insertList


def getProbablity(wordCountDictionary):
    probablities = {}
    m = sum(wordCountDictionary.values())
    for key in wordCountDictionary:
        probablities[key] = wordCountDictionary[key] / m
    return probablities


probablity = getProbablity(wordCountDictionary)


def switchLetter(word):
    splitList = []
    switchL = []
    for i in range(len(word)):
        splitList.append((word[0:i], word[i:]))
    switchL = [a + b[1] + b[0] + b[2:] for a, b in splitList if len(b) >= 2]
    return switchL


def editOneLetter(word, allowSwitches=True):
    editOneSet = set()
    editOneSet.update(deleteLetter(word))
    if allowSwitches:
        editOneSet.update(switchLetter(word))

    editOneSet.update(replaceLetter(word))
    editOneSet.update(insertLetter(word))

    return editOneSet


def editTwoLetters(word, allowSwitches=True):
    editTwoSet = set()
    editOne = editOneLetter(word, allowSwitches=allowSwitches)
    for w in editOne:
        if w:
            editTwo = editOneLetter(w, allowSwitches=allowSwitches)
            editTwoSet.update(editTwo)
    return editTwoSet


def getCorrections(word, probablity, vocabulary):
    suggestion = []
    n_best = []
    suggestions = list((word in vocabulary and word) or editOneLetter(word).intersection(vocabulary) or editTwoLetters(
        word).intersection(vocabulary))
    n_best = [[s, probablity[s]] for s in list(reversed(suggestions))]
    return n_best


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/correct', methods=['GET'])
def correct_word():
    myWord = request.args.get('word')
    if not myWord:
        return jsonify({"error": "Please provide a word."}), 400

    temporaryCorrections = getCorrections(myWord, probablity, vocabulary)
    temporaryCorrections.sort(key=lambda x: x[1], reverse=True)

    response = [{"word": word, "probability": probability} for word, probability in temporaryCorrections]
    return jsonify(response)


if __name__ == '__main__':
    app.run(debug=True)
