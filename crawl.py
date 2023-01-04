import csv
import os
import time

import GetOldTweets3 as got
import pandas as pd
import tqdm

from got_utils import getJsonResponse
from utils import set_crawl_date


def crawl_tweets(start_date, end_date, query, lang='en', debug=True):    
    '''
    query: 검색할 트윗 검색어
    lang: 검색할 트윗 언어
    debug: 설정 시 에러 url 표시
    '''
    
    # replace got.TweetManager.getJsonResponse with got_utils.getJsonResponse
    got.manager.TweetManager.getJsonResponse = getJsonResponse
    
    print("========== 트윗 수집 시작: {0} ~ {1} ==========".format(start_date, end_date))
    start_time = time.time()
    tweet_criteria = got.manager.TweetCriteria().setQuerySearch(query)\
                                                .setSince(start_date)\
                                                .setUntil(end_date)\
                                                .setLang(lang)
    tweets = got.manager.TweetManager.getTweets(tweet_criteria, debug=debug)
    
    elapsed_time = time.time()-start_time
    
    print("수집 완료 : {}".format(time.strftime("%H:%M:%S", time.gmtime(elapsed_time))))
    print("총 수집 트윗 개수 : {0}".format(len(tweets)))
    
    return tweets


# got tweet 객체로부터 결과 추출
def get_results(tweet_data):
    results = []
    for tweet in tqdm(tweet_data):
        results.append(
            {
                'url': tweet.permalink,
                'date': tweet.date,
                'text': tweet.text,
                'user': tweet.username,
                'mentions': tweet.mentions,
                'retweets': tweet.retweets,
                'favorites': tweet.favorites,
                'hashtags': tweet.hashtags
            }
        )
        
    return results


# 추출한 결과 저장
def save_tweets(tweet_lists, base_file_dir="tweets"):
    
    if not os.path.exists(base_file_dir):
        os.makedirs(base_file_dir)
        
    with open(f"{base_file_dir}/tweets.csv", "a", -1, encoding="utf-8") as f:    
        writer = csv.writer(f)
        writer.writerow(['url', 'date', 'text', 'user', 'mentions', 'retweets', 'favorites', 'hashtags'])        
        for tweet_list in tqdm(tweet_lists):
            writer.writerow(list(tweet_list.values()))
            
            
# 크롤링 진행
dateRange = pd.date_range(start='20220101', end='20220601', freq='MS') # freq 변경 가능: 며칠치 데이터 가져올 지 설정.

for date in dateRange:
    crawl_start, crawl_end = set_crawl_date(date)  # freq 변경 가능: 며칠치 데이터 가져올 지 설정.
    tweet_results = crawl_tweets(crawl_start, crawl_end, query='Elon Musk', debug=False)
    tweet_results_lists = get_results(tweet_results)
    save_tweets(tweet_results_lists)