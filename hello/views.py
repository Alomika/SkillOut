import json
from datetime import datetime
from pathlib import Path

import requests
from bs4 import BeautifulSoup
from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

# Create your views here.

def home(request):
    return HttpResponse("Hello, world!")

def hello_there(request, name):
    print(request.build_absolute_uri()) #optional
    return render(
        request,
        'hello/hello_there.html',
        {
            'name': name,
            'date': datetime.now()
        }
    )


@csrf_exempt
def scrape_text(request):
    if request.method != "POST":
        return JsonResponse({"error": "Only POST is allowed."}, status=405)

    try:
        payload = json.loads(request.body.decode("utf-8") or "{}")
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON body."}, status=400)

    url = (payload.get("url") or "").strip()
    if not url:
        return JsonResponse({"error": "Field 'url' is required."}, status=400)
    if not (url.startswith("http://") or url.startswith("https://")):
        return JsonResponse({"error": "URL must start with http:// or https://."}, status=400)

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
    except requests.RequestException as exc:
        return JsonResponse({"error": f"Failed to fetch URL: {exc}"}, status=400)

    soup = BeautifulSoup(response.text, "html.parser")

    for element in soup(["script", "style", "noscript"]):
        element.extract()

    text = soup.get_text(separator=" ", strip=True)[:60000]

    output_dir = Path(settings.BASE_DIR) / "scraped_text"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / "latest_scrape.txt"
    output_file.write_text(text, encoding="utf-8")

    return JsonResponse(
        {
            "message": "Scraped text saved successfully.",
            "file": str(output_file.relative_to(settings.BASE_DIR)),
            "characters": len(text),
        }
    )