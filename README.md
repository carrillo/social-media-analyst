<h1> Gather and analyze data from social media </h1>

<h2> Check out the ipython notebooks for examples</h2>

<h2> Main functionality:</h2>
<ul>
  <li>network_search.py</li>
  <li>message_classification.py</li>
  <li>twitter_stream_classification.py</li>
</ul>

<h2> network_search.py </h2>
  (Check out the ipython notebook for an example!)

  Explores the messages, locations and connection of a user account of interest. 
  Information is stored in an sqlite database created for the source_node. 
  One potential risk is the exponential growth for each network depth. The user can counteract this in two ways: i) Retrieve      information from only the top x% connections and ii) limit search to a specified network depth. 
