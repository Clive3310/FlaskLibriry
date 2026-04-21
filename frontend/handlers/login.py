from flask import Blueprint, request, render_template, jsonify
import requests

blue_auth = Blueprint('login', __name__)


@blue_auth.route('/', methods=['GET', 'POST'])
def login_page():
    error = None
    if request.method == 'POST':
        ans = request.get_json()
        res = requests.post('http://127.0.0.1:8080/api/login', json=ans)
        dic = res.json()

        if res.status_code == 200:
            return jsonify(dic)
        else:
            error = "Wrong email or password"
            return jsonify({"login_error": error})
    else:
        return render_template("authentication/login.html", error=error)
