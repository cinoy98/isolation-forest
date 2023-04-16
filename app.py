import pickle
import numpy as np
from flask import Flask, request, jsonify
import datetime
import pandas as pd

app = Flask(__name__)
    # Define the sigmoid function
def sigmoid(x):
    return 1 / (1 + np.exp(-x))
def map_time_of_day(time_of_day):
  # print(time_of_day)
  timestamp_datetime = datetime.datetime.strptime(time_of_day, '%Y-%m-%d %H:%M:%S.%f')

# Extract the hour from the datetime object
  hour = timestamp_datetime.hour
    # print(time_of_day)
  # hour = int(time_of_day.strftime('%H'))
  # print(hour)
  if hour >= 5 and hour < 12:
      return 1 # Morning
  elif hour >= 12 and hour < 17:
      return 2 # Noon
  elif hour >= 17 and hour < 21:
      return 3 # Evening
  else:
      return 4 # Night

# Load pickle files
with open('Browser_Name_and_Version_mapping.pkl', 'rb') as f:
    Browser_Name_and_Version_mapping = pickle.load(f)

with open('City_mapping.pkl', 'rb') as f:
    City_mapping = pickle.load(f)

with open('Country_mapping.pkl', 'rb') as f:
    Country_mapping = pickle.load(f)

with open('Device_Type_mapping.pkl', 'rb') as f:
    Device_Type_mapping = pickle.load(f)

with open('IP_Address_mapping.pkl', 'rb') as f:
    IP_Address_mapping = pickle.load(f)

with open('isolation_forest_model.pkl', 'rb') as f:
    isolation_forest_model = pickle.load(f)

with open('OS_Name_and_Version_mapping.pkl', 'rb') as f:
    OS_Name_and_Version_mapping = pickle.load(f)

with open('Region_mapping.pkl', 'rb') as f:
    Region_mapping = pickle.load(f)


with open('User_Agent_String_mapping.pkl', 'rb') as f:
    User_Agent_String_mapping = pickle.load(f)

with open('User_ID_mapping.pkl', 'rb') as f:
    User_ID_mapping = pickle.load(f)

with open('isolation_forest_model.pkl', 'rb') as f:
    isolation_forest = pickle.load(f)

@app.route('/predict', methods=['POST'])
def predict():
    # Parse request data
    data = request.json
    print(data)
    Timestamp = map_time_of_day(data['time'])

    # Map attributes to numeric values
    UserID= int(data['UserID'])
    Rtt= data['Rtt']
    IPAddress= str(data['IPAddress'])
    Country= data['Country']
    Region= data['Region']
    City= data['City']
    asn= data['asn']
    UserAgentString= data['UserAgentString']
    Browser= data['Browser']
    os= data['os']
    Device= data['Device']
    LoginSuccessful= data['LoginSuccessful']
    IsAttackIP= data['IsAttackIP']
    # IsAccountTakeover= data['IsAccountTakeover']


    UserID = User_ID_mapping[UserID]
    IPAddress = IP_Address_mapping[IPAddress]
    Country = Country_mapping[Country]
    Region = Region_mapping[Region]
    City = City_mapping[City]
    UserAgentString = User_Agent_String_mapping[UserAgentString]
    Browser = Browser_Name_and_Version_mapping[Browser]
    os = OS_Name_and_Version_mapping[os]
    Device = Device_Type_mapping[Device]


    # Create input array
    # X = np.array([Timestamp,UserID, Rtt,IPAddress, Country, Region,City,asn,UserAgentString,Browser,os,Device,LoginSuccessful,IsAttackIP,IsAccountTakeover]).reshape(1, -1)
    
    input = {'Login Timestamp': [Timestamp],
        'User ID': [UserID],
        'Round-Trip Time [ms]': [Rtt],
        'IP Address': [IPAddress],
        'Country':[Country],
        'Region':[Region],
        "City":[City],
        "ASN":[asn],
        "User Agent String":[UserAgentString],
        "Browser Name and Version":[Browser],
        "OS Name and Version":[os],
        "Device Type":[Device],
        "Login Successful":[LoginSuccessful],
        "Is Attack IP":[IsAttackIP]
        # "Is Account Takeover":[IsAccountTakeover]
        }
    
# Create a DataFrame from the dictionary
			# 9	1	1	1	500021	2643	196	2	1	0	1	
    # input2 = {'Login Timestamp': 1,
    #     'User ID': 6163,
    #     'Round-Trip Time [ms]': 555.0,
    #     'IP Address': 9,
    #     'Country':1,
    #     'Region':1,
    #     "City":1,
    #     "ASN":500021,
    #     "User Agent String":2643,
    #     "Browser Name and Version":196,
    #     "OS Name and Version":2,
    #     "Device Type":1,
    #     "Login Successful":0,
    #     "Is Attack IP":1
    #     # "Is Account Takeover":[IsAccountTakeover]
    #     }    
    X = pd.DataFrame(input)
    # Calculate the anomaly scores for all data points
    scores = isolation_forest.decision_function(X)
    print("risk score : ",scores)
# Normalize the scores using the sigmoid function
    # normalized_scores = sigmoid(scores)
    score_list = scores.tolist()

# Evaluate the model on the test set
    y_pred = isolation_forest.predict(X)
    print("anomaly : ",y_pred)
    # Predict anomaly score

    y_pred_list = y_pred.tolist()

    # Return anomaly score as JSON response
    return jsonify({'score': score_list,'anomaly':y_pred_list})

if __name__ == '__main__':
    app.run(debug=True)
