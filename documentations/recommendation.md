# Deep Neural Networks for YouTube Recommendations

## Abstract
YouTube represents one of the largest scale and most sophisticated industrial recommendation systems in existence.
Two stage information retrieval dichotomy:
1. Deep candidate generation model
2. Separate deep ranking model

[Overview of YouTube recommendation algorithm](https://lh4.googleusercontent.com/ynNiJVoWEo9IqZG2RMhgpPzgGLXyMjMX2cAXYWHjC4J5_pIOtXKw77PE_KqxQzfP1HYSCFi0uUoim1_E5WEtK8ds38UhHN01wAJCjJ_aKxRwblTI5Jby5laXd4rixKnynV47Ygeib5T_-hPZsz-AhZU)

## Introduction
- YouTube is the world's largest platform for creating, sharing and discovering video content.
- YouTube recommendations are responsible for helping more than a billion users discover personalized content from an 
ever-growing corpus of videos.
- Recommending YouTube vidoes is extremely challenging from three major perspectives:
1. **Scale**: Many existing recommendation algorithms proven to work well on small problems fail to operate on our scale.
Highly specialized distributed learning algorithms and efficient serving systems are essential for handling YouTube's
massive user base and corpus.
2. **Freshness**: YouTube has a very dynamic corpus with many hours of video are uploaded per second. The recommendation
system should be responsible enough to model newly uploaded content as well as the latest actions taken by the user.
Balancing new content with well-established vidoes can be understood from an exploration/exploitation perspective.
3. **Noise**: Historical user behavior on YouTube is inherently difficult to predict due to sparcity and a variety of 
unobservable external factors. We rarely obtain the ground truth of user satisfaction and instead model noisy implicit feedback
signals.

## Architecture and Feature Representation
As shown in **Figure 3**, the candidate generation network comprises several features (e.g user watch history,
search query, demographics, user gender, example age etc).
All these features are concatenated and fed to a feed-forward network comprising fully connected layers and ReLU activation.

[Architecture of candidate generation network](https://lh6.googleusercontent.com/Zz0-JEsQGGzbrzs8JkLQRugmubfh-HZZVSWbE-HI7KSgd9GXauNv9h_VtRjeZCDSFFz5-R8xYIOLkHyYVKgwin5w8Sq_MgwWPi-n1d4wGTTlcG7wb0FTa0Lxy6wIxAdHlSV6ZAI5owtDsE_YpMiw4ok).

- The user watch history is represented as a variable-length sequence of space video IDs (watched by the user recently)
mapped to their dense embeddings.
These dense embeddings (of videos watched by the user) are then averaged to represent the user watch vector fed into a feed-forward network. Note that the video embeddings are learned jointly with other model parameters.
- Like the user watch vector, the search query is also tokenized into unigrams and bigrams, and each token is mapped
to its resprective token embedding. The embeddings of all tokens are then averaged to obtain a user search vector.
- The user's geographic location and device ID are embedded and concatenated to represent demographics. Further,
the binary and continous features (e.g user gender, logged-in state and age) are fed directly after being normalized.
- The distribution of video popularity is highly non-stationary (i.e it lasts for a few days, slows down and then converges). Still, the above candidate recommendation network will only recommend based on the average watch likelihood of a video (but not its popularity). 
- "Example Age" represents the age of the training example used. During inference, it is set to zero or negative
to ensure that the model predictions don't get biased towards the past, and it assigns more likelihood to a new video.
