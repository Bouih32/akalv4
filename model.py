import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
import pickle

file_path = 'data.csv'
data = pd.read_csv(file_path)

X = data.drop(columns=['Fertilizer Name'])
y = data['Fertilizer Name']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

model = RandomForestClassifier(random_state=42)
model.fit(X_train, y_train)

y_pred = model.predict(X_test)

with open('model.pkl', 'wb') as model_file:
    pickle.dump(model, model_file)
