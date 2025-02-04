from flask import Flask, render_template, request, redirect, session, flash
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
import pandas as pd
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your_secret_key'

ROUND_DEADLINE = datetime(2025, 1, 15, 17, 0)  # Example deadline

def import_dataset(filepath):
    return pd.read_excel(filepath).to_dict(orient='records')

@app.route('/team_data')
def team_data():
    if 'user' in session and session['role'] == 'team':
        data = import_dataset('team_data.xlsx')
        return render_template('team_data.html', data=data, username=session['user'])
    flash('Unauthorized access.')
    return redirect('/login')


# Database setup
def init_db():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

# User authentication
def authenticate_user(username, password, role):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('SELECT password FROM users WHERE username = ? AND role = ?', (username, role))
    user = cursor.fetchone()
    conn.close()
    if user and check_password_hash(user[0], password):
        return True
    return False

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = request.form['role']

        if authenticate_user(username, password, role):
            session['user'] = username
            session['role'] = role
            return redirect('/dashboard')
        else:
            flash('Invalid credentials. Please try again.')

    return render_template('login.html', session=session)

@app.route('/logout')
def logout():
    session.pop('user', None)  # Remove user from the session
    session.pop('role', None)  # Remove role from the session
    flash('You have been logged out.')
    return redirect('/login')


@app.route('/dashboard')
def dashboard():
    if 'user' in session:
        print(f"Logged in user: {session['user']}, Role: {session['role']}")
        if session['role'] == 'admin':
            return redirect('/admin_dashboard')
        elif session['role'] == 'team':
            return redirect('/team_dashboard')
    return redirect('/login') 

@app.route('/admin_dashboard')
def admin_dashboard():
    if 'user' in session and session['role'] == 'admin':
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM proposals')
        proposals = cursor.fetchall()
        conn.close()
        return render_template('admin_dashboard.html', proposals=proposals, username=session['user'])
    flash('Unauthorized access.')
    return redirect('/login')



def fetch_announcements():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('SELECT message, timestamp FROM announcements ORDER BY timestamp DESC')
    announcements = cursor.fetchall()
    conn.close()
    return announcements

@app.route('/team_dashboard')
def team_dashboard():
    if 'user' in session and session['role'] == 'team':
        announcements = fetch_announcements()
        return render_template('team_dashboard.html', username=session['user'], announcements=announcements)
    flash('Unauthorized access.')
    return redirect('/login')

@app.route('/submit_proposal', methods=['POST'])
def submit_proposal():
    if 'user' in session and session['role'] == 'team':
        # Check if the submission deadline has passed
        if datetime.now() > ROUND_DEADLINE:
            flash('Submission deadline has passed. You cannot submit your proposal now.')
            return redirect('/team_dashboard')

        # Proceed with the proposal submission if deadline is not passed
        team = session['user']
        round_number = request.form['round']
        proposal = request.form['proposal']
        
        # Insert the proposal into the database
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        cursor.execute('INSERT INTO proposals (team, round, proposal) VALUES (?, ?, ?)', (team, round_number, proposal))
        conn.commit()
        conn.close()

        flash('Proposal submitted successfully!')
        return redirect('/team_dashboard')

    flash('Unauthorized access. Please log in as a team.')
    return redirect('/login')

@app.route('/score_submission', methods=['POST'])
def score_submission():
    if 'user' in session and session['role'] == 'admin':
        proposal_id = request.form['proposal_id']
        score = request.form['score']
        feedback = request.form['feedback']
        
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE proposals
            SET score = ?, feedback = ?
            WHERE id = ?
        ''', (score, feedback, proposal_id))
        conn.commit()
        conn.close()
        flash('Feedback submitted successfully!')
        return redirect('/admin_dashboard')
    flash('Unauthorized access.')
    return redirect('/login')

@app.route('/post_announcement', methods=['POST'])
def post_announcement():
    if 'user' in session and session['role'] == 'admin':
        message = request.form['message']
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        cursor.execute('INSERT INTO announcements (message) VALUES (?)', (message,))
        conn.commit()
        conn.close()
        flash('Announcement posted successfully!')
        return redirect('/admin_dashboard')
    flash('Unauthorized access.')
    return redirect('/login')

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
