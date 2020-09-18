import tweepy
import datetime
import MarkovModel
import GetOldTweets3 as got
import time

class TwitterBot(object):

    def __init__(self):
        #The following five lines are unique to the account being used as a bot
        #as well as the account being used to train the model.
        self.consumer_key = ''
        self.consumer_secret = ''
        self.access_token = ''
        self.access_token_secret = ''
        self.username = ''
        self.auth = tweepy.OAuthHandler(self.consumer_key, self.consumer_secret)
        self.auth.set_access_token(self.access_token, self.access_token_secret)
        self.api = tweepy.API(self.auth)
        self.ngramModel = MarkovModel.NgramModel(3)
        self.initialize_model()

    #Uses GetOldTweets API in order to train the model using 10,000 tweets
    #without hitting Twitter's limit of requests.
    def initialize_model(self):
        count = 0
        #items = tweepy.Cursor(self.api.user_timeline, screen_name=self.username, tweet_mode="extended").items()
        for i in range(1, 3200, 200):
            for status in self.api.user_timeline(self.username, since_id = i, count = 3200, tweet_mode = "extended"):
                try:
                    self.update_model(status.retweeted_status.full_text)
                except:
                    self.update_model(status.full_text)
                count += 1
        print(count)

    def update_model(self, tweet):
        self.ngramModel.update(tweet)

    #Generates a random string, separates it by <END> tokens, and
    #publishes the first tweet in the subsequent list.
    def generate_tweet(self):
        return self.ngramModel.random_text(100).split("<END>")[0]

    def publish_tweet(self, tweet):
        #print(tweet[:240])
        self.api.update_status(tweet[:240])

    #Runs indefinitely, sleeping for 15 seconds before checking for a new tweet
    #in order to avoid reaching tweepy's request limit.
    def functionality(self):
        newTweet = self.api.user_timeline(self.username, count = 1)[0]
        oldTweet = newTweet.text
        while True:
            try:
                newTweet = self.api.user_timeline(self.username, count = 1)[0]
                if newTweet.text != oldTweet:
                    self.update_model(newTweet.text)
                    tweet = self.generate_tweet()
                    self.publish_tweet(tweet)
                oldTweet = newTweet.text
            except IndexError:
                pass
            time.sleep(15)

bot = TwitterBot()
bot.publish_tweet(bot.generate_tweet())
bot.functionality()
