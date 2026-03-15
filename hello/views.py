import json
from datetime import datetime
from pathlib import Path
import time
import re

import requests
import urllib3
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


def _load_ratings_map(ratings_file: Path):
    ratings_map = {}
    if not ratings_file.exists():
        return ratings_map

    pattern = re.compile(r"^Semester\s+(\d+)\s+\|\s+(.*?)\s+\|\s+Stars:\s+(.*)$")
    for raw_line in ratings_file.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        match = pattern.match(line)
        if not match:
            continue

        semester = int(match.group(1))
        subject = match.group(2).strip()
        stars_raw = match.group(3).strip().lower()
        stars = None
        if stars_raw not in {"", "not picked", "none", "null"}:
            try:
                stars = int(stars_raw)
            except ValueError:
                stars = None

        ratings_map[(semester, subject)] = stars

    return ratings_map


def _extract_subjects_from_latest_text(text: str, from_semester: int, to_semester: int):
    subjects_by_semester = {semester: [] for semester in range(from_semester, to_semester + 1)}
    marker_pattern = re.compile(r"(\d+)\s+(?:rudens|pavasario)\s+semestras", re.IGNORECASE)
    subject_pattern = re.compile(r"([A-ZĄČĘĖĮŠŲŪŽ][^\n\r]*?)\s+(?:lietuvių|anglų)\s+\d+(?:\.\d+)?", re.IGNORECASE)

    markers = list(marker_pattern.finditer(text))
    for index, marker in enumerate(markers):
        semester = int(marker.group(1))
        if semester < from_semester or semester > to_semester:
            continue

        start = marker.end()
        end = markers[index + 1].start() if index + 1 < len(markers) else len(text)
        block = text[start:end]

        seen = set()
        for found in subject_pattern.finditer(block):
            subject = " ".join(found.group(1).split()).strip("-• \t")
            if not subject:
                continue
            if any(token in subject.lower() for token in ["privalomieji dalykai", "individualiųjų studijų dalykai", "dalykas dėstymo kalba kreditai"]):
                continue
            if subject in seen:
                continue

            seen.add(subject)
            subjects_by_semester[semester].append(subject)

    return subjects_by_semester


@csrf_exempt
def latest_subjects_fast(request):
    if request.method != "POST":
        return JsonResponse({"error": "Only POST is allowed."}, status=405)

    try:
        payload = json.loads(request.body.decode("utf-8") or "{}")
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON body."}, status=400)

    from_semester = payload.get("fromSemester", 1)
    to_semester = payload.get("toSemester", 1)
    url = (payload.get("url") or "").strip()

    try:
        from_semester = int(from_semester)
        to_semester = int(to_semester)
    except (TypeError, ValueError):
        return JsonResponse({"error": "fromSemester and toSemester must be numbers."}, status=400)

    if from_semester > to_semester:
        return JsonResponse({"error": "fromSemester cannot be greater than toSemester."}, status=400)

    output_dir = Path(settings.BASE_DIR) / "scraped_text"
    json_file = output_dir / "latest_subjects.json"
    text_file = output_dir / "latest_scrape.txt"
    ratings_file = output_dir / "latest_subject_ratings.txt"

    subjects_by_semester = {semester: [] for semester in range(from_semester, to_semester + 1)}
    source = "latest_scrape.txt"

    if json_file.exists():
        try:
            cached = json.loads(json_file.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            cached = {}

        if isinstance(cached.get("semester_subjects"), dict):
            source = "latest_subjects.json"
            for sem in range(from_semester, to_semester + 1):
                raw_list = cached.get("semester_subjects", {}).get(str(sem), [])
                if isinstance(raw_list, list):
                    subjects_by_semester[sem] = [str(item).strip() for item in raw_list if str(item).strip()]
        elif isinstance(cached.get("study_subjects"), list):
            source = "latest_subjects.json"
            source_sem = int(cached.get("from_semester", from_semester))
            if from_semester <= source_sem <= to_semester:
                subjects_by_semester[source_sem] = [
                    str(item).strip() for item in cached.get("study_subjects", []) if str(item).strip()
                ]

    if all(len(items) == 0 for items in subjects_by_semester.values()):
        if not text_file.exists():
            return JsonResponse({"error": "No cached files found in scraped_text/."}, status=400)

        raw_text = text_file.read_text(encoding="utf-8")
        subjects_by_semester = _extract_subjects_from_latest_text(raw_text, from_semester, to_semester)
        source = "latest_scrape.txt"

    ratings_map = _load_ratings_map(ratings_file)
    rows = []
    for sem in range(from_semester, to_semester + 1):
        for subject in subjects_by_semester.get(sem, []):
            rows.append(
                {
                    "id": f"{sem}::{subject}",
                    "semester": sem,
                    "subject": subject,
                    "stars": ratings_map.get((sem, subject)),
                }
            )

    return JsonResponse(
        {
            "message": "Loaded cached subjects.",
            "source": source,
            "url": url or source,
            "from_semester": from_semester,
            "to_semester": to_semester,
            "rows": rows,
            "subjects_count": len(rows),
        },
        status=200,
    )

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
    use_latest_scrape = bool(payload.get("useLatestScrape", False))
    from_semester = payload.get("fromSemester", 1)
    to_semester = payload.get("toSemester", 4)

    try:
        from_semester = int(from_semester)
        to_semester = int(to_semester)
    except (TypeError, ValueError):
        return JsonResponse({"error": "fromSemester and toSemester must be numbers."}, status=400)

    output_dir = Path(settings.BASE_DIR) / "scraped_text"
    output_dir.mkdir(parents=True, exist_ok=True)
    txt_output_file = output_dir / "latest_scrape.txt"

    if from_semester > to_semester:
        return JsonResponse({"error": "fromSemester cannot be greater than toSemester."}, status=400)

    source_url = url
    if use_latest_scrape:
        if not txt_output_file.exists():
            return JsonResponse(
                {"error": "latest_scrape.txt was not found. Run one live scrape first or provide URL mode."},
                status=400,
            )

        text = txt_output_file.read_text(encoding="utf-8").strip()[:20000]
        if not text:
            return JsonResponse({"error": "latest_scrape.txt is empty."}, status=400)

        source_url = source_url or "latest_scrape.txt"
    else:
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
            except requests.exceptions.SSLError:
                # Retry once without certificate verification for environments
                # that use TLS interception certificates.
                try:
                    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
                    response = requests.get(url, timeout=10, verify=False)
                    response.raise_for_status()
                    break
                except requests.RequestException as insecure_error:
                    return JsonResponse(
                        {
                            "error": (
                                "SSL certificate validation failed and insecure retry also failed: "
                                f"{insecure_error}"
                            )
                        },
                        status=400,
                    )
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

        # Keep prompt size moderate so extraction returns faster.
        text = soup.get_text(separator=" ", strip=True)[:20000]
        txt_output_file.write_text(text, encoding="utf-8")

    prompt = (
        "Extract only study subject names from semesters "
        f"{from_semester} to {to_semester} from the provided webpage text. "
        "Do not translate or modify original subject text. "
        "Return strict JSON only in this format: "
        '{"study_subjects": ["subject 1", "subject 2"]}. '
        "No markdown, no explanation.\n\n"
        f"Webpage text:\n{text}"
    )

    try:
        ai_start = time.perf_counter()
        ollama_http = requests.post(
            "http://localhost:11434/api/chat",
            json={
                "model": "llama3",
                "messages": [{"role": "user", "content": prompt}],
                "options": {"temperature": 0, "num_predict": 300},
                "stream": False,
            },
            timeout=300,
        )
        ollama_http.raise_for_status()
        ai_seconds = round(time.perf_counter() - ai_start, 2)
    except requests.Timeout:
        return JsonResponse(
            {"error": "AI extraction timed out after 5 minutes. The llama3 model is slow on CPU — consider using a smaller model like llama3.2:1b."},
            status=504,
        )
    except requests.RequestException as exc:
        return JsonResponse({"error": f"Ollama HTTP request failed: {exc}"}, status=500)

    raw_content = ollama_http.json().get("message", {}).get("content", "").strip()

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
        "url": source_url,
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
            "source": "latest_scrape.txt" if use_latest_scrape else "live_url",
            "url": source_url,
            "characters": len(text),
            "ai_seconds": ai_seconds,
            "subjects_count": len(subjects),
            "study_subjects": subjects,
        }
    )


@csrf_exempt
def save_subject_ratings(request):
    if request.method != "POST":
        return JsonResponse({"error": "Only POST is allowed."}, status=405)

    try:
        payload = json.loads(request.body.decode("utf-8") or "{}")
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON body."}, status=400)

    rows = payload.get("rows", [])
    if not isinstance(rows, list):
        return JsonResponse({"error": "'rows' must be a list."}, status=400)

    output_dir = Path(settings.BASE_DIR) / "scraped_text"
    output_dir.mkdir(parents=True, exist_ok=True)
    ratings_file = output_dir / "latest_subject_ratings.txt"

    lines = []
    for row in rows:
        semester = row.get("semester", "")
        subject = str(row.get("subject", "")).strip()
        try:
            stars = int(row.get("stars", 0))
        except (TypeError, ValueError):
            stars = 0
        if subject:
            lines.append(f"Semester {semester} | {subject} | Stars: {stars}")

    ratings_file.write_text("\n".join(lines), encoding="utf-8")

    return JsonResponse({"message": f"Saved {len(lines)} ratings.", "count": len(lines)})
# noop commit marker
