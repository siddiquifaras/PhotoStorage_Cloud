from flask import Flask, request, jsonify, render_template
from azure.storage.fileshare import ShareDirectoryClient
import uuid
from config import CONNECTION_STRING, SHARE_NAME, STORAGE_NAME, URL_SASTOKEN
import requests
import json
import base64

app = Flask(__name__)

URL_HOSTNAME = f"https://{STORAGE_NAME}.file.core.windows.net"

def _get_dir_client(dir):
    return ShareDirectoryClient.from_connection_string(CONNECTION_STRING, SHARE_NAME, dir)

def _get_url(dir, file_name):
    return f"{URL_HOSTNAME}/{SHARE_NAME}/{dir}/{file_name}{URL_SASTOKEN}"

def _extract_url(url):
    url = url.replace(URL_HOSTNAME, "")
    url = url.replace(SHARE_NAME, "")
    url = url.replace(URL_SASTOKEN, "")

    url = url.split("/")
    url = [i for i in url if i != ""]
    dir_name, file_name = url

    return dir_name, file_name

def create_dir(dir):
    dir_client = _get_dir_client(dir)
    dir_client.create_directory()

# def upload_image_to_dir(dir, local_img_path):
#     dir_client = _get_dir_client(dir)
#     random_filename = str(uuid.uuid4()) + ".jpg"
#     file_client = dir_client.get_file_client(random_filename)

#     with open(local_img_path, "rb") as file:
#         file_client.upload_file(file)

def upload_image_to_dir(dir, image_data):
    try:
        dir_client = _get_dir_client(dir)
        random_filename = str(uuid.uuid4()) + ".jpg"
        file_client = dir_client.get_file_client(random_filename)

        # Upload the file content to Azure Storage
        file_client.upload_file(image_data)
        

        print(f"Image uploaded successfully to Azure Storage: {random_filename}")

        return {"message": "Image uploaded successfully", "filename": random_filename}
    except Exception as e:
        print(f"Error uploading image to Azure Storage: {str(e)}")
        return {"error": f"Error uploading image to Azure Storage: {str(e)}"}


def get_images_from_dir(dir):
    dir_client = _get_dir_client(dir)
    files = [i for i in dir_client.list_directories_and_files()]
    files = [_get_url(dir, file.name) for file in files]

    return files

def delete_file_using_url(url):
    dir, filename = _extract_url(url)
    dir_client = _get_dir_client(dir)
    file_client = dir_client.get_file_client(filename)
    file_client.delete_file()
@app.route('/')
def index():

    return "Henllo   World"




@app.route('/create_dir', methods=['POST'])
def create_directory():
    data = request.get_json()
    create_dir(data['dir'])
    return jsonify(message="success"), 200



# @app.route('/upload_image', methods=['GET','POST'])
# def upload_image():
#     data = request.get_json()
#     upload_image_to_dir('username','E:\\flask-helloworld\\img.png' )
#     return jsonify(message="Image uploaded successfully"), 200
@app.route('/upload_image', methods=['POST'])
def upload_image():
    try:
        # Assuming the 'dir' and 'image' parameters are in the JSON payload of the request
        data = request.get_json()

        if 'dir' in data and 'image' in data:
            dir_name = data['dir']

            # Assuming 'image' is a base64-encoded string representation of the image
            print("reached here")

            # You may need to decode the base64 data depending on how it's sent
            # If it's a file path, use it directly, otherwise, you may need to decode it
            image_data = base64.b64decode(data['image'])

            result = upload_image_to_dir(dir_name, image_data)
            print("image uploaded")
            return jsonify(result), 200
        else:
            print("error")
            return jsonify({"error": "Invalid request format"}), 400
    except Exception as e:
        print(e)
        return jsonify({"error": f"Internal Server Error: {str(e)}"}), 500

@app.route('/get_images', methods=['POST'])
def get_images():
    data = request.get_json()
    images = get_images_from_dir(data['dir'])
    return jsonify(images), 200

@app.route('/delete_file', methods=['POST'])
def delete_file():
  try:
    data = request.get_json()
    delete_file_using_url(data['url'])
    return jsonify(message="File deleted successfully"), 200
  except Exception as e:
      return jsonify(error=e),500

if __name__ == '__main__':
    app.run(debug=True)
