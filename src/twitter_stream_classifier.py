__author__ = "Fernando Carrillo"
__email__ = "fernando at carrillo.at"

import sys
import json 

from tweepy.streaming import StreamListener
from tweepy import Stream

from twitter_auth import Twitter_auth
from message_classifier import MessageClassifier

class TwitterStreamClassifier(StreamListener):
 	"""
 	docstring for TwitterStreamClassifier
 	"""
 	def __init__(self, classifier, batch_size=100):
 		"""
 		classifier : 
 			Classifier used for tweet classification 

 		batch_size : int 
 			Number of tweets to collect for batch classification. 

 		"""
 		self.classifier = classifier
 		self.batch_size = batch_size
 		self.batch = [] 

 	def on_data(self, data):
 		if json.loads(data).keys()[0] != 'delete': 
			self.add_to_batch(data)
		return True

	def add_to_batch(self, data): 
		self.batch.append(data)
		if len(self.batch) >= self.batch_size: 
			self.classify()

	def classify(self): 
		print(json.loads(self.batch))
		#probabilities = mc.predict_proba(messages)

	def on_error(self, status):
		print status 

if __name__ == '__main__':

	# set keywords to filter. 
	keywords = ['git']
	keywords = [] 
	
	# Load trained classfier. At this point this is trained on the 
	# newsgroup data, but will be trained on a data-set of the domain of interest. 
	print('Load classifier.')
	mc = MessageClassifier()
	mc.load('../data/tweet_clf_nb')
	print(mc.labels)
	print('Load classifier. Done.')

	# Load the StreamListener. This holds the classifier. 
	lister = TwitterStreamClassifier(MessageClassifier)

	# Get login from Twitter_auth module. 
	stream = Stream(Twitter_auth().authenticate(), lister)

	# This line filters Twitter streams to track keywords. 
	try:
		if len(keywords) == 0: 
			stream.sample()
		else: 
			stream.filter(track=keywords)
	except Exception, e:
		print >> sys.stderr, e 
		pass
	
	