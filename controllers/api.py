from flask import Blueprint
from flask_restful import Api

from controllers.resources.ApiResources import UsersLocationAPI, ConversationsNextApi, StatisticsCompleteApi

api_template = Blueprint('api', __name__)
api = Api(api_template)

api.add_resource(UsersLocationAPI, '/users/location', endpoint='users_location')
api.add_resource(ConversationsNextApi, '/conversations/next', endpoint='conversations_next')
api.add_resource(StatisticsCompleteApi, '/statistics/complete', endpoint='statistics_completed')
