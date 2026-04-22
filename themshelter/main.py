from flask import Flask, render_template, request
import sqlite3
import os

app = Flask(__name__)

# Initialize DB
def init_db():
    conn = sqlite3.connect('shelter.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS requests
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  name TEXT,
                  age INTEGER,
                  family INTEGER,
                  location TEXT,
                  shelter TEXT)''')
    conn.commit()
    conn.close()

init_db()

# Dummy shelters
shelters = [
    {"name": "Shelter A", "capacity": 5},
    {"name": "Shelter B", "capacity": 3},
    {"name": "Shelter C", "capacity": 8}
]

# Allocation logic
def allocate_shelter(family_size):
    for shelter in shelters:
        if shelter["capacity"] >= family_size:
            shelter["capacity"] -= family_size
            return shelter["name"]
    return "No Shelter Available"


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/request', methods=['GET', 'POST'])
def request_shelter():
    if request.method == 'POST':
        try:
            name = request.form.get('name')
            age = int(request.form.get('age'))
            family = int(request.form.get('family'))
            location = request.form.get('location')

            allocated = allocate_shelter(family)

            conn = sqlite3.connect('shelter.db')
            c = conn.cursor()
            c.execute("INSERT INTO requests (name, age, family, location, shelter) VALUES (?, ?, ?, ?, ?)",
                      (name, age, family, location, allocated))
            conn.commit()
            conn.close()

            return render_template('success.html', name=name, shelter=allocated)

        except Exception as e:
            return f"Error: {str(e)}"

    return render_template('form.html')


@app.route('/admin')
def admin():
    conn = sqlite3.connect('shelter.db')
    c = conn.cursor()
    c.execute("SELECT * FROM requests")
    data = c.fetchall()
    conn.close()
    return render_template('admin.html', data=data)


# FIX FOR LOCAL + RENDER DEPLOYMENT
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)