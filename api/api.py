from flask import Flask, request, make_response, jsonify
import os
import sys

from services.token import TokenService
from services.deploy import DeployService
from services.secret import SecretService

app = Flask(__name__)

tokenService = False
deployService = False


# ------------------- The endpoint ---------------------------------------------
@app.route('/deploy', methods=['POST'])
def deploy():

    auth_header = request.headers.get('Authorization')
    if not tokenService.isValidHeader(auth_header):
        responseObject = {
            'status': 'fail',
            'message': 'Invalid token.'
        }
        return make_response(jsonify(responseObject)), 401
   
    request_data = request.get_json()

 
    try:
        if request.is_json and "services" in request_data:
            print("Following services will be restarted: " +   str(request.get_json()) , file=sys.stdout)
            deployService.performSelectedDeploy(request_data["services"])
        else:
            print("All services will be restarted.", file=sys.stdout)
            deployService.performDeploy()
        sys.stdout.flush()
    except Exception as e: 
        print(e,  file=sys.stderr)
        sys.stderr.flush()
        responseObject = {
            'status': 'fail',
            'message': 'Something went wrong.'
        }
        return make_response(jsonify(responseObject)), 500

    responseObject = {
        'status': 'success'
    }
    return make_response(jsonify(responseObject)), 201



#-------------------  Initialization of the services and endpoint --------------
if __name__ == '__main__':
    
    
    print("-----------------------------", file=sys.stdout)
    secretService = SecretService()
    tokenService = TokenService()
    deployService = DeployService()
    
    if secretService.loginEnabled:
        deployService.loginToRegistry(secretService.secrets)
        
    print("-----------------------------", file=sys.stdout)
    
    deployService.performDeploy()
    
    app.run(host='0.0.0.0')
