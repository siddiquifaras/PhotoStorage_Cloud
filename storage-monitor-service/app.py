from quart import Quart, request, jsonify
from service import get_storage_usage

app = Quart(__name__)

class User:
    def __init__(self, username):
        self.username = username

@app.route("/")
async def index():
    return "Application is all set"

@app.route("/get_storage_usage", methods=["POST"])
async def post_get_storage_usage():
    data = await request.get_json()

    if "username" not in data:
        return jsonify({"error": "Username not provided"}), 400

    user = User(username=data["username"])
    result = get_storage_usage(user.username)
    print(result)

    return jsonify({"storage_usage": result})

if __name__ == "__main__":
    app.run(debug=True)
