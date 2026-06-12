"""Runtime scraper for UPSC-focused quiz questions."""

from datetime import datetime, timedelta
from io import BytesIO
import re
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

import pyq_module

try:
    from pypdf import PdfReader
except ImportError:  # pragma: no cover - exercised only before dependencies install
    PdfReader = None


UPSC_ANSWER_KEY_ARCHIVE_URL = "https://www.upsc.gov.in/examinations/answer-key/archives"
CACHE_TTL = timedelta(hours=6)
DEFAULT_LIMIT = 10

fallback_questions = [
    {
        "id": "fallback-polity-73rd",
        "q": "Which constitutional amendment gave constitutional status to Panchayati Raj institutions?",
        "options": [
            "71st Constitutional Amendment",
            "73rd Constitutional Amendment",
            "74th Constitutional Amendment",
            "86th Constitutional Amendment",
        ],
        "correct": 1,
        "source": "Curated fallback: Indian Polity",
        "source_url": "https://www.india.gov.in/my-government/constitution-india",
        "year": "",
        "paper": "General Studies",
        "explanation": "The 73rd Constitutional Amendment Act, 1992 added Part IX and the Eleventh Schedule for Panchayats.",
    },
    {
        "id": "fallback-polity-basic-structure",
        "q": "The Basic Structure Doctrine was laid down by the Supreme Court in which case?",
        "options": [
            "Golaknath v. State of Punjab",
            "Minerva Mills v. Union of India",
            "Kesavananda Bharati v. State of Kerala",
            "Maneka Gandhi v. Union of India",
        ],
        "correct": 2,
        "source": "Curated fallback: Indian Polity",
        "source_url": "https://main.sci.gov.in/",
        "year": "",
        "paper": "General Studies",
        "explanation": "Kesavananda Bharati is the landmark 1973 judgment associated with the Basic Structure Doctrine.",
    },
    {
        "id": "fallback-economy-mpc",
        "q": "Which institution is responsible for monetary policy implementation in India?",
        "options": [
            "Finance Commission of India",
            "Reserve Bank of India",
            "Securities and Exchange Board of India",
            "NITI Aayog",
        ],
        "correct": 1,
        "source": "Curated fallback: Indian Economy",
        "source_url": "https://www.rbi.org.in/",
        "year": "",
        "paper": "General Studies",
        "explanation": "The Reserve Bank of India conducts monetary policy under the RBI Act framework.",
    },
    {
        "id": "fallback-environment-ramsar",
        "q": "The Ramsar Convention is primarily associated with the conservation of which ecosystem?",
        "options": ["Wetlands", "Coral reefs", "Tropical forests", "Grasslands"],
        "correct": 0,
        "source": "Curated fallback: Environment",
        "source_url": "https://www.ramsar.org/",
        "year": "",
        "paper": "General Studies",
        "explanation": "The Ramsar Convention is the international treaty for conservation and wise use of wetlands.",
    },
    {
        "id": "fallback-history-cabinet-mission",
        "q": "The Cabinet Mission Plan was announced in which year?",
        "options": ["1942", "1945", "1946", "1947"],
        "correct": 2,
        "source": "Curated fallback: Modern India",
        "source_url": "https://www.indiaculture.gov.in/",
        "year": "",
        "paper": "General Studies",
        "explanation": "The Cabinet Mission came to India in 1946 to discuss constitutional transfer of power.",
    },
    {
        "id": "fallback-geography-latitude",
        "q": "Which important latitude passes through the middle of India?",
        "options": ["Equator", "Tropic of Cancer", "Tropic of Capricorn", "Arctic Circle"],
        "correct": 1,
        "source": "Curated fallback: Geography",
        "source_url": "https://surveyofindia.gov.in/",
        "year": "",
        "paper": "General Studies",
        "explanation": "The Tropic of Cancer passes through eight Indian states.",
    },
    {
        "id": "fallback-polity-article-32",
        "q": "Article 32 of the Constitution of India is related to which of the following?",
        "options": [
            "Election of the President",
            "Right to Constitutional Remedies",
            "Official language of the Union",
            "Emergency provisions",
        ],
        "correct": 1,
        "source": "Curated fallback: Indian Polity",
        "source_url": "https://www.india.gov.in/my-government/constitution-india",
        "year": "",
        "paper": "General Studies",
        "explanation": "Article 32 allows individuals to move the Supreme Court for enforcement of Fundamental Rights.",
    },
    {
        "id": "fallback-economy-gst",
        "q": "GST in India is administered through which constitutional body?",
        "options": ["GST Council", "Finance Commission", "NITI Aayog", "Public Accounts Committee"],
        "correct": 0,
        "source": "Curated fallback: Indian Economy",
        "source_url": "https://gstcouncil.gov.in/",
        "year": "",
        "paper": "General Studies",
        "explanation": "The GST Council makes recommendations on GST rates, exemptions, and related policy.",
    },
    {
        "id": "fallback-science-dna",
        "q": "DNA is primarily responsible for which biological function?",
        "options": [
            "Storage and transmission of genetic information",
            "Transport of oxygen in blood",
            "Digestion of carbohydrates",
            "Regulation of body temperature",
        ],
        "correct": 0,
        "source": "Curated fallback: General Science",
        "source_url": "https://ncert.nic.in/",
        "year": "",
        "paper": "General Studies",
        "explanation": "DNA carries hereditary information used in growth, reproduction, and functioning of organisms.",
    },
    {
        "id": "fallback-ir-unsc",
        "q": "Which of the following is a permanent member of the United Nations Security Council?",
        "options": ["India", "Brazil", "Japan", "France"],
        "correct": 3,
        "source": "Curated fallback: International Relations",
        "source_url": "https://www.un.org/securitycouncil/",
        "year": "",
        "paper": "General Studies",
        "explanation": "France is one of the five permanent members of the UN Security Council.",
    },
]

_cache = {"fetched_at": None, "questions": []}


def _fetch(url):
    response = requests.get(
        url,
        timeout=25,
        headers={"User-Agent": "CivilServicesIITMandi/1.0"},
    )
    response.raise_for_status()
    return response


def _clean_text(value):
    return " ".join(value.split())


def _extract_pdf_text(url):
    if PdfReader is None:
        raise RuntimeError("pypdf is not installed")

    reader = PdfReader(BytesIO(_fetch(url).content))
    return "\n".join(page.extract_text() or "" for page in reader.pages)


def _official_gs_paper_links(force_refresh=False):
    links = []
    for paper in pyq_module.get_pyqs(force_refresh=force_refresh):
        exam = paper.get("exam", "")
        title = paper.get("paper", "")
        if "Civil Services (Preliminary)" not in exam:
            continue
        if "General Studies" not in title or "Paper" not in title:
            continue
        if "II" in title or "CSAT" in title.upper():
            continue

        links.append(paper)

    return sorted(links, key=lambda item: item.get("year", 0), reverse=True)


def _official_answer_key_links():
    soup = BeautifulSoup(_fetch(UPSC_ANSWER_KEY_ARCHIVE_URL).text, "html.parser")
    answer_keys = {}

    for row in soup.select(".view-content tr"):
        cells = row.find_all("td")
        if len(cells) < 2:
            continue

        exam_text = _clean_text(cells[0].get_text(" ", strip=True))
        if "Civil Services (Preliminary)" not in exam_text:
            continue

        year_match = re.search(r"\b(20\d{2})\b", exam_text)
        if not year_match:
            continue

        for item in cells[1].select("li"):
            item_text = _clean_text(item.get_text(" ", strip=True))
            link = item.find("a", href=True)
            if not link:
                continue
            if "General Studies Paper - I" in item_text or "General Studies Paper I" in item_text:
                answer_keys[int(year_match.group(1))] = urljoin(UPSC_ANSWER_KEY_ARCHIVE_URL, link["href"])

    return answer_keys


def _parse_answer_key(text):
    answers = {}
    normalized = re.sub(r"\s+", " ", text)

    for match in re.finditer(r"(?<!\d)(\d{1,3})\s*[\.\)]?\s*([A-Da-d])\b", normalized):
        question_no = int(match.group(1))
        if 1 <= question_no <= 200:
            answers[question_no] = ord(match.group(2).upper()) - ord("A")

    return answers


def _strip_question_prefix(block):
    return re.sub(r"^\s*\d{1,3}\s*[\.\)]\s*", "", block).strip()


def _parse_question_block(question_no, block, year, paper, source_url):
    option_matches = list(re.finditer(r"(?:^|\n)\s*\(?([a-dA-D])\)?[\.\)]?\s+", block))
    if len(option_matches) < 4:
        return None

    first_option = option_matches[0]
    question_text = _clean_text(_strip_question_prefix(block[: first_option.start()]))
    if len(question_text) < 20:
        return None

    options = []
    for idx, match in enumerate(option_matches[:4]):
        start = match.end()
        end = option_matches[idx + 1].start() if idx < 3 else len(block)
        option_text = _clean_text(block[start:end])
        option_text = re.sub(r"\s*(?:\d{1,3}\s*[\.\)]\s*)?$", "", option_text).strip()
        if not option_text:
            return None
        options.append(option_text)

    return {
        "id": f"upsc-{year}-gs1-{question_no}",
        "q": question_text,
        "options": options,
        "correct": None,
        "source": f"UPSC Civil Services Preliminary {year}",
        "source_url": source_url,
        "year": year,
        "paper": paper,
        "explanation": "Answer matched with the official UPSC answer key.",
        "question_no": question_no,
    }


def _parse_questions(text, year, paper, source_url):
    question_starts = list(re.finditer(r"(?:^|\n)\s*(\d{1,3})\s*[\.\)]\s+", text))
    questions = []

    for index, match in enumerate(question_starts):
        question_no = int(match.group(1))
        if not 1 <= question_no <= 200:
            continue

        end = question_starts[index + 1].start() if index + 1 < len(question_starts) else len(text)
        parsed = _parse_question_block(question_no, text[match.start() : end], year, paper, source_url)
        if parsed:
            questions.append(parsed)

    return questions


def _valid_question(question):
    return (
        isinstance(question.get("options"), list)
        and len(question["options"]) == 4
        and isinstance(question.get("correct"), int)
        and 0 <= question["correct"] < 4
        and bool(question.get("q"))
    )


def _dedupe_questions(questions):
    deduped = []
    seen = set()
    for question in questions:
        key = _clean_text(question.get("q", "")).lower()
        if not key or key in seen:
            continue
        seen.add(key)
        deduped.append(question)
    return deduped


def _get_official_questions(force_refresh=False):
    answer_keys = _official_answer_key_links()
    questions = []

    for paper in _official_gs_paper_links(force_refresh=force_refresh):
        year = paper["year"]
        answer_key_url = answer_keys.get(year)
        if not answer_key_url:
            continue

        try:
            answers = _parse_answer_key(_extract_pdf_text(answer_key_url))
            parsed_questions = _parse_questions(
                _extract_pdf_text(paper["link"]),
                year,
                paper["paper"],
                paper["link"],
            )
        except Exception as exc:
            print(f"Warning: could not parse UPSC quiz PDFs for {year}: {exc}")
            continue

        for question in parsed_questions:
            correct = answers.get(question.pop("question_no"))
            if correct is None:
                continue
            question["correct"] = correct
            questions.append(question)

        if len(questions) >= DEFAULT_LIMIT:
            break

    return _dedupe_questions([question for question in questions if _valid_question(question)])


def _fallback(limit):
    return fallback_questions[:limit]


def get_quizzes(force_refresh=False, limit=DEFAULT_LIMIT):
    """Return quiz questions, using official UPSC sources when available."""
    now = datetime.utcnow()
    cache_is_fresh = (
        _cache["fetched_at"] is not None
        and now - _cache["fetched_at"] < CACHE_TTL
        and _cache["questions"]
    )

    if cache_is_fresh and not force_refresh:
        return _cache["questions"][:limit]

    try:
        questions = _get_official_questions(force_refresh=force_refresh)
    except Exception as exc:
        print(f"Warning: could not refresh official quiz questions: {exc}")
        questions = []

    if len(questions) < limit:
        questions.extend(_fallback(limit - len(questions)))

    questions = _dedupe_questions([question for question in questions if _valid_question(question)])
    if not questions:
        questions = _fallback(limit)

    _cache["fetched_at"] = now
    _cache["questions"] = questions
    return questions[:limit]
