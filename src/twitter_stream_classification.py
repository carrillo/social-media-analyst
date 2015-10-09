from message_classifier import MessageClassifier

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker 
from sqlalchemy.sql import exists
from db_tables import Base, User, Connection, Message, Location, create_sqlite_db

from tweepy import Stream
from twitter_stream_classifier import TwitterStreamClassifier
from twitter_auth import Twitter_auth

# set keywords to filter.
keywords = ['data'] 
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
lister = TwitterStreamClassifier(db_session=session, classifier=mc, classes_of_interest=['sci.med'], probability_threshold=0.90)

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

