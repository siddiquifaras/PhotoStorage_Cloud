from flask import Flask,render_template,request,redirect,url_for,session
import requests
import os 
import base64
from werkzeug.utils import secure_filename
import json 
from urllib.parse import unquote
import re 
from flask_mysqldb import MySQL
from datetime import datetime
import logging
import sys

# Configure logging to write to a file
log_file_path = 'microservices_output.txt'
logging.basicConfig(filename=log_file_path, level=logging.INFO)

# Redirect stdout and stderr to the log file
sys.stdout = open(log_file_path, 'a')
sys.stderr = open(log_file_path, 'a')




app = Flask(__name__)

app.config['MYSQL_HOST'] = 'phovinologin.mysql.database.azure.com'
app.config['MYSQL_USER'] = 'phovinouser'
app.config['MYSQL_PASSWORD'] = 'Alpha12-'
app.config['MYSQL_DB'] = 'phovinodb'

# Initialize MySQL
mysql = MySQL(app)

app.secret_key="Mysecretkey"

@app.before_request
def before_request():
    with open("microservices_output.txt", "r") as file:
        file_content = file.read()

# Send a POST request with the file content in the request body
    response = requests.post('https://phovinologs.azurewebsites.net/get_file', data={"file_content": file_content})

UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def get_usage():
    url = "https://phovinousagemonitoring.azurewebsites.net/get_bandwidth_usage"
    data = {"username": session['username']}

    response = requests.post(url, json=data)

    if response.status_code == 200:
        result = response.json()["bandwidth_usage"]
        return  round(result,2)
    else:
        None

def get_storage():
    url = "https://phovinostoragemonitor.azurewebsites.net/get_storage_usage"
    data = {"username": session['username']}


    response = requests.post(url, json=data)

    if response.status_code == 200:
        result = response.json()["storage_usage"]
        return round(result,2)
    else:
        None

@app.route("/login",methods=['GET','POST'])
def login():
    if request.method=='POST':
       username = request.form.get('username')
       email = request.form.get('email')
       password = request.form.get('password')
       print(password,username,email)
       user_data = {
        'email': email,
        'password': password,
        'username': username
        }

    # Make a POST request to the /login endpoint
       response = requests.post('https://phovinologin.azurewebsites.net/login', json=user_data)

        # Check the response status code and content
       if response.status_code == 200:
            print('Login successful!')
            session['username']=username
            cur = mysql.connection.cursor()
            cur.execute("SELECT * FROM logins WHERE username = %s", (username,))
            result = cur.fetchone()
            cur.close()

            if result:
                print("Returning to home page after successful login")
                return redirect('/home')


        # Make a POST request to the /create_dir endpoint
            directory_data = {
    'dir': username
}
            response = requests.post('https://phovinobackend.azurewebsites.net/create_dir', json=directory_data)

            # Check the response status code and content
            if response.status_code == 200:
                print('Directory creation successful!')
                cur = mysql.connection.cursor()
                cur.execute("INSERT INTO logins (username) VALUES (%s)", (username,))
                mysql.connection.commit()
                cur.close()

                return redirect('/home')
            else:
                print(f'Directory creation request failed with status code {response.status_code}')
                return 'Some error occured'
       elif response.status_code == 401:
            print('Login failed. Invalid credentials.')
            return(response.json())
       else:
            return (f'Login request failed with status code {response.status_code}')
    return render_template('login.html')


@app.route("/")
def index():
    return redirect(url_for('login'))

@app.route("/home")
def home():
    usage=get_usage()
    storage=get_storage()

    return render_template("index.html",storage=storage,usage=usage,error=None)

@app.route("/uploader", methods=["POST"])
def uploader():
    try:
        usage=get_usage()
        storage=get_storage()
        if 'file' not in request.files:
            return "No file part"

        file = request.files['file']
        if file:
            file_size = len(file.read())
            file_size_in_mbs = round(file_size / (1024 * 1024), 2)
        if usage + file_size_in_mbs > 25 : 
            return render_template("index.html",usage=usage,storage=storage, error="Exceeded usage limit per day of 25MBs")
        if storage + file_size_in_mbs > 10 : 
            return render_template("index.html",usage=usage,storage=storage, error="Exceeded storage limit of 10MBs. Delete some files")
        if not file:
            return "No selected file"

        # Move the file pointer to the beginning
        file.seek(0)

        # Extracted file path
        url = 'https://phovinobackend.azurewebsites.net/upload_image'

        # Define the data you want to send in the request body
        image_content = base64.b64encode(file.read()).decode('utf-8')
        data = {
            'dir': session.get('username'),  # Use session.get to avoid KeyError
            'image': image_content
        }

        # Convert the data to JSON format
        json_data = json.dumps(data)

        # Set the headers to specify the content type as JSON
        headers = {'Content-Type': 'application/json'} 

        # Make a POST request to the API
        response = requests.post(url, data=json_data, headers=headers)
        print("Image uploaded successfuly to directory ",session["username"])

        return redirect(url_for("gallery"))
    except Exception as e:
        return f"Error: {str(e)}"


    return "Error"

@app.route("/gallery")
def gallery():
    usage=get_usage()
    storage=get_storage()
    url = 'https://phovinobackend.azurewebsites.net/get_images'

    # Define the data you want to send in the request body
    data = {
        'dir': session['username'],
    }

    # Convert the data to JSON format
    json_data = json.dumps(data)

    # Set the headers to specify the content type as JSON
    headers = {'Content-Type': 'application/json'}

    # Make a POST request to the API
    response = requests.post(url, data=json_data, headers=headers)
    response = response.json()
    print("response from getting images of gallery",response)
    current_datetime = datetime.now()

# Convert to timestamp (number of seconds since the epoch)
    timestamp = current_datetime.timestamp()
    timestamp=int(timestamp)
    return render_template("gallery.html",links = response, usage=usage,storage=storage, timestamp=timestamp)

@app.route("/delete",methods=['GET','POST'])
def delete_gallery():
    # Get the value of the 'url' query parameter
    # full_url=request.url
    # print("reached ")
    
    # url = full_url.replace("http://phovinoviewgen.azurewebsites.net/delete?url=","")
    # # url = full_url.replace("http://127.0.0.1:5000/delete?url=","")

    # print("Going to delete image here")       
    # new_sas_token='?sv=2022-11-02&ss=bfqt&srt=o&sp=rwdlacupiytfx&se=2023-12-30T13:47:45Z&st=2023-12-24T05:47:45Z&spr=https&sig=0tSEz8gRUmTCv45Wg2WFi08gd0rNBlQMlqs9lVy0tQk%3D'
    # url = re.sub(r'(?<=\.jp).*$', 'g' + new_sas_token, url)
    if request.method=='POST':
        url=request.form.get("img_url")
        print(url,"is legend")
     

        url=request.form.get("img_url")
        print(url,"is legend")



        fetch_url = 'https://phovinobackend.azurewebsites.net/delete_file'

        # Define the data you want to send in the request body
        data = {
            'url' : url 
        }

        # Convert the data to JSON format
        json_data = json.dumps(data)

        # Set the headers to specify the content type as JSON
        headers = {'Content-Type': 'application/json'}

        # Make a POST request to the API
        response = requests.post(fetch_url, data=json_data, headers=headers)
        response = response.json()
        return redirect(url_for("gallery"))
    return "Invalid request"

@app.route('/logout')
def logout():
    session.pop('username')
    return redirect(url_for('login'))

if __name__ == "__main__":
    app.run(debug=True)