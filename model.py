from collections import defaultdict
from transformers import pipeline
import networkx as nx


class Model:
    def __init__(self, data):
        self.data = data
    
    def brand_follower_ratio(self):
        '''
        Доля подписчиков сообщества среди активных пользователей
        '''
        active_users = 0
        followers = 0

        for post in self.data['vk'][0]['posts']:
            if post['from'] != None:
                active_users += 1
                followers += post['from']['is_member']
                
        if active_users != 0:
            return followers / active_users
        else:
            return 0
    
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
        Доля подписчиков из топа активных пользователей
        '''
        active_users = 0
        followers = 0

        for post in self.data['vk'][0]['posts']:
            if post['from'] != None:
                sorted_posts = sorted(self.data['vk'][0]['posts'], key=lambda x: (x['views'] if x['views'] is not None else len(x['replies'])) if x['from'] is not None else -1, reverse=True)
                top_posts = sorted_posts[:10]

        for post in top_posts:
            active_users += 1
            followers += post['from']['is_member']
                
        if active_users != 0:
            return followers / active_users
        else:
            return 0
    
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
            return (love_rate_sum / post_count) / 0.05
        else:
            return 0
            
    def trending_content_sentiment_ratio(self):
        '''
        Доля позитивных комментариев из топа наиболее обсуждаемых постов
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
        
    def brand_response_to_comments(self):
        '''
        Среднее время отклика компании на комментарии
        '''
        count_1 = 0
        count_0 = 0

        for post in self.data['vk'][0]['posts']:
            text = post['text'].lower()
            brand_name = self.data['vk'][0]['groupName'].lower()
            
            if brand_name in text:
                for reply in post['replies']:
                    if reply.get('sender_name', '').lower() in brand_name or reply.get('last_name', '').lower() in brand_name:
                        count_1 += 1
                        break
                else:
                    count_0 += 1

        total_posts = count_1 + count_0

        if total_posts != 0:
            return (count_1 + count_0) / total_posts
        else:
            return 0
        
    def brand_reaction_to_negativity(self):
        count_1 = 0
        count_0 = 0

        classifier = pipeline("sentiment-analysis", model="blanchefort/rubert-base-cased-sentiment")

        for post in self.data['vk'][0]['posts']:
            text = post['text'].lower()
            brand_name = self.data['vk'][0]['groupName'].lower()
            
            if brand_name in text:
                result = classifier(text)
                tone = result[0]['label']

                if tone == 'NEGATIVE':
                    for reply in post['replies']:
                        if reply.get('sender_name', '').lower() in brand_name or reply.get('last_name', '').lower() in brand_name:
                            count_1 += 1
                            break
                    else:
                        count_0 += 1

        total_posts = count_1 + count_0

        if total_posts != 0:
            return (count_1 + count_0) / total_posts
        else:
            return 0
        
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
        connections = []

        for post in self.data['vk'][0]['posts']:
            if post['from'] != None:
                post_connections = [(post['from']['id'], reply['sender_id']) for reply in post['replies']]
                connections.extend(post_connections)

        G = nx.DiGraph()
        G.add_edges_from(connections)
        pos = nx.spring_layout(G, k=0.15, iterations=20) 

        # pagerank - https://networkx.org/documentation/stable/reference/algorithms/generated/networkx.algorithms.link_analysis.pagerank_alg.pagerank.html
        pr = nx.pagerank(G)
        sorted_pr = sorted(pr.items(), key=lambda x: x[1], reverse=True)

        top_10_pr = sorted_pr[:10] 
        top_10_ids_pr = [id for id, pr in top_10_pr]

        # https://networkx.org/documentation/stable/reference/algorithms/generated/networkx.algorithms.centrality.betweenness_centrality.html
        centrality = nx.betweenness_centrality(G)
        sorted_centrality = sorted(centrality.items(), key=lambda x: x[1], reverse=True)

        top_10_centrality = sorted_centrality[:10] 
        top_10_ids_centrality = [id for id, _ in top_10_centrality]

        top_users = list(set(top_10_ids_pr + top_10_ids_centrality))

        classifier = pipeline("sentiment-analysis", model="blanchefort/rubert-base-cased-sentiment")

        user_sentiments = {}

        for post in self.data['vk'][0]['posts']:
            if post['from'] is not None and post['from']['id'] in top_users:
                text = post['text']
                result = classifier(text)[0]

                user_id = post['from']['id']
                if user_id not in user_sentiments:
                    user_sentiments[user_id] = {"POSITIVE": 0, "NEGATIVE": 0}

                if result['label'] == 'POSITIVE':
                    user_sentiments[user_id]["POSITIVE"] += 1
                elif result['label'] == 'NEGATIVE':
                    user_sentiments[user_id]["NEGATIVE"] += 1

            for reply in post['replies']:
                if reply['sender_id'] in top_users:
                    text = reply['text']
                    result = classifier(text)[0]

                    user_id = reply['sender_id']
                    if user_id not in user_sentiments:
                        user_sentiments[user_id] = {"POSITIVE": 0, "NEGATIVE": 0}

                    if result['label'] == 'POSITIVE':
                        user_sentiments[user_id]["POSITIVE"] += 1
                    elif result['label'] == 'NEGATIVE':
                        user_sentiments[user_id]["NEGATIVE"] += 1

        loyalty_scores = {}

        for user_id, sentiment_info in user_sentiments.items():
            positive = sentiment_info['POSITIVE']
            negative = sentiment_info['NEGATIVE']

            loyalty_score = positive / (positive + negative) if (positive + negative) > 0 else 0
            loyalty_scores[user_id] = loyalty_score

        if len(loyalty_scores.values()) != 0:
            return sum(loyalty_scores.values()) / len(loyalty_scores.values())
        else:
            return 0
            
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
            return (channel_citation_sum / post_count) / 0.05
        else:
            return 0
        
    def calculate_model(self):
        '''
        Итоговые значения
        '''
        name_groups = ['Показатели вовлеченности аудитории', 'Метрики для оценивания обратной связи аудитории',
                       'Метрики эффективности коммуникаций бренда', 'Метрики для оценивания взаимодействия с инфлюенсерами',
                       'Метрики информационного присутствия бренда']
        groups = [
            [self.brand_follower_ratio, self.user_engagement_ratio, self.top_audience_ratio], # Показатели вовлеченности аудитории
            [self.love_rate, self.trending_content_sentiment_ratio, self.net_promoter_score], # Метрики для оценивания обратной связи аудитории
            [self.brand_response_to_comments, self.brand_reaction_to_negativity, self.brand_responsiveness], # Метрики эффективности коммуникаций бренда
            [self.influencer_sentiment_ratio], # Метрики для оценивания взаимодействия с инфлюенсерам
            [self.channel_citation_index] # Метрики информационного присутствия бренда
        ]

        group_sums = [sum(metric() for metric in group) for group in groups]
        average = sum(group_sums) / 11

        min_index = group_sums.index(min(group_sums))

        return average, name_groups[min_index] # average - итоговый рейтинг, название группы слабой группы 