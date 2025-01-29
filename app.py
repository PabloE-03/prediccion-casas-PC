from flask import Flask, render_template, request, jsonify
import pickle
import pandas as pd
import os.path as path
from sklearn.neighbors import KNeighborsClassifier, KNeighborsRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from prepross import preprocessing
from k_folds import k_folds


app = Flask(__name__)

def get_data():
  data = preprocessing()
  
  y = data['quality']
  X = data.drop('quality', axis=1)
  
  X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
  train = pd.concat([X_train, y_train], axis=1)
  
  '''
  classifier = pickle.load(open('classifier.pkl', 'rb'))
  regressor = pickle.load(open('regressor.pkl', 'rb'))
  
  print(f'Precisión del clasificador: {accuracy_score(y_test, classifier.predict(X_test))*100}%')
  print(f'Precisión del regresor: {accuracy_score(y_test, regressor.predict(X_test))*100}%')
  '''
  
  return train

def create_models():
  hyperparams = k_folds(get_data())
  max_key = max(hyperparams, key=hyperparams.get)
  max_value = hyperparams[max_key]
  
  classifier = KNeighborsClassifier(n_neighbors=max_value, weights=max_key)
  regressor = KNeighborsRegressor(n_neighbors=max_value, weights=max_key)
  
  y = get_data()['quality'] 
  X = get_data().drop('quality', axis=1)
  
  classifier.fit(X, y)
  regressor.fit(X, y)
  
  pickle.dump(classifier, open('classifier.pkl', 'wb'))
  pickle.dump(regressor, open('regressor.pkl', 'wb'))

@app.route('/')
def index():
  return render_template('index.html')

@app.route('/classifier')
def knn_classifier():
  params = request.get_json(force=True)
  classifier = pickle.load(open('classifier.pkl', 'rb'))
  prediction = classifier.predict(params)
  return jsonify(prediction)

@app.route('/regressor')
def knn_regressor():
  params = request.get_json(force=True)
  regressor = pickle.load(open('regressor.pkl', 'rb'))
  prediction = regressor.predict(params)
  return jsonify(prediction)

if not path.exists('classifier.pkl') and not path.exists('regressor.pkl'):
  create_models()

if __name__ == '__main__':
  app.run(
    host='localhost',
    port=5002,
    debug=True
  )