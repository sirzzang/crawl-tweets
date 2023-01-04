import datetime


def set_crawl_date(start_date, freq=1):
    '''
    Notes:
        :param end_date: excluded when set in TweetCriteria.
        (https://github.com/Mottl/GetOldTweets3/blob/master/GetOldTweets3/manager/TweetCriteria.py#L50)
    '''

    end_date = start_date + datetime.timedelta(days=freq)
    
    # timestamp to string format
    start_date = start_date.strftime("%Y-%m-%d")
    end_date = end_date.strftime("%Y-%m-%d")
    
    print(f"Set crawl date: from {start_date} to {end_date}")
        
    return start_date, end_date

