from flask import Flask, request, render_template
from supabase import create_client
import os
import secrets

url = os.getenv('SUPABASE_URL')
key = os.getenv('SUPABASE_KEY')
supabase = create_client(url, key)

app = Flask(__name__)

cities = []

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/stream')
def stream():
    return render_template('stream/index.html')

@app.route('/stream/init')
def stream_init():
    return render_template('stream/init.html')

@app.route('/api/stream/init/email', methods=['POST'])
def stream_init_api():
    data = request.json
    
    if 'email' not in data:
        return {'error': 'Email not provided'}, 400
    
    email = data['email']
    response = supabase.table('stuff').select('id').eq('id', email).execute()

    return {'exists': len(response.data) > 0}

@app.route('/api/stream/init/password', methods=['POST'])
def stream_init_password():
    data = request.json

    if 'email' not in data or 'password' not in data:
        return {'error': 'Email or password not provided'}, 400

    email = data['email']
    password = data['password']

    response = supabase.table('stuff').select('id, password, city').eq('id', email).execute()

    if response.data:
        user = response.data[0]
        stored_password = user['password']

        if password == stored_password:
            session = secrets.token_urlsafe(64)
            city = user['city']
            supabase.table('stuff').update({'session': session}).eq('id', email).execute()
            return {'message': 'true', 'session': session, 'city': city}, 200
        else:
            return {'message': 'error'}, 401
    else:
        return {'error': 'User not found'}, 404

if __name__ == '__main__':
    app.run(debug=True, port=9000)