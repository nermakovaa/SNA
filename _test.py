import pytest
import json
from analysis import PageRank, BetweennessCentralityRank, InfluencerTable, InfluencerTableNegative, Telegram, Vkontakte
from model import Model
import os


@pytest.fixture
def test_data():
    file_path = os.path.join(os.getcwd(), 'data/data.json') 
    with open(file_path, 'r') as file:
        file_content = file.read()
    return json.loads(file_content)


@pytest.fixture
def test_text():
    file_path = os.path.join(os.getcwd(), 'data/new_data.txt')  
    with open(file_path, 'r') as file:
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


class TestPageRank:
    '''
    Проверка ожидаемого значения для класса PageRank
    '''
    @pytest.fixture
    def page_rank(self, test_text):
        test = PageRank(test_text)
        return test
    
    def test_get_table(self, page_rank):
        result_dict = page_rank.get_table()
        assert result_dict != {}


class TestBetweennessCentralityRank:
    '''
    Проверка ожидаемого значения для класса BetweennessCentralityRank
    '''
    @pytest.fixture
    def betweenness_centralityRank(self, test_text):
        test = BetweennessCentralityRank(test_text)
        return test
    
    def test_get_table(self, betweenness_centralityRank):
        result_dict = betweenness_centralityRank.get_table()
        assert result_dict != {}


class TestInfluencerTable:
    '''
    Проверка ожидаемого значения для класса InfluencerTable
    '''
    @pytest.fixture
    def influencer_table(self, test_text):
        test = InfluencerTable(test_text)
        return test
    
    def test_influencer_table_result(self, influencer_table):
        result_dict = influencer_table.influencer_table_result()
        assert result_dict != {}
        

class TestInfluencerTableNegative:
    '''
    Проверка ожидаемого значения для класса InfluencerTableNegative
    '''
    @pytest.fixture
    def influencer_table_negative(self, test_text):
        test = InfluencerTableNegative(test_text)
        return test
    
    def test_get_results_dict(self, influencer_table_negative):
        result_dict = influencer_table_negative.get_results_dict()
        assert result_dict != {}
    
        
class TestModel:
    '''
    Граничные тесты для класса Model
    '''
    @pytest.fixture
    def model_instance(self, test_text):
        return Model(test_text)
    
    @pytest.mark.parametrize("method_name", ["brand_follower_ratio", "user_engagement_ratio", "top_audience_ratio", "love_rate", "trending_content_sentiment_ratio", "net_promoter_score", "brand_response_to_comments", "brand_reaction_to_negativity", "brand_responsiveness", "influencer_sentiment_ratio", "channel_citation_index"])
    def test_metrics(self, model_instance, method_name):
        '''
        Модульное тестирование
        '''
        metric_value = getattr(model_instance, method_name)()
        
        assert isinstance(metric_value, (int, float)) 
        assert 0 <= metric_value <= 1
    
    @pytest.mark.parametrize("weight", [tuple((100 / 11) for _ in range(11)),
                                      tuple((10.0, 10.0, 10.0, 10.0, 10.0, 10.0, 10.0, 10.0, 10.0, 10.0, 0.0)), 
                                      tuple((11.11, 0.0, 11.11, 11.11, 0.0, 11.11, 11.11, 11.11, 11.11, 11.11, 11.11)),
                                      tuple((12.5, 12.5, 0.0, 12.5, 0.0, 0.0, 12.5, 12.5, 12.5, 12.5, 12.5)),
                                      tuple((25.0, 0.0, 25.0, 25.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 25.0))])
    def test_calculate_model_weight(self, model_instance, weight):
        '''
        Интеграционное тестирование
        '''
        calculate_model, name_model = model_instance.calculate_model(weight)
        
        assert isinstance(calculate_model, (int, float)) 
        assert 0 <= calculate_model <= 100
        
        assert name_model in ('Показатели вовлеченности аудитории', 'Метрики для оценивания обратной связи аудитории',
                            'Метрики эффективности коммуникаций бренда', 'Метрики для оценивания взаимодействия с инфлюенсерами',
                            'Метрики информационного присутствия бренда')