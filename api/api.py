import json
from flask import Flask, request
from flask_cors import cross_origin, CORS
from functions import audience_coverage, channel_citation_index, net_promoter_score, love_rate, discussion_rate, character_length, top_emoji
from model_functions import calculate_brand
from influencers_functions import most_messages_users, high_negative_reactions, top_pagerank_influencers, top_bcr_rank_influencers
from api_redis import redis_get


app = Flask(__name__)
CORS(app, resources={r"/*":{"origins":"*"}})

@app.route("/post_involvement_analysis", methods=['POST','OPTIONS'])
@cross_origin(origin='*',headers=['Content-Type', 'Access-Control-Allow-Origin'])
def post_involvement_analysis():

    request_data = json.loads(request.data)
    
    crawlingId = request_data['crawlingId']
    groupId = request_data['groupId']
    crawling_case = redis_get(crawlingId)

    audience_coverage_metric = audience_coverage(crawling_case['vk']) 
    channel_cittaion_index_metric = channel_citation_index(crawling_case['vk'])
    # net_promoter_score_metric = net_promoter_score(crawling_case['vk'])
    love_rate_metric = love_rate(crawling_case['vk'])
    discussion_rate_metric = discussion_rate(crawling_case['vk'])
    # character_length_metric = character_length(crawling_case['vk'])
    top_emoji_metric = top_emoji(crawling_case['vk'])


    return {'audience_coverage_metric': audience_coverage_metric, 'channel_cittaion_index_metric': channel_cittaion_index_metric, 
            'net_promoter_score_metric': 1, 'love_rate_metric': love_rate_metric, 'discussion_rate_metric': discussion_rate_metric, 
            'character_length_metric': 1, 'top_emoji_metric': top_emoji_metric}

@app.route("/influencers_analysis", methods=['POST','OPTIONS'])
@cross_origin(origin='*',headers=['Content-Type', 'Access-Control-Allow-Origin'])
def influencers_analysis():

    request_data = json.loads(request.data)
    
    crawlingId = request_data['crawlingId']
    groupId = request_data['groupId']
    crawling_case = redis_get(crawlingId)

    most_messages = most_messages_users(crawling_case) 
    page_rank = top_pagerank_influencers(crawling_case)
    bcr_rank = top_bcr_rank_influencers(crawling_case)
    high_negative = high_negative_reactions(crawling_case)


    return {"most_messages": most_messages, "page_rank": page_rank, "bcr_rank": bcr_rank, "high_negative": high_negative}

@app.route("/brand_rating", methods=['POST','OPTIONS'])
@cross_origin(origin='*',headers=['Content-Type', 'Access-Control-Allow-Origin'])
def brand_rating():

    request_data = json.loads(request.data)
    
    crawlingId = request_data['crawlingId']
    groupId = request_data['groupId']
    weights = request_data['weights']

    print(weights)

    crawling_case = redis_get(crawlingId)
    brand_result = calculate_brand(crawling_case, tuple(weights)) 

    return {"rating": brand_result[0], "weakness": brand_result[1]}

if __name__ == '__main__':
    app.run(port=5003, debug=True)