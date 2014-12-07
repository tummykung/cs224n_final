Notes
=====
To run SVM, first run
```
export PYTHONPATH=$PYTHONPATH:$HOME/libsvm-3.20/python
```



NLP 224N Final Project Proposal
===============================

Introduction
------------

Given a food item on Yelp (e.g. dolmathes), we want to summarize and visualize various food attributes according to reviews and compare the same food item across various restaurants or regions (e.g. lobsters in Maine are so much better than other places).

Methods
-------

We will begin by classifying the sentiment in every sentence that contains food items of interest (using SenticNet, Sentic API -- http://sentic.net/api/), and annotating some of the data for evaluation. The visualization would show the four dimensions of emotions (pleasantness, attention, sensitivity, aptitude) and polarity broken down by every place, and support it with snippets found on Yelp.

The next step is to extract and visualize broader concepts (than the above five summary scores) related to a food item and seeing if certain descriptions or sentiments are more common for some food than others.  For this, we may use the SenticNet category and concept parser (see http://sentic.net/demo/). If it is not accurate enough, we may attempt to write our own category parser, trying to determine which phrases are describing the foods we are evaluating.

Examples
--------

The following real examples show various ways to describe a burger (shown in underline):

Californians are all about the In-N-Out, where you can get your burger animal style.
The hamburger are ok, they have bigger portions than other places.
it took 30 minutes to get a hamburger.
and every burger was perfectly cooked and earned rave reviews
The burger was so good that I'd have no problem eating it completely plain - burger and bun alone.
I would've loved to have one of those succulent burgers, but I'm in the zone with my diet/exercise these days.
My fiance got a salad and I got a burger.  The food was very tasty and came out quickly. [coreference resolution needed]

Some common structures that we see
(NP [NounOfInterest]) (VP (VPZ is) (ADJP-PRD [JJ]))
[Subj] [V] [NounOfInterest]
NP [Verb] [NounOfInterest], which is [JJ]

Related Work
------------
https://github.com/pbhuss/Sentimental. Tum used to work on visualization of four dimensions of sentiment on Google map.
The Sentic library has  the following dependencies: Stanford POS tagger and NLTK
Previous NLP final project work: http://nlp.stanford.edu/courses/cs224n/2009/fp/9.pdf
“Hidden Factors and Hidden Topics: Understanding Rating Dimensions with Review Text.” Julian McAuley, Jure Leskovec. Stanford University. Published in ACM RecSys '13 Proceedings
“Clustered Layout Word Cloud for User Generated Review.” Ji Wang, Jian Zhao, Sheng Guo, Chris North. Virginia Tech and University of Toronto. Presented at Graphics Interface 2014 Montreal
“Improving Restaurants by Extracting Subtopics from Yelp Reviews.” James Huang, Stephanie Rogers, Eunkwang Joo. UC Berkeley. Presented at iConference 2014 Berlin

Timetable
---------
Week 1 (October 27), focus on PA3, but do some research on the scope of this project. Check various tools whether all are working and sufficient.
Week 2 (November 3), basic sentiment analysis workflow
Week 3 (November 10), geographic visualization
Week 4 (November 17), error analysis
Week 5 (November 24), category extraction
Week 6 (December 1), add finer categorical visualization
Week 7 (December 8): presentation


Comments from TAs
-----------------
Tum and Raphael,

Your project aims to apply sentiment analysis techniques to Yelp reviews to extract information that can then be used to find meaningful trends about food items across different geographic areas or restaurants. This seems like an interesting project, and should be doable within the scope of this class.

A couple notes:
-Right now, your project doesn't seem to have any concrete criteria that can be used to evaluate the performance of your system. This isn't necessarily an issue if there are other methods of determining whether it is working as expected (i.e., the outputted trends can be verified by your own judgement or domain knowledge), but please consider setting some sort of criteria to help gauge progress and performance.
-It seems that you are relying heavily on Sentic for much of your sentiment analysis work; this is fine, but please make sure those tools are sufficient for your needs before you get too far into the project, and that you are adding some meaningful work or insight on top of their provided tools. This will likely come from the second portion of your project, which seems less well-defined at this junction.