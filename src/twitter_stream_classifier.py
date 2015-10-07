__author__ = "Fernando Carrillo"
__email__ = "fernando at carrillo.at"

import sys
import json 
import numpy as np
import scipy as sp 

from tweepy.streaming import StreamListener
from tweepy import Stream

from twitter_auth import Twitter_auth
from message_classifier import MessageClassifier

class TwitterStreamClassifier(StreamListener):
 	"""
 	docstring for TwitterStreamClassifier
 	"""
 	def __init__(self, classifier, classes_of_interest, batch_size=10000, probability_threshold=0, verbose=1):
 		"""
 		classifier : 
 			Classifier used for tweet classification 

 		classes_of_interset : String array 
 			Keep tweets that are classified in the following classes. 

 		batch_size : int 
 			Number of tweets to collect for batch classification. 

 		"""
 		self.classifier = classifier
 		self.classes_of_interest = classes_of_interest
 		self.batch_size = batch_size
 		self.probability_threshold = probability_threshold
 		self.verbose = verbose
 		self.batch = [] 

 	def on_data(self, data):
 		if json.loads(data).keys()[0] != 'delete': 
			self.add_to_batch(data)
			if self.verbose > 0 and len(self.batch) % 100 == 0: 
				print('Collected %d tweets in the current batch.' % (len(self.batch)))
		return True

	def add_to_batch(self, data): 
		self.batch.append(data)
		if len(self.batch) >= self.batch_size: 
			self.classify()

	def classify(self): 
		json_entries = [json.loads(x) for x in self.batch]
		messages = [x['text'] for x in json_entries]
		probabilities = self.classifier.predict_proba(messages)
		
		for message, probs, tweet in zip(messages, probabilities, json_entries): 
			if self.classifier.labels[np.argmax(probs)] in self.classes_of_interest and np.max(probs) > self.probability_threshold: 
				print('%s with a probability of\t%f\t%r' % (self.classifier.labels[np.argmax(probs)], np.max(probs), message.encode('utf-8')))
				print('Entropy of prediction: %f' % (sp.stats.entropy(probs)))
				print(tweet)
		
		# Delete entries from the buffer. 
		self.batch = [] 

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
	print('Load classifier. Done.')

	# Load the StreamListener. This holds the classifier. 
	lister = TwitterStreamClassifier(classifier=mc, classes_of_interest=['sci.med'], probability_threshold=0.95)

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
	
	