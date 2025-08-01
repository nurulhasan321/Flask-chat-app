from flask import Flask, request, render_template, redirect, url_for, session
from flask_socketio import SocketIO, emit, join_room
import mysql.connector
from dotenv import load_dotenv
import os

load_dotenv()

host_ip = os.getenv("FLASK_RUN_HOST", "127.0.0.1")
app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")
socketio = SocketIO(app)

# Database connection
def get_db_connection():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME")
    )


# Check credentials
def check_in_database(username, password):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE username=%s AND password=%s", (username, password))
    user = cur.fetchone()
    cur.close()
    conn.close()
    return bool(user)

# Fetch messages
def fetch_messages():
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT username AS user, msg AS msg FROM messages ORDER BY timestamp ASC")
    messages = cur.fetchall()
    cur.close()
    conn.close()
    return messages

@app.route('/', methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        if check_in_database(username, password):
            session['username'] = username
            return redirect(url_for("chat_box"))
        else:
            return render_template("login.html", error="Invalid username or password.")
    return render_template("login.html")

@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))

@app.route('/index')
def chat_box():
    if 'username' not in session:
        return redirect(url_for('login'))
    chats = fetch_messages()
    return render_template('index.html', chats=chats)

# Socket.IO events
@socketio.on('join_room')
def handle_join(data):
    join_room("global")  # Shared room for all users

@socketio.on('send_message')
def handle_send(data):
    username = data['user']
    message = data['message']

    # Save message to DB
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO messages (username, msg) VALUES (%s, %s)", (username, message))
    conn.commit()
    cur.close()
    conn.close()

    emit('receive_message', {'user': username, 'message': message}, room="global")

if __name__ == '__main__':

    port = int(os.environ.get("PORT", 5000))
    socketio.run(app, host='0.0.0.0', port=port)

