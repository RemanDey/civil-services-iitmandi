import json
import re
import requests

# GitHub URL for the notes file
url = "https://raw.githubusercontent.com/civilservicesclub-iitmandi/website/main/notes"

response = requests.get(url)
if response.status_code == 200:
    text = response.text
    text = re.sub(r",\s*([}\]])", r"\1", text)
    data = json.loads(text)
    notes = data
else:
    notes = [{'category': 'Default', 'title': 'Error fetching notes', 'link': '#'}]

