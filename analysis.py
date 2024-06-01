from transformers import pipeline
from collections import Counter
from datetime import datetime
import networkx as nx
import matplotlib.pyplot as plt
import json
import emoji


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
        
    def engagement_rate_by_reach(self):
        '''
        Коэффициент вовлеченности (Engagement Rate By Reach)
        (Общее число взаимодействий / Общее количество уникальных просмотров) * 100%
        '''
        total_interactions = 0
        total_comments = 0
        total_views = 0

        for i in self.data:
            for item in i['tg']:
                total_views += sum([0 if _["views"] is None else _["views"] for _ in item["posts"]])
                
                likes = sum(reaction['count'] for post in item['posts'] for reaction in post['reactions'])
                reposts = sum(post.get('forwards', 0) for post in item['posts'])  

                unique_sender_ids = set(comment['sender_id'] for post in item['posts'] for comment in post.get('replies', []))

                total_comments += len(unique_sender_ids)
                total_interactions += likes + total_comments + reposts

        if total_interactions > 0 and total_views > 0:
            engagement_rate_by_reach = (total_interactions / total_views) * 100
            return engagement_rate_by_reach
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
    
    def net_promoter_score(self):
        """
        Лояльность пользователей (Net Promoter Score)
        ((Положительные комментарии - Негативные комментарии) / Всего комментариев) * 100%
        """
        classifier = pipeline("sentiment-analysis", model="blanchefort/rubert-base-cased-sentiment") 

        for i in self.data:
            for item in i['tg']:
                total_messages = [post['text'] for post in item['posts'] for post in post['replies'] if post['text'] is not None]
                print(total_messages)
                len_total_messages = len(total_messages)
                
                classified_messages = classifier(total_messages)
                positive_count = sum(1 for i in classified_messages if i['label'] == 'POSITIVE')
                negative_count = sum(1 for i in classified_messages if i['label'] == 'NEGATIVE')

        if len_total_messages > 0:
            net_promoter_score = ((positive_count - negative_count) / len_total_messages) * 100
            return net_promoter_score
        else:
            return 0
        
    def character_length(self):
        '''
        Распределение тональности комментариев по длине символов
        [количество символов | тональность]
        '''
        lists = []
        results = []
        
        # https://huggingface.co/blanchefort/rubert-base-cased-sentiment модель для анализа тональности
        classifier = pipeline("sentiment-analysis", model="blanchefort/rubert-base-cased-sentiment") 
        
        # диапазоны длин символов
        dict_lengths = {1: '0-10', 2: '11-50', 3: '51-100', 4: '101-200', 5: '201+'}

        comments_lengths = {
            dict_lengths[1]: [],
            dict_lengths[2]: [],
            dict_lengths[3]: [],
            dict_lengths[4]: [],
            dict_lengths[5]: [] 
        }

        for group in self.data:
            for post in group['tg'][0]['posts']:
                for reply in post['replies']:
                    if reply['text'] != None:
                        comment_length = len(reply['text'])
                        if comment_length < int(dict_lengths[1].split('-')[1])+1:
                            comments_lengths[dict_lengths[1]].append(reply['text'])
                        elif int(dict_lengths[1].split('-')[1])+1 <= comment_length <= int(dict_lengths[2].split('-')[1])+1:
                            comments_lengths[dict_lengths[2]].append(reply['text'])
                        elif int(dict_lengths[2].split('-')[1])+1 <= comment_length <= int(dict_lengths[3].split('-')[1])+1:
                            comments_lengths[dict_lengths[3]].append(reply['text'])
                        elif int(dict_lengths[3].split('-')[1])+1 <= comment_length <= int(dict_lengths[4].split('-')[1])+1:
                            comments_lengths[dict_lengths[4]].append(reply['text'])
                        else:
                            comments_lengths[dict_lengths[5]].append(reply['text'])

        for lengths in comments_lengths.keys():
            lists.append([classifier(_) for _ in comments_lengths[lengths]])
            
        length_keys = dict_lengths.values()

        for list in lists:
            total_score = sum(dict['score'] for sublist in list for dict in sublist)

            distribution = {'positive': 0, 'negative': 0, 'neutral': 0} 
            if total_score != 0:
                for sublist in list:
                    for dict in sublist:
                        distribution[dict['label'].lower()] += (dict['score'] / total_score) * 100

            results.append(distribution)

        comments_lengths_sentimentary = {}
        for i, dist in zip(length_keys, results):
            comments_lengths_sentimentary[i] = dist

        return comments_lengths_sentimentary  
    
    def top_emoji(self):
        '''
        Топ-5 эмодзи
        [эмодзи | количество упоминаний эмодзи]
        '''
        reactions_summary = {}
        
        for group in self.data:
            posts = (post_item for item in group['tg'] for post_item in item['posts'])
            
            for post_item in posts:
                reactions = post_item.get('reactions', {})
                
                if reactions is not None:
                    for reaction in filter(lambda r: r['emoji'] is not None, reactions):
                        emoji = reaction['emoji']
                        count = reaction['count']
                        
                        reactions_summary[emoji] = reactions_summary.get(emoji, 0) + count

        top_reactions = dict(sorted(reactions_summary.items(), key=lambda x: x[1], reverse=True)[:5])
        return top_reactions  
    

class Vkontakte:
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
    
    def net_promoter_score(self):
        """
        Лояльность пользователей (Net Promoter Score)
        ((Положительные комментарии - Негативные комментарии) / Всего комментариев) * 100%
        """
        # https://huggingface.co/blanchefort/rubert-base-cased-sentiment модель для анализа тональности
        classifier = pipeline("sentiment-analysis", model="blanchefort/rubert-base-cased-sentiment") 

        for i in self.data:
            for item in i['vk']:
                total_messages = [post['text'] for post in item['posts'] for post in post['replies'] if post['text'] is not None]
                len_total_messages = len(total_messages)
                
                classified_messages = classifier(total_messages)
                positive_count = sum(1 for i in classified_messages if i['label'] == 'POSITIVE')
                negative_count = sum(1 for i in classified_messages if i['label'] == 'NEGATIVE')

        if len_total_messages > 0:
            net_promoter_score = ((positive_count - negative_count) / len_total_messages) * 100
            return net_promoter_score
        else:
            return 0
        
    def character_length(self):
        '''
        Распределение тональности комментариев по длине символов
        [количество символов | тональность]
        '''
        lists = []
        results = []
        
        # https://huggingface.co/blanchefort/rubert-base-cased-sentiment модель для анализа тональности
        classifier = pipeline("sentiment-analysis", model="blanchefort/rubert-base-cased-sentiment") 
        
        # диапазоны длин символов
        dict_lengths = {1: '0-10', 2: '11-50', 3: '51-100', 4: '101-200', 5: '201+'}

        comments_lengths = {
            dict_lengths[1]: [],
            dict_lengths[2]: [],
            dict_lengths[3]: [],
            dict_lengths[4]: [],
            dict_lengths[5]: [] 
        }

        for group in self.data:
            for post in group['vk'][0]['posts']:
                for reply in post['replies']:
                    if reply['text'] != None:
                        comment_length = len(reply['text'])
                        if comment_length < int(dict_lengths[1].split('-')[1])+1:
                            comments_lengths[dict_lengths[1]].append(reply['text'])
                        elif int(dict_lengths[1].split('-')[1])+1 <= comment_length <= int(dict_lengths[2].split('-')[1])+1:
                            comments_lengths[dict_lengths[2]].append(reply['text'])
                        elif int(dict_lengths[2].split('-')[1])+1 <= comment_length <= int(dict_lengths[3].split('-')[1])+1:
                            comments_lengths[dict_lengths[3]].append(reply['text'])
                        elif int(dict_lengths[3].split('-')[1])+1 <= comment_length <= int(dict_lengths[4].split('-')[1])+1:
                            comments_lengths[dict_lengths[4]].append(reply['text'])
                        else:
                            comments_lengths[dict_lengths[5]].append(reply['text'])

        for lengths in comments_lengths.keys():
            lists.append([classifier(_) for _ in comments_lengths[lengths]])
            
        length_keys = dict_lengths.values()

        for list in lists:
            total_score = sum(dict['score'] for sublist in list for dict in sublist)

            distribution = {'positive': 0, 'negative': 0, 'neutral': 0} 
            if total_score != 0:
                for sublist in list:
                    for dict in sublist:
                        distribution[dict['label'].lower()] += (dict['score'] / total_score) * 100

            results.append(distribution)

        comments_lengths_sentimentary = {}
        for i, dist in zip(length_keys, results):
            comments_lengths_sentimentary[i] = dist

        return comments_lengths_sentimentary

    def top_emoji(self):
        '''
        Топ-5 эмодзи
        [эмодзи | количество упоминаний эмодзи в комментариях]
        '''
        def extract_emojis(text):
            return ''.join(c for c in text if emoji.is_emoji(c))

        emoji_counter = Counter()

        for group in self.data:
            for item in group['vk']:

                messages = (reply['text'] for post in item['posts'] 
                            for reply in post['replies'] if reply['text'] is not None)
                
                for message in messages:
                    emojis = extract_emojis(message)
                    emoji_counter.update(emojis)

        top_emojis = dict(emoji_counter.most_common(5))       
        return top_emojis  
    

class General():  
    def __init__(self, data):
        self.data = data
      
    def page_rank(sender_id, data, connections):
        '''
        Топ-10 авторов с наибольшей способностью вовлекать других пользователей в дискуссию
        [пользователь | значение pagerank]
        
        sender_id - nodes (id) example [108718, 108719, 108720, 108721, ]
        data - (id: {first_name: , last_name: }) example {108718: {'first_name': 'Richard', 'last_name': 'Lowe'}, }
        connections - edges (one-to-one = id-to-id) example [(108990, 108928), (108916, 108760), ]
        '''
        G = nx.DiGraph()
        [G.add_node(k, first_name = data[k]['first_name'], last_name = data[k]['last_name']) for k in sender_id]
        G.add_edges_from(connections)
        # spring_layout - https://networkx.org/documentation/stable/reference/generated/networkx.drawing.layout.spring_layout.html
        pos = nx.spring_layout(G, k=0.15, iterations=20) 

        # pagerank - https://networkx.org/documentation/stable/reference/algorithms/generated/networkx.algorithms.link_analysis.pagerank_alg.pagerank.html
        pr = nx.pagerank(G)
        sorted_pr = sorted(pr.items(), key=lambda x: x[1], reverse=True)

        top_10 = sorted_pr[:10] 
        top_10_ids = [id for id, pr in top_10]
        # топ 10 пользователей с наибольшим pagerank
        top_nodes = {node: G.nodes[node]['first_name'] + ' ' + G.nodes[node]['last_name'] for node in dict(top_10).keys()} 

        # для графа
        node_colors = ['#FF5558' if node in top_10_ids else "#27BBBD" for node in G.nodes()]
        plt.figure(figsize = (10, 10)) 
        nx.draw_networkx_labels(G, pos, 
                                labels = top_nodes, 
                                font_color = '#333335', 
                                font_size = 10, 
                                bbox = dict(facecolor='white', edgecolor='white', boxstyle='square'))
        nx.draw(G, pos, 
                nodelist = list(pr.keys()), 
                node_size = [v * 100000 for v in pr.values()], 
                with_labels = False, 
                node_color = node_colors, 
                edge_color = '#27BBBD', 
                width = 0.2)
        plt.show()

        # для таблицы "Top 20 influencers by PageRank"
        name_surname_dict = {data[k]['first_name'] + ' ' + data[k]['last_name']: round(v, 5) for k, v in top_10}
        # print(name_surname_dict)
        
    def betweenness_centrality_rank(sender_id, example_data, connections):
        '''
        Топ-10 авторов с наибольшей способностью связывать подсети других пользователей в графе
        [пользователь | значение betweenness centrality rank]
        
        sender_id - узлы (id пользователей)
        example_data - (словарь с id в качестве ключа и значений в качестве словаря из first_name и last_name)
        connections - ребра (one-to-one = id-to-id)
        '''
        G = nx.DiGraph()
        [G.add_node(k, first_name = example_data[k]['first_name'], last_name = example_data[k]['last_name']) for k in sender_id]
        G.add_edges_from(connections)
        # spring_layout - https://networkx.org/documentation/stable/reference/generated/networkx.drawing.layout.spring_layout.html
        pos = nx.spring_layout(G, k=0.15, iterations=20)

        # https://networkx.org/documentation/stable/reference/algorithms/generated/networkx.algorithms.centrality.betweenness_centrality.html
        centrality = nx.betweenness_centrality(G)
        sorted_centrality = sorted(centrality.items(), key=lambda x: x[1], reverse=True)

        # топ 10 пользователей с наибольшим pagerank
        top_10 = sorted_centrality[:10] 
        top_10_ids = [id for id, _ in top_10]
        top_nodes = {node: G.nodes[node]['first_name'] + ' ' + G.nodes[node]['last_name'] for node in dict(top_10).keys()} 

        # для графа
        node_colors = ['#FF5558' if node in top_10_ids else '#27BBBD' for node in G.nodes()]
        plt.figure(figsize = (10, 10)) 
        nx.draw_networkx_labels(G, pos, 
                                labels = top_nodes, 
                                font_color = '#333335', 
                                font_size = 10, 
                                bbox = dict(facecolor='white', edgecolor='white', boxstyle='square'))
        nx.draw(G, pos, 
                nodelist = list(centrality.keys()), 
                node_size = [v * 300000 for v in centrality.values()], 
                with_labels = False, 
                node_color = node_colors, 
                edge_color = '#27BBBD', 
                width = 0.2)
        plt.show()

        # для таблицы "Top 20 influencers by Betweenness Centrality Rank"
        name_surname_dict = {example_data[k]['first_name'] + ' ' + example_data[k]['last_name']: round(v, 5) for k, v in top_10}
        # print(name_surname_dict)