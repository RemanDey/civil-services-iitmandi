import requests
import json
# Raw URL for the announcements file
url = "https://raw.githubusercontent.com/civilservicesclub-iitmandi/website/main/announcements"

response = requests.get(url)
if response.status_code == 200:
    data = response.json() 
    announcements = data
    # Parse JSON into a Python list
else:
    announcements = [{'date': 'Now', 'title': 'Error fetching announcements', 'tag': 'Default'}]

