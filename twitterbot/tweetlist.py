#
#  grabbed most of this code from https://gist.github.com/yanofsky/5436496
#  only changed a bit of it
#
#
# i will be keeping a separate file for holding all of jaden smith's tweets.
# this should speed up the process of generating a tweet, because i won't constantly
# be grabbing it from online.

import json, tweepy, csv, os

secrets_file = open('twitterbot/secrets.json', 'r')
secrets = json.load(secrets_file)

# Twitter API credentials
CONSUMER_KEY = secrets["twitter"]["consumer_key"]
CONSUMER_SECRET = secrets["twitter"]["consumer_secret"]
ACCESS_KEY = secrets["twitter"]["access_key"]
ACCESS_SECRET = secrets["twitter"]["access_secret"]

def getAllTweets(screen_name):
    # Twitter only allows access to a users most recent 3240 tweets with this method

    # authorize twitter, initialize tweepy
    auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
    auth.set_access_token(ACCESS_KEY, ACCESS_SECRET)
    api = tweepy.API(auth)

    # initialize a list to hold all the tweepy Tweets
    alltweets = []

    # make initial request for most recent tweets (200 is the maximum allowed count)
    new_tweets = api.user_timeline(screen_name=screen_name, count=50)

    # save most recent tweets
    alltweets.extend(new_tweets)

    # save the id of the oldest tweet less one
    oldest = alltweets[-1].id - 1

    # hail mary fubar
    tweet_count = 0

    # keep grabbing tweets until there are no tweets left to grab
    #while len(new_tweets) > 0 & tweet_count < 100:
    #    print "getting tweets before %s" % (oldest)

        # all subsiquent requests use the max_id param to prevent duplicates
    #    new_tweets = api.user_timeline(screen_name=screen_name, count=50, max_id=oldest)

        # save most recent tweets
    #    alltweets.extend(new_tweets)

        # update the id of the oldest tweet less one
    #    oldest = alltweets[-1].id - 1
	
	# increment tweet count
	#tweet_count += 1

        #print "...%s tweets downloaded so far" % min(len(alltweets),100)

    # transform the tweepy tweets into a 2D array that will populate the csv
    outtweets = [[tweet.created_at, tweet.text.encode("utf-8")] for tweet in alltweets]

    # write the csv
    with open('twitterbot/data/%s_tweets.csv' % screen_name, 'wb') as f:
        writer = csv.writer(f)
        writer.writerow(["created_at", "text"])
        writer.writerows(outtweets)

    pass

def getJadenTweets():
    getAllTweets(jaden_name)
    return

def isRetweet(row):
    # TODO: check if 'RT @' are the first letters of the tweet
    tweet = row.split(',')[2] # isolate the tweet

    return 'RT @' in tweet

def isLineBreak(row):

            # lots of tweets, for some reason, have line breaks in them.
            # if a line in the CSV doesn't have at least two commas, i'm assuming that
            # it's a mistake and i'm getting rid of it.

    count = row.count(",")
    return count < 2

def sanitize(word):
    word = word.lower()

    word = word.replace("\t", "")
    word = word.replace("\r", "")
    word = word.replace("\n", "")
    word = word.replace("\"", "")

    return word

def makeMarkovChain(screen_name):

    print 'making markov chain'

    tweets_file = open(str('twitterbot/data/clean_%s_tweets.csv' % screen_name), 'r')
    # markovJSON = json.loads(request.POST.get('mydata', '{}'))

    data = 'data'

    markovData = {data: {}}
    rowCounter = 0

    for row in tweets_file:
        print 'loading row ' + str(rowCounter) + '/2002'

        tweet = row.split(',')[2] # isolate the tweet
        tweetWords = tweet.split(' ')

        markovJSONfile = open(str('twitterbot/data/%s_markov.json' % screen_name), 'w')

        previousWord = ''
        for tweetWord in tweetWords:

            if previousWord is not '':
                previousWord = sanitize(previousWord)
                tweetWord = sanitize(tweetWord)

                if not markovData[data].get(previousWord): # key isn't there
                    markovData[data][previousWord] = {} # init
                    markovData[data][previousWord][tweetWord] = str(0) # start frequency at 0

                elif not markovData[data].get(tweetWord): # value isn't there
                    markovData[data][previousWord][tweetWord] = str(0) # start at 0

                else: # increment

                    # TODO: fix!
                    try:
                        index = markovData[data][previousWord][tweetWord]
                        index = int(index) + 1
                        markovData[data][previousWord][tweetWord] = str(index)
                    except KeyError:
                        pass

                # clear file
                # markovJSONfile.seek(0)
                # markovJSONfile.truncate()

                # write to file
            
            previousWord = tweetWord

        rowCounter = rowCounter + 1

    json.dump(markovData, markovJSONfile, sort_keys=True, indent=4)
    markovJSONfile.close()

    tweets_file.close()

    print 'finished, exiting'




def cleanTweets(screen_name):

    # Set working file names
    raw_file = str('twitterbot/data/%s_tweets.csv' % screen_name)
    cleanfile = str('twitterbot/data/clean_%s_tweets.csv' % screen_name)

    # Read from raw file, run cleaning functions, print to clean file
    with open(raw_file,'r') as incsv, open(cleanfile,'w') as outcsv:
        for row in incsv:

            if isLineBreak(row):
                # don't write this to new file
                continue
            elif isRetweet(row):
                # don't write this either
                continue
            else:
                outcsv.write(row)

