import json
import re
import requests

# GitHub URL for the core file
url = "https://raw.githubusercontent.com/civilservicesclub-iitmandi/website/refs/heads/main/core"

response = requests.get(url)

if response.status_code == 200:
    text = response.text
    # Remove trailing commas before closing braces/brackets (invalid JSON)
    text = re.sub(r",\s*([}\]])", r"\1", text)
    data = json.loads(text)
    core_members = data
else:
    core_members = [
        {"name": "ERROR", "role": "ERROR", "email": "ERROR", "profile_image": "https://cdn-icons-png.flaticon.com/512/10809/10809585.png"}
    ]

