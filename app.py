import os
import uuid
from flask import Flask, request, render_template, send_from_directory, jsonify

app = Flask(__name__)
UPLOAD_FOLDER = '/tmp/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

users = {}


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/signin', methods=['POST'])
def signin():
    data = request.get_json()
    username = data['username']
    if not username in users:
        users[username] = {}

    return 'Signup successful'
    

@app.route('/get_users', methods=['GET'])
def get_users():
    return jsonify(users)


@app.route('/get_items', methods=['POST'])
def get_items():
    data = request.get_json()
    username = data['username']
    if username not in users:
        return 'User not found. Please sign in first', 400
        
    return jsonify(users[username])

@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        return 'No file part', 400
    
    file = request.files['file']
    title = request.form.get('title')
    username = request.form.get('username')
    
    if not title or not username:
        return 'Title and username are required', 400
    
    if username not in users:
        return 'User not found. Please sign in first', 400
        
    filepath = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(filepath)
    
    # Generate UUID and store the file info
    file_uuid = str(uuid.uuid4())
    users[username][file_uuid] = [title, filepath]
    
    return f'File uploaded successfully with title: {title} and UUID: {file_uuid}'


@app.route('/uploads/<filename>', methods=['GET'])
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/delete_item', methods=['DELETE'])
def delete_item():
    data = request.get_json()
    username = data.get('username')
    file_uuid = data.get('file_uuid')
    
    if not username or not file_uuid:
        return 'Username and file_uuid are required', 400
        
    if username not in users:
        return 'User not found', 400
        
    if file_uuid not in users[username]:
        return 'File not found', 400
        
    # Get the filepath before removing the entry
    filepath = users[username][file_uuid][1]
    
    # Remove the file from storage
    try:
        os.remove(filepath)
    except OSError:
        # If file doesn't exist, continue with cleanup
        pass
        
    # Remove the entry from user's data
    del users[username][file_uuid]
    
    return 'File deleted successfully'


if __name__ == '__main__':
    app.run('0.0.0.0', port=5000, debug=True)

