import json
from flask import Flask, request
from flask_cors import cross_origin, CORS
from api_redis import redis_get


app = Flask(__name__)
CORS(app, resources={r"/*":{"origins":"*"}})

@app.route("/basic_analysis", methods=['POST','OPTIONS'])
@cross_origin(origin='*',headers=['Content-Type', 'Access-Control-Allow-Origin'])
def basic_analysis():

    request_data = json.loads(request.data)
    
    # здесь мы с фронта получили crawlingId, groupId и можем по ним найти группу, для которой будем считать статистику
    crawlingId = request_data['crawlingId']
    groupId = request_data['groupId']

    crawling_case = redis_get(crawlingId)

    # должны вернуть рассчитанную статистику (зависимости в формате JSON)
    return {'result': 1}

@app.route("/page_involvement_analysis", methods=['POST','OPTIONS'])
@cross_origin(origin='*',headers=['Content-Type', 'Access-Control-Allow-Origin'])
def page_involvement_analysis():

    request_data = json.loads(request.data)
    
    # здесь мы с фронта получили crawlingId, groupId и можем по ним найти группу, для которой будем считать статистику
    crawlingId = request_data['crawlingId']
    groupId = request_data['groupId']

    crawling_case = redis_get(crawlingId)

    # должны вернуть рассчитанную статистику (зависимости в формате JSON)
    return {'result': 1}

@app.route("/post_involvement_analysis", methods=['POST','OPTIONS'])
@cross_origin(origin='*',headers=['Content-Type', 'Access-Control-Allow-Origin'])
def post_involvement_analysis():

    request_data = json.loads(request.data)
    
    # здесь мы с фронта получили crawlingId, groupId и можем по ним найти группу, для которой будем считать статистику
    crawlingId = request_data['crawlingId']
    groupId = request_data['groupId']

    crawling_case = redis_get(crawlingId)

    # должны вернуть рассчитанную статистику (зависимости в формате JSON)
    return {'result': 1}

@app.route("/influencers_analysis", methods=['POST','OPTIONS'])
@cross_origin(origin='*',headers=['Content-Type', 'Access-Control-Allow-Origin'])
def influencers_analysis():

    request_data = json.loads(request.data)
    
    # здесь мы с фронта получили crawlingId, groupId и можем по ним найти группу, для которой будем считать статистику
    crawlingId = request_data['crawlingId']
    groupId = request_data['groupId']

    crawling_case = redis_get(crawlingId)

    # должны вернуть рассчитанную статистику (зависимости в формате JSON)
    return {'result': 1}

# @app.route("/brand_rating", methods=['POST','OPTIONS'])
# @cross_origin(origin='*',headers=['Content-Type', 'Access-Control-Allow-Origin'])
# def brand_rating():

#     request_data = json.loads(request.data)
    
#     # здесь мы с фронта получили crawlingId, groupId и можем по ним найти группу, для которой будем считать статистику
#     crawlingId = request_data['crawlingId']
#     groupId = request_data['groupId']

#     crawling_case = redis_get(crawlingId)

#     # должны вернуть рассчитанную статистику (зависимости в формате JSON)
#     return {'result': 1}

# if __name__ == '__main__':
#     app.run(port=5003, debug=True)