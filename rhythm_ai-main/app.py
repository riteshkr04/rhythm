from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
import cv2
import numpy as np
from fer import FER
import random
import sqlite3
from datetime import datetime

app = Flask(__name__)
CORS(app)
detector = FER()


def init_db():
    conn = sqlite3.connect('emotion_history.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS emotions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            detected_emotion TEXT NOT NULL,
            song_recommendation TEXT,
            timestamp DATETIME DEFAULT (datetime('now','localtime'))
        )
    ''')
    conn.commit()
    conn.close()


init_db()

# Function to save emotion and song to the database
def save_emotion_to_db(emotion, song):
    conn = sqlite3.connect('emotion_history.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO emotions (detected_emotion, song_recommendation) VALUES (?, ?)', (emotion, song))
    conn.commit()
    conn.close()

@app.route('/')

def index():
    return render_template('index.html')


@app.route('/predict', methods=['POST'])
def predict():
    frame = request.files['image']
    frame = cv2.imdecode(np.frombuffer(frame.read(), np.uint8), cv2.IMREAD_COLOR)

    # Check if the user has selected an emotion
    user_emotion = request.form.get('emotion')

    # Use the FER detector to analyze emotions in the frame
    emotions = detector.detect_emotions(frame)

    # Extract the dominant emotion
    if emotions:
        dominant_emotion = max(emotions[0]['emotions'], key=emotions[0]['emotions'].get)
    else:
        dominant_emotion = "Neutral"

    if user_emotion:
        dominant_emotion = user_emotion

    # Expanded song recommendations with actual URLs
    song_recommendations = {
        "happy": [
            {"song": "Happy - Pharrell Williams", "link": "https://www.youtube.com/watch?v=ZbZSe6N_BXs"},
            {"song": "Can't Stop the Feeling! - Justin Timberlake", "link": "https://www.youtube.com/watch?v=ru0K8uYEZWw"},
            {"song": "Coldplay - Hymn For The Weekend", "link": "https://www.youtube.com/watch?v=YykjpeuMNEk"},
            {"song": "Walking on Sunshine - Katrina and the Waves", "link": "https://www.youtube.com/watch?v=iPUmE-tne5U"},
            {"song": "Aankh Marey - Simmba", "link": "https://www.youtube.com/watch?v=_KhQT-LGb-4"},
            {"song": "Kar Gayi Chull - Kapoor & Sons", "link": "https://www.youtube.com/watch?v=NTHz9ephYTw"},
            {"song": "Uptown Funk - Mark Ronson ft. Bruno Mars", "link": "https://www.youtube.com/watch?v=OPf0YbXqDm0"},
            {"song": "Good Life - OneRepublic", "link": "https://www.youtube.com/watch?v=3Loi6UnpLfA"},
            {"song": "Dandelions - Ruth B.", "link": "https://www.youtube.com/watch?v=Kh6YlG5-WXA"},
            {"song": "Pehli Baar - Neha Kakkar", "link": "https://www.youtube.com/watch?v=SZpL2mj_vgA"},
        ],
        "sad": [
            {"song": "Someone Like You - Adele", "link": "https://www.youtube.com/watch?v=hLQl3WQQoQ0"},
            {"song": "Fix You - Coldplay", "link": "https://www.youtube.com/watch?v=k4V3Mo61fJM"},
            {"song": "Tears Dry on Their Own - Amy Winehouse", "link": "https://www.youtube.com/watch?v=ojdbDYahiCQ"},
            {"song": "The Night We Met - Lord Huron", "link": "https://www.youtube.com/watch?v=wGF7PswOENQ"},
            {"song": "Tujhe Kitna Chahne Lage - Kabir Singh", "link": "https://www.youtube.com/watch?v=AgX2II9si7w"},
            {"song": "Channa Mereya - Ae Dil Hai Mushkil", "link": "https://www.youtube.com/watch?v=284Ov7ysmfA"},
            {"song": "When I Was Your Man - Bruno Mars", "link": "https://www.youtube.com/watch?v=ekzHIouo8Q4"},
            {"song": "I Will Always Love You - Whitney Houston", "link": "https://www.youtube.com/watch?v=3JWTaaS7LdU"},
            {"song": "Stay - Rihanna ft. Mikky Ekko", "link": "https://www.youtube.com/watch?v=JF8BRvqGCNs"},
            {"song": "Agar Tum Saath Ho - Tamasha", "link": "https://www.youtube.com/watch?v=TI6HfZanr84"},
        ],
        "angry": [
            {"song": "Killing in the Name - Rage Against the Machine", "link": "https://www.youtube.com/watch?v=bWXazVhlyxQ"},
            {"song": "Break Stuff - Limp Bizkit", "link": "https://www.youtube.com/watch?v=EItGdA24g2U"},
            {"song": "Bodies - Drowning Pool", "link": "https://www.youtube.com/watch?v=06nYy3AqYxU"},
            {"song": "Duality - Slipknot", "link": "https://www.youtube.com/watch?v=6fVE8kSM43I"},
            {"song": "Dhoom Machale - Dhoom", "link": "https://www.youtube.com/watch?v=3N2qZ8eZ8cU"},
            {"song": "Aankh Marey - Simmba", "link": "https://www.youtube.com/watch?v=_KhQT-LGb-4"},
            {"song": "Enter Sandman - Metallica", "link": "https://www.youtube.com/watch?v=CD-E-LDc384"},
            {"song": "Numb - Linkin Park", "link": "https://www.youtube.com/watch?v=kXYiU_JCYtU"},
            {"song": "Believer - Imagine Dragons", "link": "https://www.youtube.com/watch?v=7wtfhZwyrcc"},
            {"song": "Bulls on Parade - Rage Against The Machine", "link": "https://www.youtube.com/watch?v=P6Q8Z0LB9B4"},
        ],
        "surprise": [
            {"song": "Badtameez dil - Yeh Jawaani hai Deewani", "link": "https://www.youtube.com/watch?v=II2EO3Nw4m0"},
            {"song": "I Wasn't Expecting That - Jamie Lawson", "link": "https://www.youtube.com/watch?v=Y-lI_tgQMMk"},
            {"song": "Unexpected Song - Sarah Brightman", "link": "https://www.youtube.com/watch?v=b5ie8hitiSc"},
            {"song": "What a Wonderful World - Louis Armstrong", "link": "https://www.youtube.com/watch?v=rBrd_3VMC3c"},
            {"song": "Tum Hi Ho - Aashiqui 2", "link": "https://www.youtube.com/watch?v=Umqb9KENgmk"},
            {"song": "Shape of You - Ed Sheeran", "link": "https://www.youtube.com/watch?v=JGwWNGJdvx8"},
            {"song": "Sugar - Maroon 5", "link": "https://www.youtube.com/watch?v=09R8_2nJtjg"},
            {"song": "Dynamite - BTS", "link": "https://www.youtube.com/watch?v=gdZLi9oWNZg"},
            {"song": "Old Town Road - Lil Nas X", "link": "https://www.youtube.com/watch?v=7ysFgElLwYU"},
            {"song": "Havana - Camila Cabello", "link": "https://www.youtube.com/watch?v=HCjNJDNzw8Y"},
        ],
        "disgust": [
            {"song": "Shut Up and Drive - Rihanna", "link": "https://www.youtube.com/watch?v=up7pvPqNkuU"},
            {"song": "You Don't Own Me - Lesley Gore", "link": "https://www.youtube.com/watch?v=OYB1rbL8EHo"},
            {"song": "Creep - Radiohead", "link": "https://www.youtube.com/watch?v=XFkzRNyygfk"},
            {"song": "Bad Guy - Billie Eilish", "link": "https://www.youtube.com/watch?v=DyDfgMOUjCI"},
            {"song": "Genda Phool - Delhi 6", "link": "https://www.youtube.com/watch?v=nqydfARGDh4"},
            {"song": "Disturbia - Rihanna", "link": "https://www.youtube.com/watch?v=1Q4a_YWqDLo"},
            {"song": "Rockstar - Post Malone", "link": "https://www.youtube.com/watch?v=mvwg2Y9syvA"},
            {"song": "Toxic - Britney Spears", "link": "https://www.youtube.com/watch?v=LOZuxwVk7TU"},
            {"song": "Hate Me - Blue October", "link": "https://www.youtube.com/watch?v=kf0vFhXxI1I"},
            {"song": "Heathens - Twenty One Pilots", "link": "https://www.youtube.com/watch?v=UPrVdEJdT6M"},
        ],
        "fear": [
            {"song": "Here Comes the Sun - The Beatles", "link": "https://www.youtube.com/watch?v=KQetemT1sWc"},
            {"song": "Waiting on the World to Change - John Mayer", "link": "https://www.youtube.com/watch?v=oBIxScJ5rlY"},
            {"song": "Dreams - Fleetwood Mac", "link": "https://www.youtube.com/watch?v=swJOIjjW69U"},
         {"song": "Budapest - George Ezra", "link": "https://www.youtube.com/watch?v=VHrLPs3_1Fs"},
            {"song": "Senorita - Zindagi Na Milegi Dobara", "link": "https://www.youtube.com/watch?v=2Z0Put0teCM"},
            {"song": "Kabira - Yeh Jawaani Hai Deewani", "link": "https://www.youtube.com/watch?v=jHNNMj5bNQw"},
            {"song": "Disturbia - Rihanna", "link": "https://www.youtube.com/watch?v=1Q4a_YWqDLo"},
            {"song": "Counting Stars - OneRepublic", "link": "https://www.youtube.com/watch?v=hT_nvWreIhg"},
            {"song": "It's My Life - Bon Jovi", "link": "https://www.youtube.com/watch?v=vx2u5uUu3DE"},
            {"song": "Channa Mereya - Ae Dil Hai Mushkil", "link": "https://www.youtube.com/watch?v=284Ov7ysmfA"},
        ]
    }
    # Select songs based on the dominant or user emotion
    if dominant_emotion in song_recommendations:
        selected_song = random.choice(song_recommendations[dominant_emotion])
    else:
        selected_song = {"song": "Let's open a playlist for you.", "link": "https://www.youtube.com/playlist?list=PL9bw4S5ePsEEqCMJSiYZ-KTtEjzVy0YvK"}
    save_emotion_to_db(dominant_emotion, selected_song['song'])

    return jsonify({
        "dominant_emotion": dominant_emotion,
        "selected_song": selected_song
    })
@app.route('/history')
def history():
    conn = sqlite3.connect('emotion_history.db')
    cursor = conn.cursor()
    cursor.execute('SELECT detected_emotion, song_recommendation, timestamp FROM emotions ORDER BY timestamp DESC')
    emotion_history = cursor.fetchall()
    conn.close()
    return render_template('history.html', emotion_history=emotion_history)
if __name__ == '__main__':
    app.run(debug=True)