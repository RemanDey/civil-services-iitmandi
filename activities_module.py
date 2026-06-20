import requests

# Raw URL for the activities file
url = "https://raw.githubusercontent.com/civilservicesclub-iitmandi/website/refs/heads/main/activities"

response = requests.get(url)
if response.status_code == 200:
    data = response.json() 
    activities = data
    # Parse JSON into a Python list
else:
    activities = [{'date': 'Now', 'title': 'Error fetching activities', 'tag': 'ERROR'}]

