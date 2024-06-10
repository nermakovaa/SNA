import emoji
from collections import Counter
from datetime import datetime, timedelta
# from transformers import pipeline

# 2
def audience_coverage(data):
    '''
    Показатель аудиторного охвата (Audience Coverage)
    (Уникальные пользователи (Количество лайков + количество просмотров + количество репостов + количестко комментариев + 
    количество лайков комментариев)) / (Количество дней рассматриваемого периода) 
    '''
    total_interactions = 0
    total_comments = 0
    total_views = 0

    for item in data:
        valid_posts = [post for post in item["posts"] if post["views"] is not None] 
        total_views += sum([post["views"] for post in valid_posts])
        
        likes_comments = sum([reaction['count'] for post in item['posts'] for comment in post.get('replies', []) for reaction in comment.get('reactions', [])])
        total_likes = sum(reaction['count'] for post in item['posts'] for reaction in post['reactions']) + likes_comments
        
        reposts = sum(post.get('forwards', 0) for post in item['posts'])  

        unique_sender_ids = set(comment['sender_id'] for post in item['posts'] for comment in post.get('replies', []))

        total_comments += len(unique_sender_ids)
        total_interactions += total_likes + total_comments + reposts + total_views
        
        start_date = datetime.strptime(item["from"], "%d/%m/%Y")
        end_date = datetime.strptime(item["to"], "%d/%m/%Y")
        days_between = (end_date - start_date).days
                
    if total_interactions > 0 and days_between > 0:
        audience_coverage = (total_interactions / days_between) 
        return int(audience_coverage)
    else:
        return 0
    
# 3
def channel_citation_index(data):
    """
    Индекс цитируемости (Channel Citation Index)
    (Количество репостов / Общее количество уникальных просмотров) * 100%
    """
    total_views = 0
    total_reposts = 0

    for item in data:
        valid_posts = [post for post in item["posts"] if post["views"] is not None] 
        total_views += sum([post["views"] for post in valid_posts])
        total_reposts = sum(post.get('forwards', 0) for post in item['posts'])  

    if total_views > 0 and total_reposts > 0:
        channel_citation_index = (total_reposts / total_views) * 100
        return channel_citation_index
    else:
        return 0
    
# 5    
def net_promoter_score(data):
    """
    Лояльность пользователей (Net Promoter Score)
    ((Положительные комментарии - Негативные комментарии) / Всего комментариев) * 100%
    """
    # https://huggingface.co/blanchefort/rubert-base-cased-sentiment модель для анализа тональности
    classifier = pipeline("sentiment-analysis", model="blanchefort/rubert-base-cased-sentiment") 

    for item in data:
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

# 6
def love_rate(data):
    """
    Коэффициент привлекательности (Love Rate)
    (Количество лайков / Общее количество уникальных просмотров) * 100%
    """
    total_views = 0
    total_likes = 0

    for j in data:
        valid_posts = [post for post in j["posts"] if post["views"] is not None] # только те посты, где просмотры != None
        total_views += sum([post["views"] for post in valid_posts])
        total_likes += sum([reaction["count"] for post in valid_posts for reaction in post["reactions"] if reaction["emoji"] == "like"])

    if total_views > 0 and total_likes > 0:
        love_rate = (total_likes / total_views) * 100
        return love_rate
    else:
        return 0    
    
# 7
def discussion_rate(data):
    """
    Обсуждаемость постов (Discussion Rate)
    (Количество подкомментариев / Количество уникальных пользователей в подкомментариях) * 100% 
    """

    result = []


    for item in data:
        start_date = datetime.strptime(item['from'], "%d/%m/%Y")
        end_date = datetime.strptime(item['to'], "%d/%m/%Y")
        days_interval_length = (end_date - start_date).days + 1
        delta_day = timedelta(days=1)

        for i in range(days_interval_length):
            cur_date = (start_date + i * delta_day).strftime("%d/%m/%Y")

            comments = [comment['sender_id'] for post in item['posts'] if (datetime.fromtimestamp(post['date']).strftime("%d/%m/%Y") == cur_date) for comment in post.get('replies', [])]

           
            
            total_comment = len(comments)
            unique_sender_ids = len(set(comments))
            
            
            if unique_sender_ids == 1:
                result.append({'name': cur_date, 'value': 1})
            else:
                discussion_rate = (total_comment / unique_sender_ids) # * 100 - слишком большое число??
                result.append({'name': cur_date, 'value': discussion_rate})

    return result            

# 10
def character_length(data):
    '''
    Распределение тональности комментариев по длине символов
    [количество символов | тональность]
    '''
    lists = []
    results = []
    
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

    for group in data:
        for post in group['posts']:
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

# 11
def top_emoji(data):
    '''
    Топ-5 эмодзи
    [эмодзи | количество упоминаний эмодзи в комментариях]
    '''
    def extract_emojis(text):
        return ''.join(c for c in text if emoji.is_emoji(c))

    emoji_counter = Counter()

    for group in data:
        messages = (reply['text'] for post in group['posts'] 
                    for reply in post['replies'] if reply['text'] is not None)
        
        for message in messages:
            emojis = extract_emojis(message)
            emoji_counter.update(emojis)

    top_emojis = dict(emoji_counter.most_common(5))       
    return top_emojis  