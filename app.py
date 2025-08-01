from flask import Flask, request, render_template, redirect, url_for, session
from flask_socketio import SocketIO, emit, join_room
import psycopg2
import psycopg2.extras
from dotenv import load_dotenv
import os

load_dotenv()
port = int(os.environ.get("PORT", 5000))
app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY")
socketio = SocketIO(app)

def get_db_connection():
    try:
        return psycopg2.connect(
            host=os.getenv("DB_HOST"),
            dbname=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            port=os.getenv("DB_PORT", 5432)
        )
    except Exception as e:
        print("Database connection failed:", e)
        return None

def check_in_database(username, password):
    conn = get_db_connection()
    if conn is None:
        return False
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM users WHERE username=%s AND password=%s", (username, password))
            user = cur.fetchone()
        return bool(user)
    finally:
        conn.close()

def fetch_messages():
    conn = get_db_connection()
    if conn is None:
        return []
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute("SELECT username AS user, msg AS msg FROM messages ORDER BY timestamp ASC")
            messages = cur.fetchall()
        return messages
    finally:
        conn.close()

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

@socketio.on('join_room')
def handle_join(data):
    join_room("global")

@socketio.on('send_message')
def handle_send(data):
    username = data['user']
    message = data['message']
    conn = get_db_connection()
    if conn is None:
        emit('receive_message', {'user': 'System', 'message': 'DB connection failed, message not saved.'})
        return
    try:
        with conn.cursor() as cur:
            cur.execute("INSERT INTO messages (username, msg) VALUES (%s, %s)", (username, message))
            conn.commit()
    except Exception as e:
        print("Failed to save message:", e)
    finally:
        conn.close()
    emit('receive_message', {'user': username, 'message': message}, broadcast=True)

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=port)
