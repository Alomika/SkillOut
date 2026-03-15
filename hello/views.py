import json
from datetime import datetime
from pathlib import Path
import time

import requests
from bs4 import BeautifulSoup
from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from .models import Student, Category, Subject, StudentSubject
import json

import os

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
def add_student(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            username = data.get('username')
            email = data.get('email')
            password = data.get('password')
            first_name = data.get('first_name', '')
            last_name = data.get('last_name', '')

            if not username or not password:
                return JsonResponse({'error': 'Username and password are required'}, status=400)

            if User.objects.filter(username=username).exists():
                return JsonResponse({'error': 'Username already exists'}, status=400)

            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name
            )

            student = Student.objects.create(user=user)

            return JsonResponse({
                'message': 'Student created successfully',
                'student_id': student.id,
                'user_id': user.id
            }, status=201)

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    else:
        return JsonResponse({'error': 'Method not allowed'}, status=405)

@csrf_exempt
def add_category(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            name = data.get('name')

            if not name:
                return JsonResponse({'error': 'Name is required'}, status=400)

            if Category.objects.filter(name=name).exists():
                return JsonResponse({'error': 'Category already exists'}, status=400)

            category = Category.objects.create(name=name)

            return JsonResponse({
                'message': 'Category created successfully',
                'category_id': category.id,
                'name': category.name
            }, status=201)

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    else:
        return JsonResponse({'error': 'Method not allowed'}, status=405)

@csrf_exempt
def add_subject(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            name = data.get('name')
            category_id = data.get('category_id')

            if not name:
                return JsonResponse({'error': 'Name is required'}, status=400)

            if Subject.objects.filter(name=name).exists():
                return JsonResponse({'error': 'Subject already exists'}, status=400)

            category = None
            if category_id:
                try:
                    category = Category.objects.get(id=category_id)
                except Category.DoesNotExist:
                    return JsonResponse({'error': 'Category not found'}, status=400)

            subject = Subject.objects.create(name=name, category=category)

            return JsonResponse({
                'message': 'Subject created successfully',
                'subject_id': subject.id,
                'name': subject.name,
                'category_id': category.id if category else None,
                'category_name': category.name if category else None
            }, status=201)

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    else:
        return JsonResponse({'error': 'Method not allowed'}, status=405)

@csrf_exempt
def add_subject_interest(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            student_id = data.get('student_id')
            subject_id = data.get('subject_id')
            interest = data.get('interest')

            if not all([student_id, subject_id, interest]):
                return JsonResponse({'error': 'student_id, subject_id, and interest are required'}, status=400)

            try:
                interest = int(interest)
                if interest not in [1, 2, 3, 4, 5]:
                    return JsonResponse({'error': 'Interest must be between 1 and 5'}, status=400)
            except ValueError:
                return JsonResponse({'error': 'Interest must be a number'}, status=400)

            try:
                student = Student.objects.get(id=student_id)
            except Student.DoesNotExist:
                return JsonResponse({'error': 'Student not found'}, status=404)

            try:
                subject = Subject.objects.get(id=subject_id)
            except Subject.DoesNotExist:
                return JsonResponse({'error': 'Subject not found'}, status=404)

            student_subject, created = StudentSubject.objects.update_or_create(
                student=student,
                subject=subject,
                defaults={'interest': interest}
            )

            return JsonResponse({
                'message': 'Interest level updated successfully' if not created else 'Interest level set successfully',
                'student_id': student_id,
                'subject_id': subject_id,
                'interest': interest,
                'created': created
            }, status=201)

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    else:
        return JsonResponse({'error': 'Method not allowed'}, status=405)

def get_student_subjects(request, student_id):
    if request.method == 'GET':
        try:
            student = Student.objects.get(id=student_id)
        except Student.DoesNotExist:
            return JsonResponse({'error': 'Student not found'}, status=404)

        student_subjects = StudentSubject.objects.filter(student=student).select_related('subject__category')

        subjects_data = []
        for ss in student_subjects:
            subject = ss.subject
            subjects_data.append({
                'subject_id': subject.id,
                'name': subject.name,
                'category_id': subject.category.id if subject.category else None,
                'category_name': subject.category.name if subject.category else None,
                'interest': ss.interest,
                'interest_description': dict(StudentSubject.INTEREST_CHOICES)[ss.interest]
            })

        return JsonResponse({
            'student_id': student_id,
            'student_username': student.user.username,
            'subjects': subjects_data,
            'total_subjects': len(subjects_data)
        }, status=200)

    else:
        return JsonResponse({'error': 'Method not allowed'}, status=405)

@csrf_exempt
def add_category(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            name = data.get('name')

            if not name:
                return JsonResponse({'error': 'Name is required'}, status=400)

            if Category.objects.filter(name=name).exists():
                return JsonResponse({'error': 'Category already exists'}, status=400)

            category = Category.objects.create(name=name)

            return JsonResponse({
                'message': 'Category created successfully',
                'category_id': category.id,
                'name': category.name
            }, status=201)

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    else:
        return JsonResponse({'error': 'Method not allowed'}, status=405)

@csrf_exempt
def add_subject(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            name = data.get('name')
            category_id = data.get('category_id')

            if not name:
                return JsonResponse({'error': 'Name is required'}, status=400)

            if Subject.objects.filter(name=name).exists():
                return JsonResponse({'error': 'Subject already exists'}, status=400)

            category = None
            if category_id:
                try:
                    category = Category.objects.get(id=category_id)
                except Category.DoesNotExist:
                    return JsonResponse({'error': 'Category not found'}, status=400)

            subject = Subject.objects.create(name=name, category=category)

            return JsonResponse({
                'message': 'Subject created successfully',
                'subject_id': subject.id,
                'name': subject.name,
                'category_id': category.id if category else None,
                'category_name': category.name if category else None
            }, status=201)

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    else:
        return JsonResponse({'error': 'Method not allowed'}, status=405)


@csrf_exempt
def scrape_text(request):
    if request.method != "POST":
        return JsonResponse({"error": "Only POST is allowed."}, status=405)

    try:
        payload = json.loads(request.body.decode("utf-8") or "{}")
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON body."}, status=400)

    url = (payload.get("url") or "").strip()
    if "fromSemester" not in payload or "toSemester" not in payload:
        return JsonResponse(
            {"error": "Fields 'fromSemester' and 'toSemester' are required."},
            status=400,
        )

    from_semester = payload.get("fromSemester")
    to_semester = payload.get("toSemester")

    try:
        from_semester = int(from_semester)
        to_semester = int(to_semester)
    except (TypeError, ValueError):
        return JsonResponse({"error": "fromSemester and toSemester must be numbers."}, status=400)

    if from_semester < 1 or to_semester < 1:
        return JsonResponse({"error": "fromSemester and toSemester must be at least 1."}, status=400)

    if from_semester > to_semester:
        return JsonResponse({"error": "fromSemester cannot be greater than toSemester."}, status=400)
    if not url:
        return JsonResponse({"error": "Field 'url' is required."}, status=400)
    if not (url.startswith("http://") or url.startswith("https://")):
        return JsonResponse({"error": "URL must start with http:// or https://."}, status=400)

    max_retries = 3
    for attempt in range(max_retries):
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            break
        except requests.HTTPError as e:
            return JsonResponse({"error": f"HTTP error: {e.response.status_code}"}, status=400)
        except (requests.Timeout, requests.ConnectionError) as e:
            if attempt == max_retries - 1:
                return JsonResponse({"error": f"Failed after {max_retries} attempts: {e}"}, status=400)
            time.sleep(1)
        except requests.RequestException as e:
            return JsonResponse({"error": f"Request failed: {e}"}, status=400)

    soup = BeautifulSoup(response.text, "html.parser")

    for element in soup(["script", "style", "noscript"]):
        element.extract()

    text = soup.get_text(separator=" ", strip=True)[:60000]

    output_dir = Path(settings.BASE_DIR) / "scraped_text"
    output_dir.mkdir(parents=True, exist_ok=True)
    txt_output_file = output_dir / "latest_scrape.txt"
    txt_output_file.write_text(text, encoding="utf-8")

    try:
        import ollama
    except ImportError:
        return JsonResponse(
            {"error": "Ollama Python package is not installed. Install it with: pip install ollama"},
            status=500,
        )

    # prompt = (
    #     "Extract only study subject names from semesters "
    #     f"{from_semester} to {to_semester} from the provided webpage text. "
    #     f"That means study subjects are between text for {from_semester} semester to {to_semester + 1} semester. "
    #     "Do not translate or modify original subject text. "
    #     "Return strict JSON only in this format: "
    #     '{"study_subjects": ["subject 1", "subject 2"]}. '
    #     "No markdown, no explanation.\n\n"
    #     f"Webpage text:\n{text}"
    # )

    prompt = (
    "Task: Extract study subjects only from selected semesters.\n"
    f"Selected semesters: {from_semester} to {to_semester} (inclusive).\n\n"
    "Strict rules:\n"
    "1) Include subject only if it is clearly listed under semester number "
    f"{from_semester}..{to_semester}.\n"
    "2) Exclude all subjects from any semester outside that range.\n"
    "3) If semester is unclear, exclude it.\n"
    "4) Keep original subject text exactly (no translation, no rewriting).\n"
    "5) Remove duplicates.\n"
    "6) Output ONLY valid JSON with one key exactly:\n"
    '{"study_subjects":["...","..."]}\n'
    "7) Do not output markdown, comments, explanations, or extra keys.\n\n"
    "Webpage text:\n"
    f"{text}"
)

    try:
        ollama_response = ollama.chat(
            model="llama3",
            messages=[{"role": "user", "content": prompt}],
            options={"temperature": 0, "top_p": 0.1}
        )
    except Exception as exc:
        return JsonResponse({"error": f"Ollama request failed: {exc}"}, status=500)

    raw_content = ollama_response.get("message", {}).get("content", "").strip()

    if raw_content.startswith("```"):
        raw_content = raw_content.strip("`")
        if raw_content.lower().startswith("json"):
            raw_content = raw_content[4:].strip()

    parsed = None
    try:
        parsed = json.loads(raw_content)
    except json.JSONDecodeError:
        start = raw_content.find("{")
        end = raw_content.rfind("}")
        if start != -1 and end != -1 and end > start:
            try:
                parsed = json.loads(raw_content[start : end + 1])
            except json.JSONDecodeError:
                parsed = None

    subjects = []
    if isinstance(parsed, dict) and isinstance(parsed.get("study_subjects"), list):
        subjects = [str(item).strip() for item in parsed["study_subjects"] if str(item).strip()]
    else:
        subjects = [
            line.strip("-• \t")
            for line in raw_content.splitlines()
            if line.strip("-• \t")
        ]

    json_output = {
        "url": url,
        "from_semester": from_semester,
        "to_semester": to_semester,
        "study_subjects": subjects,
    }

    json_output_file = output_dir / "latest_subjects.json"
    json_output_file.write_text(
        json.dumps(json_output, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    return JsonResponse(
        {
            "message": "Scrape and AI extraction completed successfully.",
            "file": str(txt_output_file.relative_to(settings.BASE_DIR)),
            "json_file": str(json_output_file.relative_to(settings.BASE_DIR)),
            "characters": len(text),
            "subjects_count": len(subjects),
            "study_subjects": subjects,
        }
    )


# This view is for testing purposes to retrieve the latest scraped subjects from the JSON file.
def get_latest_subjects(request):
    # SVARBU: Failas yra 'scraped_text' aplanke, todėl turime jį įtraukti į kelią
    file_path = os.path.join(settings.BASE_DIR, 'scraped_text', 'latest_subjects.json')
    
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return JsonResponse(data)
    
    # Jei failo nėra, grąžiname klaidą su tiksliu keliu (kad žinotume, kur jis ieško)
    return JsonResponse({
        "error": "File not found", 
        "searched_at": str(file_path)
    }, status=404)