Installation
================================
Install the following through pip install
- ```scikit-learn```
- ```nltk``` (also download data after installing)
- ```senticnet```

Download MaltParser 1.8.1, place it at ```~/maltparser-1.8.1```, and create a symbolic
link ```ln -s ~/maltparser-1.8.1/maltparser-1.8.1.jar /usr/local/bin/malt.jar```

Download concept parser from the senticNet website and place it at ```~/concept-parser```.


File structure
================================
Most results are stored at ```static/test_data/sample_data.json```.

Caches are located in ```caches```

Helper script is in ```scripts```

Python code is in ```code```

Visualization tools are in ```static```

Other assorted data is in ```data```


Visualizer
================================

To use our visualizer, open ```static/map.html```. Use Firefox instead of Safari for a better support of AngularJS.

```static/map.js``` and ```static/admin.js``` contain all the logic components related to mapping and visualizing.
 

Rule-Based Scorers
================================

To run the scorers, run ```python code/process_review.py [foodName] 0 199```

foodName can be any of beer, burger, burrito, lobster. 0 and 199 indicate that we're running from
data sample 0 to data sample 199. You can change these numbers.

To evaluate the scorer output, run
```
python evaluator.py static/test_data/sample_data.json
```

Classifier
================================

To run the classification system, ensure that ```static/test/sample_data.json```
has been generated (revert, or regenerate if necessary).  Then, go to the code
director and run ```python feature_based_sentiment_classifier.py foodName```.
Where foodName can be any of those specified in the rule-based section.
