import json
from transformers import pipeline


class Telegram:
    def __init__(self, data):
        self.data = data
    
    def love_rate(self):
        """
        Коэффициент привлекательности (Love Rate)
        (Количество лайков / Общее количество уникальных просмотров ) * 100%
        """
        total_views = 0
        total_likes = 0

        for i in self.data:
            for j in i['tg']:
                total_views += sum([0 if _["views"] is None else _["views"] for _ in j["posts"]])
                total_likes += sum([reaction["count"] for post in j["posts"] for reaction in post["reactions"] if reaction["emoji"] == "❤"])

        if total_views > 0 and total_likes > 0:
            love_rate = (total_likes / total_views) * 100
            return love_rate
        else:
            return 0
        
    def engagement_rate(self):
        '''
        Коэффициент вовлеченности (Engagement Rate)
        (Общее число взаимодействий / Общее число подписчиков) * 100%
        '''
        total_interactions = 0
        total_comments = 0

        for i in self.data:
            for item in i['tg']:
                followers = item['membersCount']
                likes = sum(reaction['count'] for post in item['posts'] for reaction in post['reactions'])
                reposts = sum(post['forwards'] for post in item['posts'])

                unique_sender_ids = set(comment['sender_id'] for post in item['posts'] for comment in post.get('replies', []))

                total_comments += len(unique_sender_ids)
                total_interactions += likes + total_comments + reposts

        if total_interactions > 0 and followers > 0:
            engagement_rate = (total_interactions / followers) * 100
            return engagement_rate
        else:
            return 0
        
    def top_regions(self):
        '''
        Топ-20 регионов с наибольшим числом пользователей
        [регион | пользователей | % | тональность]
        '''
        # https://huggingface.co/blanchefort/rubert-base-cased-sentiment модель для анализа тональности
        classifier = pipeline("sentiment-analysis", model="blanchefort/rubert-base-cased-sentiment") 

        city_users = {}

        total_users = 0
        
        for i in self.data:
            for item in i['tg']:
                for post in item['posts']:
                    for reply in post.get('replies', []):
                        city = reply.get('city', 'Unknown')
                        if city not in city_users:
                            city_users[city] = []
                        city_users[city].append(reply['sender_id'])
                        total_users += 1

        city_stats = {}
        for city, users in city_users.items():
            users_count = len(users)
            percent = (users_count / total_users) * 100

            user_messages = [post['text'] for post in item['posts'] for post in post['replies'] if post.get('city') == city and post['text'] is not None]
            classified_messages = classifier(user_messages)
            len_messages = len(classified_messages)
            positive = len([i for i in classified_messages if i['label']=='POSITIVE']) / len_messages
            negative = len([i for i in classified_messages if i['label']=='NEGATIVE']) / len_messages
            neutral = len([i for i in classified_messages if i['label']=='NEUTRAL']) / len_messages

            city_stats[city] = {
                'users_count': users_count,
                'percent': percent,
                'user_messages': user_messages,
                'positive': positive,
                'negative': negative,
                'neutral': neutral
            }

        # Оставляем топ-20, сортируем city_stats по users_count 
        sorted_city_stats = dict(sorted(city_stats.items(), key=lambda x: x[1]['users_count'], reverse=True)[:20])

        top_regions = json.dumps(sorted_city_stats, indent=4, ensure_ascii=False)
        return top_regions
    

class Telegram:
    def __init__(self, data):
        self.data = data
    
    def love_rate(self):
        """
        Коэффициент привлекательности (Love Rate)
        (Количество лайков / Общее количество уникальных просмотров) * 100%
        """
        total_views = 0
        total_likes = 0

        for i in self.data:
            for j in i['vk']:
                valid_posts = [post for post in j["posts"] if post["views"] is not None] # только те посты, где просмотры != None
                total_views += sum([post["views"] for post in valid_posts])
                total_likes += sum([reaction["count"] for post in valid_posts for reaction in post["reactions"] if reaction["emoji"] == "like"])

        if total_views > 0 and total_likes > 0:
            love_rate = (total_likes / total_views) * 100
            return love_rate
        else:
            return 0
        
    def engagement_rate(self):
        '''
        Коэффициент вовлеченности (Engagement Rate)
        (Общее число взаимодействий / Общее число подписчиков) * 100%
        '''
        total_interactions = 0
        total_comments = 0

        for i in self.data:
            for item in i['vk']:
                followers = item['membersCount']
                likes = sum(reaction['count'] for post in item['posts'] for reaction in post['reactions'])
                reposts = sum(post['forwards'] for post in item['posts'])

                unique_sender_ids = set(comment['sender_id'] for post in item['posts'] for comment in post.get('replies', []))

                total_comments += len(unique_sender_ids)
                total_interactions += likes + total_comments + reposts

        if total_interactions > 0 and followers > 0:
            engagement_rate = (total_interactions / followers) * 100
            return engagement_rate
        else:
            return 0

    def top_regions(self):
        '''
        Топ-20 регионов с наибольшим числом пользователей
        [регион | пользователей | % | тональность]
        '''
        # https://huggingface.co/blanchefort/rubert-base-cased-sentiment модель для анализа тональности
        classifier = pipeline("sentiment-analysis", model="blanchefort/rubert-base-cased-sentiment") 

        city_users = {}

        total_users = 0
        
        for i in self.data:
            for item in i['vk']:
                for post in item['posts']:
                    for reply in post.get('replies', []):
                        city = reply.get('city', 'Unknown')
                        if city not in city_users:
                            city_users[city] = []
                        city_users[city].append(reply['sender_id'])
                        total_users += 1

        city_stats = {}
        for city, users in city_users.items():
            users_count = len(users)
            percent = (users_count / total_users) * 100

            user_messages = [post['text'] for post in item['posts'] for post in post['replies'] if post.get('city') == city and post['text'] is not None]
            classified_messages = classifier(user_messages)
            len_messages = len(classified_messages)
            positive = len([i for i in classified_messages if i['label']=='POSITIVE']) / len_messages
            negative = len([i for i in classified_messages if i['label']=='NEGATIVE']) / len_messages
            neutral = len([i for i in classified_messages if i['label']=='NEUTRAL']) / len_messages

            city_stats[city] = {
                'users_count': users_count,
                'percent': percent,
                'user_messages': user_messages,
                'positive': positive,
                'negative': negative,
                'neutral': neutral
            }

        # Оставляем топ-20, сортируем city_stats по users_count 
        sorted_city_stats = dict(sorted(city_stats.items(), key=lambda x: x[1]['users_count'], reverse=True)[:20])

        top_regions = json.dumps(sorted_city_stats, indent=4, ensure_ascii=False)
        return top_regions