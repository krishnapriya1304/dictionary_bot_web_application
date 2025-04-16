from flask import Flask, render_template, request,session, redirect
from nltk.corpus import wordnet as wn
from gtts import gTTS
import random
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Required for using session

# Route for home page
@app.route('/')
def home():
    return render_template('project.html')

# Route for Search
def get_word_details(word):
    synsets = wn.synsets(word)
    if not synsets:
        return {"definition": "No definition found.", "synonyms": [], "antonyms": []}
    
    definition = synsets[0].definition()
    synonyms = set()
    antonyms = set()

    for syn in synsets:
        for lemma in syn.lemmas():
            synonyms.add(lemma.name())
            if lemma.antonyms():
                antonyms.add(lemma.antonyms()[0].name())

    return {
        "definition": definition,
        "synonyms": list(synonyms),
        "antonyms": list(antonyms)
    }

# --- /search route ---
@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        word = request.form['word']
        data = get_word_details(word)

    # Create pronunciation audio
        tts = gTTS(word)
        audio_path = os.path.join('static', 'audio.mp3')
        tts.save(audio_path)

        return render_template("search.html", word=word, data=data)
    return redirect('/')

@app.route('/wordoftheday', methods=['GET'])
def wordoftheday():
    # Convert to list to avoid TypeError
    random_word = random.choice(list(wn.words()))

    synsets = wn.synsets(random_word)
    if synsets:
        definition = synsets[0].definition()
    else:
        definition = "Definition not found."

    # Generate pronunciation audio
    tts = gTTS(text=random_word, lang='en')
    audio_path = os.path.join('static', 'audio.mp3')
    tts.save(audio_path)

    return render_template("wordoftheday.html", word=random_word, definition=definition)

# Spellbee
@app.route('/spellbee', methods=['GET'])
def spellbee():
    word = random.choice(list(wn.words()))  # Convert iterator to list
    session['spellbee_word'] = word.lower()
    session['attempts'] = 0

    # Create pronunciation audio
    tts = gTTS(word)
    audio_path = os.path.join('static', 'audio.mp3')
    tts.save(audio_path)

    return render_template("spellbee.html", message=None)

# --- SPELLBEE CHECK ---
@app.route('/spellbee-check', methods=['POST'])
def spellbee_check():
    guess = request.form['guess'].strip().lower()
    correct_word = session.get('spellbee_word', '')
    attempts = session.get('attempts', 0) + 1
    session['attempts'] = attempts

    if guess == correct_word:
        message = f"✅ Correct! The word was '{correct_word}'."
        session.pop('spellbee_word', None)
        session.pop('attempts', None)
    elif attempts >= 3:
        message = f"❌ You've used all attempts. The correct word was '{correct_word}'."
        session.pop('spellbee_word', None)
        session.pop('attempts', None)
    else:
        message = f"❌ Incorrect. Try again! Attempt {attempts}/3."

    return render_template("spellbee.html", message=message)


# ---------- Run ----------
if __name__ == '__main__':
    app.run(debug=True)
