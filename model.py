from collections import defaultdict
from transformers import pipeline


class Model:
    def __init__(self, data):
        self.data = data
    
    def brand_follower_ratio(self):
        '''
        Доля подписчиков сообщества среди активных пользователей
        '''
        pass
    
    def user_engagement_ratio(self):
        '''
        Доля комментирующих среди активных пользователей
        '''
        post_data = defaultdict(int)
        post_count = len(self.data['vk'][0]['posts'])

        ratios = []
        for post in self.data['vk'][0]['posts']:
            sender_ids = set(comment['sender_id'] for comment in post['replies'])

            unique_sender_count = len(sender_ids)
            unique_forward_count = post['forwards']
            unique_reaction_count = post['reactions'][0]['count']

            post_data[post['id']] = {
                'unique_sender_count': unique_sender_count,
                'unique_forward_count': unique_forward_count,
                'unique_reaction_count': unique_reaction_count
            }

            ratios.append(unique_sender_count / (unique_sender_count + unique_forward_count + unique_reaction_count))

        if post_count != 0:
            return sum(ratios) / post_count
        else:
            return 0
    
    def top_audience_ratio(self):
        '''
        Доля подписчиков из топ 100 активных пользователей
        '''
        pass
    
    def love_rate(self):
        '''
        Коэффициент привлекательности
        '''
        love_rate_sum = 0
        post_count = 0

        for post in self.data['vk'][0]['posts']:
            if post['views'] is not None:
                views = post['views']
                likes = post['reactions'][0]['count']
                
                love_rate = likes / views
                
                love_rate_sum += love_rate
                post_count += 1

        if post_count != 0:
            return love_rate_sum / post_count
        else:
            return 0
            
    def trending_content_sentiment_ratio(self):
        '''
        Доля позитивных комментариев из топ 10 наиболее обсуждаемых постов
        '''
        posts_with_replies = []

        for post in self.data['vk'][0]['posts']:
            post_id = post['id']
            replies = post['replies']
            
            if replies:
                posts_with_replies.append({'post_id': post_id, 'replies_count': len(replies), 'replies': replies})
                
        sorted_posts = sorted(posts_with_replies, key=lambda x: x['replies_count'], reverse=True)
        top_posts = sorted_posts[:10]
        
        classifier = pipeline("sentiment-analysis", model="blanchefort/rubert-base-cased-sentiment")
        post_sentiments = {}

        for post in top_posts:
            post_id = post['post_id']
            replies = post['replies']
            
            positive_count = 0
            negative_count = 0
            
            for reply in replies:
                text = reply['text']
                tone = classifier(text)[0]['label']
                
                if tone == 'POSITIVE':
                    positive_count += 1
                elif tone == 'NEGATIVE':
                    negative_count += 1
            
            post_sentiments[post_id] = {'positive_count': positive_count, 'negative_count': negative_count}

        total_loyalty = 0
        
        for post_id, counts in post_sentiments.items():
            total_comments = counts['positive_count'] + counts['negative_count']
            positive_ratio = counts['positive_count'] / total_comments if total_comments != 0 else 0

            total_loyalty += positive_ratio

        if len(post_sentiments) != 0:
            return total_loyalty / len(post_sentiments)
        else:
            return 0
            
    def net_promoter_score(self):
        '''
        Лояльность аудитории бренда
        '''
        classifier = pipeline("sentiment-analysis", model="blanchefort/rubert-base-cased-sentiment")
        post_sentiments = {}

        for post in self.data['vk'][0]['posts']:
            if len(post['replies']) != 0:
                post_id = post['id']
                replies = post['replies']
                
                positive_count = 0
                negative_count = 0
                
                for reply in replies:
                    text = reply['text']
                    tone = classifier(text)[0]['label'] 
                    
                    if tone == 'POSITIVE':
                        positive_count += 1
                    elif tone == 'NEGATIVE':
                        negative_count += 1
                
                post_sentiments[post_id] = {'positive_count': positive_count, 'negative_count': negative_count}

        total_loyalty = 0

        for post_id, counts in post_sentiments.items():
            total_comments = counts['positive_count'] + counts['negative_count']
            positive_ratio = counts['positive_count'] / total_comments if total_comments != 0 else 0

            total_loyalty += positive_ratio

        if len(post_sentiments) != 0:
            return total_loyalty / len(post_sentiments)
        else:
            return 0
        
    def brand_response_to_comments():
        '''
        Среднее время отклика компании на комментарии
        '''
        pass
        
    def brand_reaction_to_negativity():
        '''
        Среднее время отклика бренда на негативные комментарии
        '''
        pass
        
    def brand_responsiveness(self):
        '''
        Отзывчивость бренда
        '''
        answers = 0
        posts = 0

        for post in self.data['vk'][0]['posts']:
            posts += 1
            post_answered = False  
            for replies in post['replies']:
                if (replies['sender_name'].lower() in self.data['vk'][0]['groupName'].lower()) == True or (replies['last_name'].lower() in self.data['vk'][0]['groupName'].lower()) == True:
                    answers += 1
                    post_answered = True 
                    break  
            if post_answered:  
                continue

        if posts != 0:
            return answers / posts
        else:
            return 0
        
    def influencer_sentiment_ratio(self):
        '''
        Доля лояльных инфлюенсеров из топа
        '''
        pass
            
    def channel_citation_index(self):
        '''
        Индекс цитируемости
        '''
        channel_citation_sum = 0
        post_count = 0

        for post in self.data['vk'][0]['posts']:
            if post['views'] is not None:
                views = post['views']
                forwards = post['forwards']
                
                channel_citation_index = forwards / views
                
                channel_citation_sum += channel_citation_index
                post_count += 1

        if post_count != 0:
            return channel_citation_sum / post_count
        else:
            return 0  