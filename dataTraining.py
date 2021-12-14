#Recommend to perform this stage on Google Colab instead of local PC - 8 threads can bubble RAM usage to over 40GB
import pandas as pd
from dataset.dataCleaning import cleanData
from db.connection import get_weatherData
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split as tts
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score,recall_score,precision_score,f1_score,roc_auc_score,average_precision_score
import pickle

RSEED = 12345

#dataprep
data = get_weatherData()
data = cleanData(data)

#drop non numeric data
data.drop(['reading_time'], axis=1, inplace=True)
data.drop(['summary'], axis=1, inplace=True)

#convert precip_type from categorical to numerical (only 3 classes)
le = LabelEncoder()
data['precip_type']=le.fit_transform(data['precip_type'])


#select y as precip_type for this model
x = data.iloc[:,1:]
y = data.iloc[:,0]

#split 30% for test
X_train, X_test, y_train, y_test = tts(x,y,test_size=0.3,random_state=RSEED)

#train model, set parallel threads to 8 for speedier training
rf = RandomForestClassifier(max_depth=16,random_state=RSEED,n_jobs=8)
rf.fit(X_train,y_train)
y_pred = rf.predict(X_test)

#model performance
print("Accuracy Score {}".format(accuracy_score(y_test,y_pred)))
print("Recall Score {}".format(recall_score(y_test,y_pred,average='weighted')))
print("Precision Score {}".format(precision_score(y_test,y_pred,average='weighted')))
print("F1 Score {}".format(f1_score(y_test,y_pred,average='weighted')))

#dump pickle model
pickle.dump(rf, open('model/weathermodel.pickle','wb'))