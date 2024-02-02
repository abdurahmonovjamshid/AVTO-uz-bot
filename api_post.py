import requests

# Define the API endpoint URL
url = "http://56d5-84-54-90-131.ngrok-free.app/api/cars/"

# Define the car data to be posted
car_data = {
    "owner_telegram_id": 6881836818,  # The owner's Telegram ID
    "name": "Example Car",
    "model": "XYZ",
    "year": 2022,
    "price": 25000,
    "description": "This is an example car.",
    "contact_number": "+998906666666",
    "images": [
        {
            "image_link": "https://telegra.ph/file/6529587f8e3bd7a9b0c56.jpg",
            "telegraph": "https://telegra.ph/file/6529587f8e3bd7a9b0c56.jpg"
        },
        {
            "image_link": "https://telegra.ph/file/6529587f8e3bd7a9b0c56.jpg",
            "telegraph": "https://telegra.ph/file/6529587f8e3bd7a9b0c56.jpg"
        }
    ]
}

# Send the POST request to create the car
response = requests.post(url, json=car_data)

# Check the response status code
if response.status_code == 201:
    print("Car data posted successfully!")
else:
    print("Failed to post car data. Error:", response.text)
