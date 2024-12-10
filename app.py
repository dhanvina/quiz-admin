from flask import Flask, render_template, request, redirect, url_for, session
from firebase_admin import credentials, firestore, initialize_app

# Initialize Flask App
app = Flask(__name__)
app.secret_key = "supersecretkey"  # Replace with an actual secret key

# Firebase Admin Initialization
cred = credentials.Certificate("serviceAccountKey.json")
initialize_app(cred)
db = firestore.client()

# Routes
@app.route('/')
def login():
    return render_template('login.html')

@app.route('/authenticate', methods=['POST'])
def authenticate():
    school_code = request.form['school_code']
    # Authenticate against Firestore (Assuming a 'schools' collection exists)
    schools_ref = db.collection('schools').document(school_code).get()
    if schools_ref.exists:
        session['school_code'] = school_code
        return redirect(url_for('dashboard'))
    return "Invalid School Code", 403

@app.route('/dashboard')
def dashboard():
    school_code = session.get('school_code', None)
    if school_code:
        return render_template('dashboard.html', school_code=school_code)
    return redirect(url_for('login'))

@app.route('/quizzes')
def quizzes():
    quizzes_ref = db.collection('quizzes')
    quizzes = [doc.to_dict() for doc in quizzes_ref.stream()]
    return render_template('quizzes.html', quizzes=quizzes)

@app.route('/leaderboard')
def leaderboard():
    school_code = session.get('school_code')
    results_ref = db.collection('results').where('school_code', '==', school_code)
    results = sorted([doc.to_dict() for doc in results_ref.stream()], key=lambda x: (x['score'], x['time']), reverse=True)
    return render_template('leaderboard.html', results=results)

@app.route('/results')
def results():
    school_code = session.get('school_code')
    results_ref = db.collection('results').where('school_code', '==', school_code)
    results = [doc.to_dict() for doc in results_ref.stream()]
    return render_template('results.html', results=results)

if __name__ == '__main__':
    app.run(debug=True)
