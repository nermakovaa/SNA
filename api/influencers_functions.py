from transformers import pipeline
import networkx as nx

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
        result = []
        
        names = self.get_name()
        engagement_rate = self.engagement_rate_by_reach()
        nps = self.net_promoter_score()
        
        nps_dict = {name: rating for name, rating in nps}
        
        for name, messages in names.items():
            result.append({
                "name": name,
                "value": messages,
                "involvement":  round(engagement_rate.get(name, 0) * 10)/10,
                'loyality': round(nps_dict.get(name, 0) * 10)/10
            })
        
        return result # {'Галина Погорельченко': {'get_message': 10,  'engagement_rate_by_reach': 4.31,  'net_promoter_score': 65.0}, 'Евгения Санникова': ...}
    
def most_messages_users(data):
     influencers = InfluencerTable(data)
     res = influencers.influencer_table_result()

     print(res)

     return res


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
        
        results = []
        
        for id, info in self.neg_posts:
            results.append({
                "name": info['first_name'] + ' ' + info['last_name'],
                "text": info['post'],
                "value": round(info['engagement_rate']*1000)/10,
                "positive": round(info['positive_percentage']),
                "neutral": round(info['neutral_percentage']),
                "negative": round(info['negative_percentage']),
            })
        
        # # {'Друзья, будьте осторожны...',  {'first_name': 'Наталия Милано', 'negative': 100.0,  
        # 'neutral': 0.0,  'positive': 0.0,  'engagement_rate': 0.01790601898038012}, 'Вот такие стрипсы, одни обрезки': {'first...   
        return results 

def high_negative_reactions(data):
    negative_influencers = InfluencerTableNegative(data)

    return negative_influencers.get_results_dict()

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
        # plt.figure(figsize=(10, 10))
        # nx.draw_networkx_labels(G, pos,
        #                         labels=top_nodes,
        #                         font_color='#333335',
        #                         font_size=10,
        #                         bbox=dict(facecolor='white', edgecolor='white', boxstyle='square'))
        # nx.draw(G, pos,
        #         nodelist=list(pr.keys()),
        #         node_size=[v * 20000 for v in pr.values()],
        #         with_labels=False,
        #         node_color=node_colors,
        #         edge_color='#27BBBD',
        #         width=0.2)
        
        # current_dir = os.getcwd()
        # file_path = os.path.join(current_dir, 'data/PageRank.png')
        # plt.savefig(file_path) 
        # plt.close()  
        
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
    
def top_pagerank_influencers(data):
    influencers = PageRank(data)    
    return influencers.get_table()

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

    def page_rank(self):
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
        # plt.figure(figsize=(15, 15))
        # nx.draw_networkx_labels(G, pos,
        #                         labels=top_nodes,
        #                         font_color='#333335',
        #                         font_size=10,
        #                         bbox=dict(facecolor='white', edgecolor='white', boxstyle='square'))
        # nx.draw(G, pos,
        #         nodelist=list(centrality.keys()),
        #         node_size=[v * 20000 for v in centrality.values()],
        #         with_labels=False,
        #         node_color=node_colors,
        #         edge_color='#27BBBD',
        #         width=0.2)
        
        # current_dir = os.getcwd()
        # file_path = os.path.join(current_dir, 'data/BetweennessCentralityRank.png')
        # plt.savefig(file_path) 
        # plt.close()      
    
    def get_table(self):
        '''
        Данные для таблицы топ-инфлюенсеров BetweennessCentralityRank
        '''
        result_dict = {}
        for k, v in self.page_rank().items():
            name = self.sender_info[k]['first_name'] + ' ' + self.sender_info[k]['last_name']
            result_dict[name] = {
                'bc_rank': self.page_rank()[k],
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
        
        return result_dict # {'Татьяна Балакирева': {'bc_rank': 0.07433, 'id': 588079193,  'engagement_users': 81,  'positive': 73.33333333333333,  'negative': 8.88888888888889,  'neutral': 17.77777777777778},
    
def top_bcr_rank_influencers(data):
    influencers = BetweennessCentralityRank(data)    
    return influencers.get_table()