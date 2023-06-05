import requests

url = "https://eastus.api.cognitive.microsoft.com/customvision/v3.0/Prediction/7f8dff8a-540f-4481-83f6-fe5c40b27a86/detect/iterations/Iteration4/image"
headers = {
    "Prediction-Key": "f1435307693849aaadb11925eb6eaaae",
    "Content-Type": "application/octet-stream"
}

# Open image file in binary mode
with open('/Users/stefanhamilton/Downloads/Frame_2023-05-22_12-20-59.jpg', 'rb') as f:
    img_data = f.read()

response = requests.post(url, headers=headers, data=img_data)

# Get response as JSON
response_json = response.json()

# Filter response to only include entries with probabilities > 0.1
filtered_response = [prediction for prediction in response_json['predictions'] if prediction['probability'] > 0.1]

print(filtered_response)
