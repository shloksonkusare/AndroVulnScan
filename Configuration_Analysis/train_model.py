import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
import pickle

# Sample labeled dataset
data = pd.DataFrame({
    'permissions': [['INTERNET', 'ACCESS_FINE_LOCATION'], ['INTERNET'], ['READ_SMS', 'INTERNET'], ['INTERNET']],
    'components': [{'activities': 5, 'services': 1, 'receivers': 0, 'providers': 0},
                   {'activities': 3, 'services': 2, 'receivers': 1, 'providers': 0},
                   {'activities': 2, 'services': 1, 'receivers': 1, 'providers': 0},
                   {'activities': 4, 'services': 0, 'receivers': 0, 'providers': 0}],
    'min_sdk': [21, 23, 19, 21],
    'is_secure': [0, 1, 0, 1]  # Labels: 0 = Insecure, 1 = Secure
})

# Feature engineering: Convert categorical lists to numerical counts
data['permission_count'] = data['permissions'].apply(len)
data['activity_count'] = data['components'].apply(lambda x: x['activities'])
data['service_count'] = data['components'].apply(lambda x: x['services'])
data['receiver_count'] = data['components'].apply(lambda x: x['receivers'])
data['provider_count'] = data['components'].apply(lambda x: x['providers'])

X = data[['permission_count', 'activity_count', 'service_count', 'receiver_count', 'provider_count', 'min_sdk']]
y = data['is_secure']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

model = RandomForestClassifier()
model.fit(X_train, y_train)

y_pred = model.predict(X_test)
print(f"Accuracy: {accuracy_score(y_test, y_pred)}")
print(f"Classification Report:\n{classification_report(y_test, y_pred)}")

# Save the trained model
with open('security_model.pkl', 'wb') as file:
    pickle.dump(model, file)
