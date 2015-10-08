<h1> Gather and analyze data from social media </h1>

Check out the ipython notebooks for examples. 

<h2> Main functionality:</h2>
<ul>
  <li>network_search.py</li>
  <li>message_classification.py</li>
  <li>twitter_stream_classification.py</li>
</ul>

<h3> network_search.py (Check out example ipython notebook)</h3>

Explores the messages, locations and connection of a user account of interest. 
Information is stored in an sqlite database created for the source_node. 
One potential risk is the exponential growth for each network depth. The user can counteract this in two ways: i) Retrieve      information from only the top x% connections and ii) limit search to a specified network depth. 

<h3> message_classification.py (Check out example ipython notebook)</h3> 

Trains a text classifier on labeled examples. Then classifies tweets stored in an sqlite database to identify intersting candidates for further inspection.  

<h3> twitter_stream_classification.py (Example ipython notebook comning soon.) </h3>

Identify interesting candidate tweets from the (keyword filtered) twitter stream. Use a trained text classifier to keep only tweets which fall into classes of interest with a minimal prediction probability. 
