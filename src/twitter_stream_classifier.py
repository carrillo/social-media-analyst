__author__ = "Fernando Carrillo"
__email__ = "fernando at carrillo.at"

import sys
import json 
import re
import numpy as np
import scipy as sp

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker 
from sqlalchemy.sql import exists
from db_tables import Base, User, Connection, Message, Location, create_sqlite_db

from tweepy.streaming import StreamListener
from tweepy import Stream

from twitter_auth import Twitter_auth
from message_classifier import MessageClassifier

class TwitterStreamClassifier(StreamListener):
 	"""
 	docstring for TwitterStreamClassifier
 	"""
 	def __init__(self, db_session, classifier, classes_of_interest, batch_size=10000, probability_threshold=0, verbose=1):
 		"""
 		classifier : 
 			Classifier used for tweet classification 

 		classes_of_interset : String array 
 			Keep tweets that are classified in the following classes. 

 		batch_size : int 
 			Number of tweets to collect for batch classification. 

 		"""
 		self.db_session = db_session
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

	def add_user(self, user_name): 
		"""
		Adds a user to the database.
		1. Check if already present. 
		2. If not, add. 
		"""
		if not self.db_session.query(exists().where(User.name == user_name)).scalar(): 
			new_user = User(name=user_name, visited=False, depth=0)
			self.db_session.add(new_user)
			self.db_session.commit()

	def add_message(self, user_name, text): 
		"""
		Add message to MESSAGE relationship. 
		"""
		new_message = Message(user_name=user_name, text=text)
		self.db_session.add(new_message)
		self.db_session.commit()

	def add_connection(self, user_name1, user_name2, weight): 
		"""
		Add connection between user 1 and user 2 in CONNECTION relationship. 
		"""
		entry = self.db_session.query(Connection).filter((Connection.user_1_name == user_name1) & (Connection.user_2_name == user_name2)).scalar()
		if not entry: 
			new_connection = Connection(user_1_name=user_name1, user_2_name=user_name2, weight=weight )
			self.db_session.add(new_connection)
			self.db_session.commit()	
		else: 
			self.db_session.query(Connection).filter((Connection.user_1_name == user_name1) & (Connection.user_2_name == user_name2)).update({"weight": (entry.weight + weight)})
			self.db_session.commit()

	def add_location(self, user_name, geojson, location): 
		"""
		Add message to LOCATION relationship. 
		"""
		if (geojson == "nan"): geojson = "NULL"
		if (location == "nan"): location = "NULL"
		new_location = Location(user_name=user_name, geojson=geojson, location=location)
		self.db_session.add(new_location)
		self.db_session.commit()

	def classify(self): 
		json_entries = [json.loads(x) for x in self.batch]
		messages = [x['text'] for x in json_entries]
		probabilities = self.classifier.predict_proba(messages)
		
		for message, probs, tweet in zip(messages, probabilities, json_entries): 
			if self.classifier.labels[np.argmax(probs)] in self.classes_of_interest and np.max(probs) > self.probability_threshold: 
				u1 = tweet['user']['screen_name']
				self.add_user(u1)
				self.add_message(u1, message)
				geostring = str(tweet['coordinates'])
				if (geostring == 'None'): geostring = 'NULL'
				self.add_location(u1, geostring, tweet['user']['location'])
				for u2 in re.findall('\B\@\w+', str(tweet)): 
					self.add_connection(user_name1=u1, user_name2=u2.strip('\@'), weight=1)
		# Delete entries from the buffer. 
		self.batch = [] 

	def on_error(self, status):
		print status 

if __name__ == '__main__':

	# set keywords to filter.
	keywords = [] 
	
	# Load trained classfier. At this point this is trained on the 
	# newsgroup data, but will be trained on a data-set of the domain of interest. 
	print('Load classifier.')
	mc = MessageClassifier()
	mc.load('../data/tweet_clf_nb')
	print('Load classifier. Done.')

	# Create and connect to database
	db_path = 'sqlite:///data/twitter_stream.db'
	create_sqlite_db(db_path)
	engine = create_engine(db_path)
	Base.metadata.bind = engine 
	DBSession = sessionmaker(bind=engine)
	session = DBSession()

	# Load the StreamListener. This holds the classifier. 
	lister = TwitterStreamClassifier(db_session=session, classifier=mc, classes_of_interest=['sci.med'], probability_threshold=0.95)

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
	
	