from config import CONNECTION_STRING, SHARE_NAME, STORAGE_NAME, URL_SASTOKEN
from azure.storage.fileshare import ShareDirectoryClient
import logging
import sys
from flask import Flask, request, jsonify, after_this_request

def _get_dir_client(dir):
    return ShareDirectoryClient.from_connection_string(CONNECTION_STRING, SHARE_NAME, dir)


def get_azure_file_client():
    dir_client = ShareDirectoryClient.from_connection_string(CONNECTION_STRING, SHARE_NAME, 'PhovinoAppLogs' )
    file_client = dir_client.get_file_client('logs.txt')
    return file_client


app = Flask(__name__)

@app.route('/')
def index():
    return 'Hello, World!'

@app.route('/get_file',methods=['POST'])
def get_file():
    file_content = request.form['file_content']
        # Append the content to another file
    with open("microservices_output.txt", "a") as dest_file:
            dest_file.write(file_content)
    log_file_path=get_azure_file_client()
    with open('microservices_output.txt', "rb") as file:
        log_file_path.upload_file(file)
    return jsonify({"message":"success"})
    
# # Configure logging to write to a file
# local_log_file_path = 'mircoservices_output.txt'
# logging.basicConfig(filename=local_log_file_path, level=logging.INFO)

# # Redirect stdout and stderr to the log file
# sys.stdout = open(local_log_file_path, 'a')
# sys.stderr = open(local_log_file_path, 'a')

# logs_dir=_get_dir_client('PhovinoAppLogs')
# log_file_path=logs_dir.get_file_client('logs.txt')

# with open(local_log_file_path, "rb") as file:
#     log_file_path.upload_file(file)

# print("done")

if __name__ == "__main__":
    app.run(debug=True)