#!/usr/bin/python

import sys
import pickle
import pandas
import warnings
warnings.filterwarnings("ignore")
sys.path.append("../tools/")

from feature_format import featureFormat, targetFeatureSplit
from tester import dump_classifier_and_data


### Task 1: Select what features you'll use.
### features_list is a list of strings, each of which is a feature name.
### The first feature must be "poi".
financial_features = ['salary', 'deferral_payments', 'total_payments',
                      'loan_advances', 'bonus', 'restricted_stock_deferred',
                      'deferred_income', 'total_stock_value', 'expenses',
                      'exercised_stock_options', 'other', 'long_term_incentive',
                      'restricted_stock', 'director_fees']
email_features = ['to_messages','from_poi_to_this_person', 'from_messages',
                  'from_this_person_to_poi', 'shared_receipt_with_poi']
#The features list is tuned further in the code
features_list = ['poi'] + financial_features + email_features + ['discreationary_cashout_ratio', 'poi_to_ratio', 'poi_from_ratio']

### Load the dictionary containing the dataset
with open("final_project_dataset.pkl", "rb") as data_file:
    data_dict = pickle.load(data_file)

### Task 2: Remove outliers
del data_dict["TOTAL"]
del data_dict['THE TRAVEL AGENCY IN THE PARK']

# and fill "NaN" with 0 to improve engineering the feature

for entry in data_dict.values():
    for feature in financial_features:
        if entry[feature] == 'NaN':
            entry[feature] = 0

### Task 3: Create new feature(s)
### Store to my_dataset for easy export below.
my_dataset = data_dict

#New feature: discreationary_cashout_ratio
# estimates the ratio of taken payments vs possible total income
# poi to/from ratio -> normalized with the to/from messages
for entry in my_dataset.values():
    divisor = entry["total_stock_value"] + entry["total_payments"] + entry["deferred_income"]
    if divisor !=0:
        entry["discreationary_cashout_ratio"] = \
                ( entry["exercised_stock_options"] + \
                  entry["total_payments"] - entry["salary"]) /\
                divisor
    else:
        entry["discreationary_cashout_ratio"] = "NaN"
            
    if entry['to_messages'] == "NaN":
        entry["poi_to_ratio"] = "NaN"
        entry["poi_from_ratio"] = "NaN"
    else:
        entry["poi_to_ratio"] = entry['from_poi_to_this_person']/entry['to_messages']
        entry["poi_from_ratio"] = entry['from_this_person_to_poi']/entry['from_messages']


### Extract features and labels from dataset for local testing
features_list = ['poi', "exercised_stock_options", 'salary', 'deferred_income']

data = featureFormat(my_dataset, features_list, sort_keys = True)
labels, features = targetFeatureSplit(data)

### Task 4: Try a varity of classifiers
### Please name your classifier clf for easy export below.
### Note that if you want to do PCA or other multi-stage operations,
### you'll need to use Pipelines. For more info:
### http://scikit-learn.org/stable/modules/pipeline.html

# Provided to give you a starting point. Try a variety of classifiers.
from sklearn.naive_bayes import GaussianNB
from sklearn.ensemble import AdaBoostClassifier
from sklearn.ensemble import RandomForestClassifier

clfs = [GaussianNB(), 
        AdaBoostClassifier(),
        RandomForestClassifier(n_estimators=50)]

### Task 5: Tune your classifier to achieve better than .3 precision and recall 
### using our testing script. Check the tester.py script in the final project
### folder for details on the evaluation method, especially the test_classifier
### function. Because of the small size of the dataset, the script uses
### stratified shuffle split cross validation. For more info: 
### http://scikit-learn.org/stable/modules/generated/sklearn.cross_validation.StratifiedShuffleSplit.html
# Example starting point. Try investigating other evaluation techniques!
from sklearn.model_selection import train_test_split, cross_val_score, StratifiedKFold, GridSearchCV
from sklearn.metrics import precision_score, recall_score
features_train, features_test, labels_train, labels_test = \
    train_test_split(features, labels, test_size=0.3, random_state=42)
    
from tester import test_classifier

for i, clf in enumerate(clfs):
    clf.fit(features_train, labels_train)
    pred = clf.predict(features_test)
    print("Precision: %.2f Recall: %.2f" % (precision_score(labels_test, pred), recall_score(labels_test, pred)))   
    k = 6
    skf = StratifiedKFold(n_splits=k)
    
    if i==1: #tune Adaboost
        parameters = {'base_estimator':(GaussianNB(), None), 
                      'n_estimators':[10, 50, 100],
                      'learning_rate':[0.1,1.0,5.]}
        gscv = GridSearchCV(clf, parameters, cv=skf, scoring="f1")
        gscv.fit(features, labels)
        print(pandas.DataFrame(gscv.cv_results_)
                [["param_base_estimator", "param_n_estimators", "param_learning_rate",
                "rank_test_score", 'mean_fit_time', 'mean_test_score']])
        clf = gscv.best_estimator_
        
    precision = cross_val_score(clf, features, labels,
                            scoring='precision',
                            cv=skf)
    recall = cross_val_score(clf, features, labels,
                            scoring='recall',
                            cv=skf)
                        
    print("Precision: %.2f Recall: %.2f" % (sum(precision)/k, sum(recall)/k))
    
    test_classifier(clf, my_dataset, features_list, folds = 100)
    try:
        print(*zip(features_list[1:],clf.feature_importances_))
    except:
        pass
    
clf = clfs[0]

#basic manual tuning was checked for the the model, however since no method strongly 
#depends on the hyperparameters, the defautls were kept except for the RandomForest where 
#the defaukt n_estimators = 10 lead to underfitting
# balanced RandomForest and realistic prior probability for the GaussianNB resulted in worse
# target values


### Task 6: Dump your classifier, dataset, and features_list so anyone can
### check your results. You do not need to change anything below, but make sure
### that the version of poi_id.py that you submit can be run on its own and
### generates the necessary .pkl files for validating your results.

dump_classifier_and_data(clf, my_dataset, features_list)