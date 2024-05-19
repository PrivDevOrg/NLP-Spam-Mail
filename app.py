from flask import Flask,render_template,url_for,request
import pandas as pd 
# import pickle
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB
# import joblib
from imblearn.over_sampling import SMOTE
# from sklearn.metrics import precision_score
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import MultinomialNB
from nltk.stem import PorterStemmer
from sklearn.linear_model import LogisticRegression
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import precision_score, recall_score, f1_score



app = Flask(__name__)

# we load the data in our excel into a panda dataframe
df= pd.read_csv(r"spam.csv", encoding="latin-1")

# here we drop these column that are generated by default or in our excel we have a unnamed columns
df.drop(['Unnamed: 2', 'Unnamed: 3', 'Unnamed: 4'], axis=1, inplace=True)

# here we remove the whitespaces in all row in the v1 column
df['v1'] = df['v1'].str.strip()

# here we create label column and we map its data from the v1 column if the v1 is spam we put 1 if its ham we put 0
df['label'] = df['v1'].map({'ham': 0, 'spam': 1})

# stemmer = PorterStemmer()
# here we create message column and we put the data as it is from v2
# df['message'] = df['v2'].apply(lambda x: ' '.join([stemmer.stem(word) for word in x.split()]))
df['message']=df['v2']

# we drop the column v1 and v2 row in our data
df.drop(['v1','v2'],axis=1,inplace=True)

# here we assign that x is the message and y is the lable (ham or spam)
X = df['message']
y = df['label']



# we create a countvectorizer its used to create a matrix that take each document (sentence) as a row 
# and each unique word as a column and put the count of each word and it remove the stopwords -- >from scikit-learn library
cv = CountVectorizer(stop_words='english')
X = cv.fit_transform(X)


# remove the nan before we balance the data we used numpy if either y and x is nan we remove the whole row
mask = ~(np.isnan(X.toarray()).any(axis=1) | np.isnan(y))
X = X[mask]
y = y[mask]


# we balance the data here using smote 
# (SMOTE check the minority then for each sentence he find a similar sentence and he create a third sentence from both)
smote = SMOTE(random_state=42)
X_resampled, y_resampled = smote.fit_resample(X, y)



# we split the data between the test and training
X_train, X_test, y_train, y_test = train_test_split(X_resampled, y_resampled, test_size=0.33, random_state=42)

# we create LogisticRegression and the we train it on the training data
# (logisticregression is a classifier that we train it before we try it on new data/sentences ) -> from scikit-learn library
clf = LogisticRegression()
clf.fit(X_train,y_train)

# some classifier to compare the result of them
# classifiers = [
#     LogisticRegression(),
#     SVC(),
#     RandomForestClassifier(),
#     DecisionTreeClassifier(),
#     KNeighborsClassifier(),
#     MultinomialNB()
# ]
# for clf in classifiers:
# 	clf.fit(X_train,y_train)

# 	# here we find the score on the testing data
# 	score = clf.score(X_test, y_test)
# 	y_pred = clf.predict(X_test)
# 	precision = precision_score(y_test, y_pred)
# 	recall = recall_score(y_test, y_pred)
# 	f1 = f1_score(y_test, y_pred)

# 	print(f"Classifier: {type(clf).__name__}")
# 	print(f"Accuracy score: {score:.2f}")
# 	print(f"Precision: {precision:.2f}")
# 	print(f"Recall: {recall:.2f}")
# 	print(f"F1-score: {f1:.2f}")
# 	print()




# here we render the home page where the user will enter the sentence
@app.route('/')
def home():
	return render_template('home.html')

# when the user submit a from to the predict page we call the predict method
@app.route('/predict',methods=['POST'])
def predict():
	

	if request.method == 'POST':
		# here we get the message entered by the user
		message = request.form['message']
		# here we create a list with a single element message
		data = [message]
		# we create the matrix of the data we have (We put the message in array because countervecorize expect a 1D array or a list)
		# then we used .toarray to convert it to a 2D array to use it in the prediction
		vect = cv.transform(data).toarray()
		# here we use the logisticregression to predict the result
		my_prediction = clf.predict(vect)
	# after we get the prediction we load the result and send the prediciton and the message as parameter 
	return render_template('result.html',prediction = my_prediction,messagex = message)



if __name__ == '__main__':
	app.run(debug=True)