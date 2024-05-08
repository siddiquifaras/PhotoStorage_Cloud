from quart import Quart, request, jsonify
from service import get_bandwidth_usage

app = Quart(__name__)

class User:
    def __init__(self, username):
        self.username = username

@app.route("/")
async def index():
    return "Application is all set"

@app.route("/get_bandwidth_usage", methods=["POST"])
async def post_get_bandwidth_usage():
    data = await request.get_json()

    if "username" not in data:
        return jsonify({"error": "Username not provided"}), 400

    user = User(username=data["username"])
    result = await get_bandwidth_usage(user.username)

    return jsonify({"bandwidth_usage": result})

if __name__ == "__main__":
    app.run(debug=True)
