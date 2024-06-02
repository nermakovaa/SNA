import pytest
import json
from analysis import Telegram, Vkontakte, General
from model import Model
from faker import Faker
import random


@pytest.fixture
def test_data():
    with open('/home/nermakovaa/semester_4/SNA/SNA/data/data.json', 'r') as file:
        file_content = file.read()
    return json.loads(file_content)


@pytest.fixture
def test_text():
    with open('/home/nermakovaa/semester_4/SNA/SNA/data/text.txt', 'r') as file:
        file_content = file.read()
    return json.loads(file_content)
    

class TestTelegram:
    '''
    Проверка ожидаемого значения для класса Telegram
    '''
    @pytest.fixture
    def telegram_instance(self, test_data):
        return Telegram(test_data)

    def test_love_rate(self, telegram_instance):
        love_rate = telegram_instance.love_rate()
        assert love_rate == 1.1029618652810864
        
    def test_engagement_rate(self, telegram_instance):
        engagement_rate = telegram_instance.engagement_rate()
        assert engagement_rate == 0.9626264357963312 
        
    def test_engagement_rate_by_reach(self, telegram_instance):
        engagement_rate_by_reach = telegram_instance.engagement_rate_by_reach()
        assert engagement_rate_by_reach == 2.106507099848061
        
    def test_top_regions(self, telegram_instance):
        top_regions = telegram_instance.top_regions()
        assert top_regions != {}  
        
    def test_net_promoter_score(self, telegram_instance):
        net_promoter_score = telegram_instance.net_promoter_score()
        assert net_promoter_score > 0 
        
    def test_top_emoji(self, telegram_instance):
        top_emoji = telegram_instance.top_emoji()
        assert top_emoji == {'❤': 588, '👍': 82, '🔥': 74, '🤣': 71, '👎': 36}   
        
    def test_character_length(self, telegram_instance):
        character_length = telegram_instance.character_length()
        assert character_length != {}
        

class TestVkontakte:
    '''
    Проверка ожидаемого значения для класса Vkontakte
    '''
    @pytest.fixture
    def vkontakte_instance(self, test_data):
        return Vkontakte(test_data)

    def test_love_rate(self, vkontakte_instance):
        love_rate = vkontakte_instance.love_rate()
        assert love_rate == 35.0  
        
    def test_engagement_rate(self, vkontakte_instance):
        engagement_rate = vkontakte_instance.engagement_rate()
        assert engagement_rate == 0.135772935928105  
        
    def test_top_regions(self, vkontakte_instance):
        top_regions = vkontakte_instance.top_regions()
        assert top_regions != {}
        
    def test_net_promoter_score(self, vkontakte_instance):
        net_promoter_score = vkontakte_instance.net_promoter_score()
        assert net_promoter_score != {}
        
    def test_character_length(self, vkontakte_instance):
        character_length = vkontakte_instance.character_length()
        assert character_length != {}
        
    def test_top_emoji(self, vkontakte_instance):
        top_emoji = vkontakte_instance.top_emoji()
        assert len(top_emoji.keys()) == 5
        

@pytest.fixture
def prepare_data():
    sender_id = list(range(108718, 108818)) 
    connections = [(random.choice(sender_id), random.choice(sender_id)) for _ in range(len(sender_id))] 

    fake = Faker()

    example_data = {}
    for id in sender_id:
        example_data[id] = {"first_name": fake.first_name(), "last_name": fake.last_name()}

    return sender_id, example_data, connections


class TestGeneral:
    '''
    Проверка ожидаемого значения для класса General
    '''
    @pytest.fixture
    def general_instance(self, prepare_data):
        return General(prepare_data)
    
    def test_page_rank(self, general_instance, prepare_data):
        sender_id, example_data, connections = prepare_data
        
        result_dict = general_instance.page_rank(sender_id, example_data, connections)
        assert result_dict != {}

    def test_betweenness_centrality_rank_not_empty(self, general_instance, prepare_data):
        sender_id, example_data, connections = prepare_data

        result_dict = general_instance.betweenness_centrality_rank(sender_id, example_data, connections)
        assert result_dict != {}
        
 
class TestModel:
    '''
    Граничные тесты для класса Model
    '''
    @pytest.fixture
    def model_instance(self, test_text):
        return Model(test_text)
        
    def test_user_engagement_ratio(self, model_instance):
        user_engagement_ratio = model_instance.user_engagement_ratio()
        assert 0 <= user_engagement_ratio <= 1

    def test_love_rate(self, model_instance):
        love_rate = model_instance.love_rate()
        assert 0 <= love_rate <= 1 
        
    def test_trending_content_sentiment_ratio(self, model_instance):
        trending_content_sentiment_ratio = model_instance.trending_content_sentiment_ratio()
        assert 0 <= trending_content_sentiment_ratio <= 1
        
    def test_net_promoter_score(self, model_instance):
        net_promoter_score = model_instance.net_promoter_score()
        assert 0 <= net_promoter_score <= 1
        
    def test_brand_responsiveness(self, model_instance):
        brand_responsiveness = model_instance.brand_responsiveness()
        assert 0 <= brand_responsiveness <= 1
    
    def test_channel_citation_index(self, model_instance):
        channel_citation_index = model_instance.channel_citation_index()
        assert 0 <= channel_citation_index <= 1