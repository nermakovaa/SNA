import unittest
import json
from analysis import Telegram, Vkontakte
from model import Model


class TestTelegram(unittest.TestCase):
    with open('/home/nermakovaa/semester_4/SNA/SNA/data/data.json', 'r') as file:
        data = json.load(file)

    def test_love_rate(self):
        telegram = Telegram(self.data)
        love_rate = telegram.love_rate()
        self.assertEqual(love_rate, 1.1029618652810864)  
        
    def test_engagement_rate(self):
        telegram = Telegram(self.data)
        engagement_rate = telegram.engagement_rate()
        self.assertEqual(engagement_rate, 0.9626264357963312)  
        
    def test_engagement_rate_by_reach(self):
        telegram = Telegram(self.data)
        engagement_rate_by_reach = telegram.engagement_rate_by_reach()
        self.assertEqual(engagement_rate_by_reach, 2.106507099848061)  
        
    def test_top_emoji(self):
        telegram = Telegram(self.data)
        top_emoji = telegram.top_emoji()
        self.assertEqual(top_emoji, {'❤': 588, '👍': 82, '🔥': 74, '🤣': 71, '👎': 36})      
        

class TestVkontakte(unittest.TestCase):
    with open('/home/nermakovaa/semester_4/SNA/SNA/data/data.json', 'r') as file:
        data = json.load(file)

    def test_love_rate(self):
        vkontakte = Vkontakte(self.data)
        love_rate = vkontakte.love_rate()
        self.assertEqual(love_rate, 35.0)  
        
    def test_engagement_rate(self):
        vkontakte = Vkontakte(self.data)
        engagement_rate = vkontakte.engagement_rate()
        self.assertEqual(engagement_rate, 0.135772935928105)  
        
    def test_top_emoji(self):
        vkontakte = Vkontakte(self.data)
        net_promoter_score = vkontakte.net_promoter_score()
        self.assertEqual(net_promoter_score, 37.5)     
        
        
class TestModel(unittest.TestCase):
    with open('/home/nermakovaa/semester_4/SNA/SNA/data/text.txt', 'r') as file:
        file_content = file.read()
        data = json.loads(file_content)

    def test_love_rate(self):
        model = Model(self.data)
        love_rate = model.love_rate()
        self.assertTrue(0 < love_rate < 1)
        
    def test_trending_content_sentiment_ratio(self):
        model = Model(self.data)
        trending_content_sentiment_ratio = model.trending_content_sentiment_ratio()
        self.assertTrue(0 < trending_content_sentiment_ratio < 1)
        
    def test_net_promoter_score(self):
        model = Model(self.data)
        net_promoter_score = model.net_promoter_score()
        self.assertTrue(0 < net_promoter_score < 1)
        
    def test_brand_responsiveness(self):
        model = Model(self.data)
        brand_responsiveness = model.brand_responsiveness()
        self.assertTrue(0 < brand_responsiveness < 1)
        
    def test_channel_citation_index(self):
        model = Model(self.data)
        channel_citation_index = model.channel_citation_index()
        self.assertTrue(0 < channel_citation_index < 1)
        
        
if __name__ == '__main__':
    unittest.main()