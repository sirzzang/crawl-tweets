import json
import time
import urllib

import GetOldTweets3 as got


# https://github.com/Mottl/GetOldTweets3/blob/master/GetOldTweets3/manager/TweetManager.py#L274
def getJsonResponse(tweetCriteria, refreshCursor, cookieJar, proxy, useragent=None, debug=False):
    """
    Invoke an HTTP query to Twitter.
    Should not be used as an API function. A static method.
    """
    url = "https://twitter.com/i/search/timeline?"

    if not tweetCriteria.topTweets:
        url += "f=tweets&"

    url += ("vertical=news&q=%s&src=typd&%s"
            "&include_available_features=1&include_entities=1&max_position=%s"
            "&reset_error_state=false")

    urlGetData = ''

    if hasattr(tweetCriteria, 'querySearch'):
        urlGetData += tweetCriteria.querySearch

    if hasattr(tweetCriteria, 'excludeWords'):
        urlGetData += ' -'.join([''] + tweetCriteria.excludeWords)

    if hasattr(tweetCriteria, 'username'):
        if not hasattr(tweetCriteria.username, '__iter__'):
            tweetCriteria.username = [tweetCriteria.username]

        usernames_ = [u.lstrip('@') for u in tweetCriteria.username if u]
        tweetCriteria.username = {u.lower() for u in usernames_ if u}

        usernames = [' from:'+u for u in sorted(tweetCriteria.username)]
        if usernames:
            urlGetData += ' OR'.join(usernames)

    if hasattr(tweetCriteria, 'within'):
        if hasattr(tweetCriteria, 'near'):
            urlGetData += ' near:"%s" within:%s' % (tweetCriteria.near, tweetCriteria.within)
        elif hasattr(tweetCriteria, 'lat') and hasattr(tweetCriteria, 'lon'):
            urlGetData += ' geocode:%f,%f,%s' % (tweetCriteria.lat, tweetCriteria.lon, tweetCriteria.within)

    if hasattr(tweetCriteria, 'since'):
        urlGetData += ' since:' + tweetCriteria.since

    if hasattr(tweetCriteria, 'until'):
        urlGetData += ' until:' + tweetCriteria.until

    if hasattr(tweetCriteria, 'minReplies'):
        urlGetData += ' min_replies:' + tweetCriteria.minReplies

    if hasattr(tweetCriteria, 'minFaves'):
        urlGetData += ' min_faves:' + tweetCriteria.minFaves

    if hasattr(tweetCriteria, 'minRetweets'):
        urlGetData += ' min_retweets:' + tweetCriteria.minRetweets

    if hasattr(tweetCriteria, 'lang'):
        urlLang = 'l=' + tweetCriteria.lang + '&'
    else:
        urlLang = ''
    url = url % (urllib.parse.quote(urlGetData.strip()), urlLang, urllib.parse.quote(refreshCursor))
    useragent = useragent or got.manager.TweetManager.user_agents[2] # fix user agent
    print(useragent)

    headers = [
        ('Host', "twitter.com"),
        ('User-Agent', useragent),
        ('Accept', "application/json, text/javascript, */*; q=0.01"),
        ('Accept-Language', "en-US,en;q=0.5"),
        ('X-Requested-With', "XMLHttpRequest"),
        ('Referer', url),
        ('Connection', "keep-alive")
    ]

    if proxy:
        opener = urllib.request.build_opener(urllib.request.ProxyHandler({'http': proxy, 'https': proxy}), urllib.request.HTTPCookieProcessor(cookieJar))
    else:
        opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cookieJar))
    opener.addheaders = headers

    if debug:
        print(url)
        print('\n'.join(h[0]+': '+h[1] for h in headers))

    # sleep to prevent HTTP 429 request error
    time.sleep(3)
    
    # try to get response
    try:
        response = opener.open(url)
        jsonResponse = response.read()
    except TimeoutError as e:
        '''
        catch TimeoutError and retry
        '''
        print("Timeout error, sleep 30")
        time.sleep(30)
        
        # TODO: retry annotation
        try:
            response = opener.open(url)
            jsonResponse = response.read()
        except TimeoutError as e:
            print("Timeout Error again.")
            pass

    except Exception as e:
        '''
        catch exception and print out info
        '''
        print("An error occured during an HTTP request:", str(e))
        print("Error URL:", url)
        print("Try to open in browser: https://twitter.com/search?q=%s&src=typd" % urllib.parse.quote(urlGetData))
        pass
        # sys.exit()
        
    # response to json
    try:
        s_json = jsonResponse.decode()
    except:
        print("Invalid response from Twitter")
        print("Error URL:", url)
        pass
        # sys.exit()
    else:
        try:
            dataJson = json.loads(s_json)
        except:
            print("Error parsing JSON: %s" % s_json)
            print("Error URL:", url)
        pass
        # sys.exit()
        
    if debug:
        print(s_json)
        print("---\n")

    return dataJson