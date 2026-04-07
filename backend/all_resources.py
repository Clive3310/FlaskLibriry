from backend.resources.login import Login
from backend.resources.reg import Register
from backend.resources.refresh import Refresh
from backend.resources.check_user import CheckUser  # Для дебага


def add_resources(api):
    api.add_resource(Login, '/api/login')
    api.add_resource(Register, '/api/reg')
    api.add_resource(Refresh, '/api/refresh')
    api.add_resource(CheckUser, '/api/check_user')  # Для дебага
