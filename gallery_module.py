import json
import re
import requests

# GitHub URL for the gallery file
url = "https://raw.githubusercontent.com/civilservicesclub-iitmandi/website/refs/heads/main/gallery"

response = requests.get(url)

if response.status_code == 200:
    text = response.text
    # Remove trailing commas before closing braces/brackets (invalid JSON)
    text = re.sub(r",\s*([}\]])", r"\1", text)
    data = json.loads(text)
    images = data
else:
    images = [{'url': 'https://cdn-icons-png.flaticon.com/512/10809/10809585.png', 'title': 'Error fetching gallery images'}]
