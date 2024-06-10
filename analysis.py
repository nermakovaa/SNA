from transformers import pipeline
from collections import Counter
from datetime import datetime
import networkx as nx
import matplotlib.pyplot as plt
import json
import emoji
import os


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
            for item in i['vk']:
                total_messages = [post['text'] for post in item['posts'] for post in post['replies'] if post['text'] is not None]
                # print(total_messages)
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
    

class PageRank:
    '''
    Топ-10 авторов с наибольшей способностью вовлекать других пользователей в дискуссию
    [пользователь | значение page rank]
    '''
    def __init__(self, data, top_authors=10):
        self.data = data
        self.top_authors = top_authors
        self.sender_id, self.sender_info, self.connections = self.__get_data()
        self.__get_file()
        
    def __get_data(self):
        '''
        sender_id - узлы (id пользователей)
        sender_info - (словарь с id в качестве ключа и значений в качестве словаря из first_name и last_name)
        connections - ребра (id-to-id)
        '''
        connections = []

        for post in self.data['vk'][0]['posts']:
            if post['from'] != None:
                post_connections = [(post['from']['id'], reply['sender_id']) for reply in post['replies']]
                connections.extend(post_connections)

        sender_id = list(set(sum(connections, ())))

        sender_info = {}

        for post in self.data['vk'][0]['posts']:
            if post['from'] is not None and post['from']['id'] in sender_id:
                if post['from']['id'] not in sender_info:
                    sender_info[post['from']['id']] = {
                        'first_name': post['from']['first_name'],
                        'last_name': post['from']['last_name']
                    }

        for post in self.data['vk'][0]['posts']:
            if 'replies' in post:
                for reply in post['replies']:
                    if reply['sender_id'] in sender_id:
                        if reply['sender_id'] not in sender_info:
                            sender_info[reply['sender_id']] = {
                                'first_name': reply['sender_name'],
                                'last_name': reply['last_name']
                            }

        return sender_id, sender_info, connections

    def page_rank(self):
        '''
        Для получения топа пользователей pagerank {722219350: 0.04746, 732871646: 0.03822 ...}
        '''
        G = nx.DiGraph()
        [G.add_node(k, first_name = self.sender_info[k]['first_name'], last_name = self.sender_info[k]['last_name']) for k in self.sender_id]
        G.add_edges_from(self.connections)
        pos = nx.spring_layout(G, k=0.15, iterations=20) 
        
        # pagerank - https://networkx.org/documentation/stable/reference/algorithms/generated/networkx.algorithms.link_analysis.pagerank_alg.pagerank.html
        pr = nx.pagerank(G)
        sorted_pr = sorted(pr.items(), key=lambda x: x[1], reverse=True)

        top_pr = sorted_pr[:self.top_authors] 
        
        # топ 10 пользователей с наибольшим pagerank
        name_surname_dict = {k: round(v, 5) for k, v in top_pr}
        
        return name_surname_dict # возвращает id и значение pagerank {722219350: 0.04746, 732871646: 0.03822 ...}
    
    def __get_file(self):
        '''
        Для сохранения файла pagerank
        '''
        # spring_layout - https://networkx.org/documentation/stable/reference/generated/networkx.drawing.layout.spring_layout.html
        G = nx.DiGraph()
        [G.add_node(k, first_name=self.sender_info[k]['first_name'], last_name=self.sender_info[k]['last_name']) for k in self.sender_id]
        G.add_edges_from(self.connections)
        pos = nx.spring_layout(G, k=0.15, iterations=20)

        pr = nx.pagerank(G)
        sorted_pr = sorted(pr.items(), key=lambda x: x[1], reverse=True)
        top_pr = sorted_pr[:self.top_authors]
        top_ids = [id for id, pr in top_pr]
        top_nodes = {node: G.nodes[node]['first_name'] + ' ' + G.nodes[node]['last_name'] for node in dict(top_pr).keys()}

        node_colors = ['#FF5558' if node in top_ids else "#27BBBD" for node in G.nodes()]
        plt.figure(figsize=(10, 10))
        nx.draw_networkx_labels(G, pos,
                                labels=top_nodes,
                                font_color='#333335',
                                font_size=10,
                                bbox=dict(facecolor='white', edgecolor='white', boxstyle='square'))
        nx.draw(G, pos,
                nodelist=list(pr.keys()),
                node_size=[v * 20000 for v in pr.values()],
                with_labels=False,
                node_color=node_colors,
                edge_color='#27BBBD',
                width=0.2)
        
        current_dir = os.getcwd()
        file_path = os.path.join(current_dir, 'data/PageRank.png')
        plt.savefig(file_path) 
        plt.close()  
        
    def get_table(self):
        '''
        Данные для таблицы топ-инфлюенсеров
        '''
        result_dict = {}
        for k, v in self.page_rank().items():
            name = self.sender_info[k]['first_name'] + ' ' + self.sender_info[k]['last_name']
            result_dict[name] = {
                'page_rank': self.page_rank()[k],
                'id': k
            }

        for key, value in result_dict.items():
            id_to_find = value['id']
            count = 0
            for tpl in self.connections:
                if id_to_find in tpl:
                    count += 1
            value['engagement_users'] = count
        
        for key, value in result_dict.items():
            value['comments'] = []  # создаем пустой список для комментариев
            
        id = [value['id'] for key, value in result_dict.items()]

        for post in self.data['vk'][0]['posts']:
            for replies in post['replies']:
                for key, value in result_dict.items():
                    if replies['sender_id'] == value['id']:
                        value['comments'].append(replies['text'])
                        
        classifier = pipeline("sentiment-analysis", model="blanchefort/rubert-base-cased-sentiment")
        
        for key, value in result_dict.items():
            pos_count = 0
            neg_count = 0
            comments = value['comments']

            for comment in comments:
                sentiment = classifier(comment)
                if sentiment[0]['label'] == 'POSITIVE':
                    pos_count += 1
                else:
                    neg_count += 1

            if (pos_count + neg_count) != 0:
                nps = (pos_count / (pos_count + neg_count)) * 100 # nps = лояльность
                value['net_promoter_score'] = nps
            else:
                0     
                                    
        for key in result_dict:
            if 'comments' in result_dict[key]:
                del result_dict[key]['comments']
        
        return result_dict # {'Марина Вкусвилл': {'page_rank': 0.04746,  'id': 722219350,  'engagement_users': 28,  'net_promoter_score': 82.14285714285714},


class BetweennessCentralityRank:
    '''
    Топ-10 авторов с наибольшей способностью вовлекать других пользователей в дискуссию
    [пользователь | значение page rank]
    '''
    def __init__(self, data, top_authors=10):
        self.data = data
        self.top_authors = top_authors
        self.sender_id, self.sender_info, self.connections = self.__get_data()
        self.__get_file()
        
    def __get_data(self):
        '''
        sender_id - узлы (id пользователей)
        sender_info - (словарь с id в качестве ключа и значений в качестве словаря из first_name и last_name)
        connections - ребра (id-to-id)
        '''
        connections = []

        for post in self.data['vk'][0]['posts']:
            if post['from'] != None:
                post_connections = [(post['from']['id'], reply['sender_id']) for reply in post['replies']]
                connections.extend(post_connections)

        sender_id = list(set(sum(connections, ())))

        sender_info = {}

        for post in self.data['vk'][0]['posts']:
            if post['from'] is not None and post['from']['id'] in sender_id:
                if post['from']['id'] not in sender_info:
                    sender_info[post['from']['id']] = {
                        'first_name': post['from']['first_name'],
                        'last_name': post['from']['last_name']
                    }

        for post in self.data['vk'][0]['posts']:
            if 'replies' in post:
                for reply in post['replies']:
                    if reply['sender_id'] in sender_id:
                        if reply['sender_id'] not in sender_info:
                            sender_info[reply['sender_id']] = {
                                'first_name': reply['sender_name'],
                                'last_name': reply['last_name']
                            }

        return sender_id, sender_info, connections

    def betweenness_centrality(self):
        '''
        Для получения топа пользователей betweenness_centrality_rank {722219350: 0.04746, 732871646: 0.03822 ...}
        '''
        G = nx.DiGraph()
        [G.add_node(k, first_name = self.sender_info[k]['first_name'], last_name = self.sender_info[k]['last_name']) for k in self.sender_id]
        G.add_edges_from(self.connections)
        pos = nx.spring_layout(G, k=0.15, iterations=20) 
        
        # pagerank - https://networkx.org/documentation/stable/reference/algorithms/generated/networkx.algorithms.link_analysis.pagerank_alg.pagerank.html
        centrality = nx.betweenness_centrality(G)
        sorted_centrality = sorted(centrality.items(), key=lambda x: x[1], reverse=True)

        top_centrality = sorted_centrality[:self.top_authors] 
        
        # топ 10 пользователей с наибольшим pagerank
        name_surname_dict = {k: round(v, 5) for k, v in top_centrality}
        
        return name_surname_dict # возвращает id и значение pagerank {722219350: 0.04746, 732871646: 0.03822 ...}    
    
    def __get_file(self):
        '''
        Для сохранения файла pagerank
        '''
        # spring_layout - https://networkx.org/documentation/stable/reference/generated/networkx.drawing.layout.spring_layout.html
        G = nx.DiGraph()
        [G.add_node(k, first_name=self.sender_info[k]['first_name'], last_name=self.sender_info[k]['last_name']) for k in self.sender_id]
        G.add_edges_from(self.connections)
        pos = nx.spring_layout(G, k=0.15, iterations=20)

        centrality = nx.betweenness_centrality(G)
        sorted_centrality = sorted(centrality.items(), key=lambda x: x[1], reverse=True)
        top_centrality = sorted_centrality[:self.top_authors] 
        top_ids = [id for id, pr in top_centrality]
        top_nodes = {node: G.nodes[node]['first_name'] + ' ' + G.nodes[node]['last_name'] for node in dict(top_centrality).keys()}

        node_colors = ['#FF5558' if node in top_ids else '#27BBBD' for node in G.nodes()]
        plt.figure(figsize=(15, 15))
        nx.draw_networkx_labels(G, pos,
                                labels=top_nodes,
                                font_color='#333335',
                                font_size=10,
                                bbox=dict(facecolor='white', edgecolor='white', boxstyle='square'))
        nx.draw(G, pos,
                nodelist=list(centrality.keys()),
                node_size=[v * 20000 for v in centrality.values()],
                with_labels=False,
                node_color=node_colors,
                edge_color='#27BBBD',
                width=0.2)
        
        current_dir = os.getcwd()
        file_path = os.path.join(current_dir, 'data/BetweennessCentralityRank.png')
        plt.savefig(file_path) 
        plt.close()      
    
    def get_table(self):
        '''
        Данные для таблицы топ-инфлюенсеров BetweennessCentralityRank
        '''
        result_dict = {}
        for k, v in self.betweenness_centrality().items():
            name = self.sender_info[k]['first_name'] + ' ' + self.sender_info[k]['last_name']
            result_dict[name] = {
                'betweenness_centrality': self.betweenness_centrality()[k],
                'id': k
            }

        for key, value in result_dict.items():
            id_to_find = value['id']
            count = 0
            for tpl in self.connections:
                if id_to_find in tpl:
                    count += 1
            value['engagement_users'] = count
        
        for key, value in result_dict.items():
            value['comments'] = []  

        for post in self.data['vk'][0]['posts']:
            for replies in post['replies']:
                for key, value in result_dict.items():
                    if replies['sender_id'] == value['id']:
                        value['comments'].append(replies['text'])
                        
        classifier = pipeline("sentiment-analysis", model="blanchefort/rubert-base-cased-sentiment")
        
        for key, value in result_dict.items():
            comments = value['comments']
            
            pos_count = 0
            neg_count = 0
            neu_count = 0

            for comment in comments:
                sentiment = classifier(comment)
                label = sentiment[0]['label']

                if label == 'POSITIVE':
                    pos_count += 1
                elif label == 'NEGATIVE':
                    neg_count += 1
                else:
                    neu_count += 1
            
            total_count = pos_count + neg_count + neu_count
            value['positive'] = pos_count / total_count * 100
            value['negative'] = neg_count / total_count * 100
            value['neutral'] = neu_count / total_count * 100
            
        for key in result_dict:
            if 'comments' in result_dict[key]:
                del result_dict[key]['comments']
        
        return result_dict # {'Татьяна Балакирева': {'page_rank': 0.07433, 'id': 588079193,  'engagement_users': 81,  'positive': 73.33333333333333,  'negative': 8.88888888888889,  'neutral': 17.77777777777778},
    
        
class InfluencerTable:
    '''
    Топ-5 авторов с наибольшим числом сообщений
    [пользователь | постов в группе | вовлеченность | лояльность]
    '''
    def __init__(self, data, person=5):
        self.data = data
        self.person = person
        
    def __get_data(self):
        dt = {}  

        for post in self.data['vk'][0]['posts']:
            if post['from'] is not None:
                post_id = post['from']['id']
                if post_id not in dt:
                    dt[post_id] = {
                        'first_name': post['from']['first_name'],
                        'last_name': post['from']['last_name'],
                        'likes': post['reactions'][0]['count'],
                        'messages': 1,
                        'comments': [reply['text'] for reply in post['replies']],
                        'reposts': post['forwards'],
                        'followers': self.data['vk'][0]['membersCount']
                    }
                else:  
                    dt[post_id]['messages'] += 1
                    dt[post_id]['likes'] += post['reactions'][0]['count']
                    dt[post_id]['reposts'] += post['forwards']
                    dt[post_id]['comments'].extend([reply['text'] for reply in post['replies']])
                
        return dt
            
    def get_name(self):
        '''
        ФИО пользователей с наибольшим числом инициированных постов
        '''
        self.data = self.__get_data()
        sorted_data = sorted(self.data.values(), key=lambda x: x['messages'], reverse=True)
        authors_names = {v['first_name'] + ' ' + v['last_name']: v['messages'] for v in sorted_data[:self.person]}
        return authors_names # словарь {'first_name last_name': messages}, где messages - количество постов, инициированных данным пользователем
    
    def engagement_rate_by_reach(self):
        '''
        Коэффициент вовлеченности (Engagement Rate By Reach)
        (Общее число взаимодействий / Общее количество подписчиков сообщества) * 100%
        '''
        sorted_data = sorted(self.data.values(), key=lambda x: x['messages'], reverse=True)

        engagement_rates = {
            v['first_name'] + ' ' + v['last_name']: round(((v['likes'] + v['reposts'] + len(v['comments'])) / v['followers']) * 1000, 3) 
            for v in sorted_data[:self.person] if v['followers'] != 0
        }
        return engagement_rates # словарь {'first_name last_name': engagement_rate_by_reach}, engagement_rate_by_reach - вовлеченность
    
    def net_promoter_score(self):
        """
        Лояльность пользователей (Net Promoter Score)
        ((Положительные комментарии - Негативные комментарии) / Всего комментариев) * 100%
        """
        classifier = pipeline("sentiment-analysis", model="blanchefort/rubert-base-cased-sentiment") 
        
        top_users = sorted(self.data.values(), key=lambda x: x['messages'], reverse=True)[:self.person]
        loyalty_scores = []
        
        for user in top_users:
            positive_count = 0
            negative_count = 0
            
            for comment in user['comments']:
                classified_comment = classifier(comment)
                if classified_comment[0]['label'] == 'POSITIVE':
                    positive_count += 1
                elif classified_comment[0]['label'] == 'NEGATIVE':
                    negative_count += 1
            
            total_comments = len(user['comments'])
            if total_comments > 0:
                loyalty_score = ((positive_count - negative_count) / total_comments) * 100
                loyalty_scores.append((user['first_name'] + ' ' + user['last_name'], round(loyalty_score, 2)))
        
        return sorted(loyalty_scores, key=lambda x: x[1], reverse=True) # словарь {'first_name last_name': net_promoter_score}, net_promoter_score - лояльность

    def influencer_table_result(self):
        '''
        Топ-5 авторов с наибольшим числом сообщений
        '''
        data_dict = {}
        
        names = self.get_name()
        engagement_rate = self.engagement_rate_by_reach()
        nps = self.net_promoter_score()
        
        nps_dict = {name: rating for name, rating in nps}
        
        for name, messages in names.items():
            data_dict[name] = {
                'get_message': messages,
                'engagement_rate_by_reach': engagement_rate.get(name, 0),
                'net_promoter_score': nps_dict.get(name, 0)
            }
        
        return data_dict # {'Галина Погорельченко': {'get_message': 10,  'engagement_rate_by_reach': 4.31,  'net_promoter_score': 65.0}, 'Евгения Санникова': ...}
    
        
class InfluencerTableNegative:
    '''
    Топ-10 постов с высоким уровнем негативной реакции аудитории
    [пост | инфлюенсер | негатив | нейтрально | позитив | вовлеченность]
    '''
    def __init__(self, data, top_neg_posts=10):
        self.data = data
        self.top_neg_posts = top_neg_posts
        self.__analyze_comments()
        self.__engagement_rate_by_reach()

    def __get_data(self):
        dt = {}  

        for post in self.data['vk'][0]['posts']:
            if post['from'] is not None:
                post_id = post['id']
                if post_id not in dt:
                    dt[post_id] = {
                        'first_name': post['from']['first_name'],
                        'last_name': post['from']['last_name'],
                        'likes': post['reactions'][0]['count'],
                        'messages': 1,
                        'comments': [reply['text'] for reply in post['replies']],
                        'reposts': post['forwards'],
                        'followers': self.data['vk'][0]['membersCount'],
                        'post': post['text']
                    }
                    
        return dt

    def __analyze_comments(self):
        self.data = self.__get_data()
        
        classifier = pipeline("sentiment-analysis", model="blanchefort/rubert-base-cased-sentiment")
        
        for id, info in self.data.items():
            pos_count = 0
            neg_count = 0
            neu_count = 0
            total_count = 0
            
            for comment in info['comments']:
                result = classifier(comment)
                sentiment = result[0]['label']
                
                if sentiment == 'NEGATIVE':
                    neg_count += 1
                elif sentiment == 'POSITIVE':
                    pos_count += 1
                else:
                    neu_count += 1
                
                total_count += 1

            pos_perc = (pos_count / total_count) * 100
            neg_perc = (neg_count / total_count) * 100
            neu_perc = (neu_count / total_count) * 100

            info['positive_percentage'] = pos_perc
            info['negative_percentage'] = neg_perc
            info['neutral_percentage'] = neu_perc

        sorted_data = sorted(self.data.items(), key=lambda x: x[1]['negative_percentage'], reverse=True)
        self.neg_posts = sorted_data[:self.top_neg_posts]
    
    def __engagement_rate_by_reach(self):
        '''
        Коэффициент вовлеченности (Engagement Rate By Reach)
        (Общее число взаимодействий / Общее количество подписчиков сообщества) * 100%
        '''
        for id, info in self.neg_posts:
            total_interactions = info['likes'] + len(info['comments']) + info['reposts']
            engagement_rate = (total_interactions / info['followers']) * 100
            info['engagement_rate'] = engagement_rate
    
    def get_results_dict(self):
        
        results_dict = {}
        
        for id, info in self.neg_posts:
            results_dict[info['post']] = {
                'first_name': info['first_name'] + ' ' + info['last_name'],
                'negative': info['negative_percentage'],
                'neutral': info['neutral_percentage'],
                'positive': info['positive_percentage'],
                'engagement_rate': info['engagement_rate']
            }
        
        # # {'Друзья, будьте осторожны...',  {'first_name': 'Наталия Милано', 'negative': 100.0,  
        # 'neutral': 0.0,  'positive': 0.0,  'engagement_rate': 0.01790601898038012}, 'Вот такие стрипсы, одни обрезки': {'first...   
        return results_dict 