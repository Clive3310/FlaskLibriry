from flask import Blueprint, render_template, request, redirect
import requests

blue_reg = Blueprint('registration', __name__)


@blue_reg.route('/', methods=['GET', 'POST'])
def reg_page():
    error = None
    if request.method == 'POST':
        dic = request.form.to_dict()
        res = requests.post('http://127.0.0.1:8080/api/reg', json=dic)
        if res.status_code == 201:
            return redirect('/login')
        else:
            error = "User already exists"
            return render_template("authentication/reg.html", error=error)
    else:
        return render_template("authentication/reg.html", error=error)
