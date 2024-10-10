from flask import Flask, render_template, request, jsonify
import sqlite3

app = Flask(__name__)


# Initialize the SQLite database
def init_db():
    conn = sqlite3.connect('test/annotations.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS annotations
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  text TEXT,
                  entities TEXT)''')
    conn.commit()
    conn.close()


# Route for the home page
@app.route('/')
def index():
    return render_template('index.html')


# Route to handle adding new entity classes dynamically
@app.route('/add_class', methods=['POST'])
def add_class():
    new_class = request.json.get('new_class')
    return jsonify({'message': 'Class added successfully', 'class': new_class})


# Route to submit annotations and save to the database
@app.route('/submit', methods=['POST'])
def submit():
    data = request.get_json()
    text = data.get('text')
    annotations = data.get('annotations')

    conn = sqlite3.connect('test/annotations.db')
    c = conn.cursor()
    c.execute('INSERT INTO annotations (text, entities) VALUES (?, ?)', (text, str(annotations)))
    conn.commit()
    conn.close()

    return jsonify({'message': 'Annotations saved successfully'})


# Route to import text files
@app.route('/import', methods=['POST'])
def import_file():
    file = request.files['file']
    if file:
        content = file.read().decode('utf-8')
        return jsonify({'content': content})
    return jsonify({'error': 'No file uploaded'})


if __name__ == '__main__':
    init_db()
    app.run(debug=True)
