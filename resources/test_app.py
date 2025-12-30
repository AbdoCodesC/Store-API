from flask_smorest import Blueprint
from flask.views import MethodView

blp = Blueprint('AppRunning', 'app_running', __name__, description="Check if the app is running")

@blp.route('/')
class AppRunning(MethodView):
  def get(self):
    return {"message": "The application is running."}, 200