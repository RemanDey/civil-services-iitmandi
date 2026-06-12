# Backend-Driven Quiz Module Documentation

## Overview
The Civil Services IIT Mandi website features a robust backend-driven quiz system that fetches UPSC previous year questions (PYQs) and provides fallback quiz content for exam preparation.

## Architecture

### Components

#### 1. **quizzes_module.py** - Backend Quiz Engine
The main module that handles all quiz data retrieval logic.

**Main Function:**
```python
get_quizzes(force_refresh=False, limit=10)
```

**Returns:** List of question dictionaries

**Question Structure:**
```python
{
    "id": "upsc-2024-gs1-5",           # Unique identifier
    "q": "Question text here?",         # The actual question
    "options": ["A", "B", "C", "D"],   # 4 multiple choice options
    "correct": 2,                       # 0-3 index of correct answer
    "source": "UPSC Civil Services...", # Source attribution
    "source_url": "https://...",       # Link to source material
    "year": 2024,                       # Year of examination
    "paper": "General Studies",         # Paper name
    "explanation": "Optional..."        # Optional explanation
}
```

#### 2. **Data Sources** (Priority Order)

1. **Official UPSC Sources (Primary)**
   - Question Papers: `https://www.upsc.gov.in/examinations/previous-question-papers`
   - Answer Keys: `https://www.upsc.gov.in/examinations/answer-key/archives`
   - Integrated with `pyq_module.py` for PYQ data

2. **Fallback Questions (10 curated MCQs)**
   - Served when official sources are unavailable
   - Covers key exam topics:
     - Constitutional amendments
     - Monetary policy
     - Environmental conservation
     - Modern Indian history
     - Geography
     - Science basics
     - International relations

#### 3. **Caching Strategy**
- **TTL:** 6 hours (`CACHE_TTL = timedelta(hours=6)`)
- **Storage:** In-memory dictionary `_cache`
- **Cache Key:** Stores `fetched_at` timestamp and `questions` list
- **Force Refresh:** Use `get_quizzes(force_refresh=True)` to bypass cache

### Workflow

```
Request to /quizzes
    ↓
app.py calls quizzes_module.get_quizzes()
    ↓
Check cache (if fresh and not force_refresh)
    ├─→ Cache hit: Return cached questions
    └─→ Cache miss: Proceed to fetching
    ↓
Attempt to fetch official UPSC questions
    ├─→ Success: Parse PDFs and extract questions
    └─→ Failure: Continue to fallback
    ↓
Merge with fallback questions if needed
    ↓
Deduplicate and validate
    ↓
Cache result (6-hour TTL)
    ↓
Return up to 'limit' questions
    ↓
Template renders with {{ questions|tojson }}
```

## Implementation Details

### Key Functions

#### `get_quizzes(force_refresh=False, limit=DEFAULT_LIMIT)`
Main public API that returns quiz questions.

```python
# Default usage (10 fallback questions from cache if fresh)
questions = quizzes_module.get_quizzes()

# Force fresh data from official sources
questions = quizzes_module.get_quizzes(force_refresh=True)

# Custom limit
questions = quizzes_module.get_quizzes(limit=20)
```

#### Private Functions

- `_fetch(url)` - HTTP request with timeout and headers
- `_extract_pdf_text(url)` - Extract text from PDF using `pypdf`
- `_official_gs_paper_links()` - Get GS Paper I links from `pyq_module`
- `_official_answer_key_links()` - Scrape UPSC answer key archive
- `_parse_answer_key(text)` - Extract question-answer mappings from PDF
- `_parse_questions(text, year, paper, source_url)` - Parse question blocks from text
- `_parse_question_block()` - Extract individual question with 4 options
- `_valid_question()` - Validate question structure
- `_dedupe_questions()` - Remove duplicate questions
- `_get_official_questions()` - Main fetching logic for official sources
- `_fallback()` - Return curated fallback questions

### Error Handling

**Graceful Degradation:**
1. If PDF parsing fails for a year → Skip and try next year
2. If all official sources fail → Use all 10 fallback questions
3. If fallback questions run out → Return whatever valid questions exist
4. If no valid questions exist → Return empty list (fallback applies)

**Warning Messages:**
```
Warning: could not parse UPSC quiz PDFs for {year}: {error}
Warning: could not refresh official quiz questions: {error}
```

### Dependencies

```txt
Flask                 # Web framework
gunicorn             # WSGI server
requests             # HTTP library
beautifulsoup4       # HTML/XML parsing
pypdf                # PDF text extraction
```

**Note:** `pypdf` must be installed for PDF parsing. If missing, module gracefully falls back to hardcoded questions.

## Flask Integration

### Route Configuration
```python
# app.py
@app.route('/quizzes')
def quizzes():
    """Renders the Quizzes landing page."""
    questions = quizzes_module.get_quizzes()
    return render_template('quizzes.html', questions=questions)
```

### Template Rendering
```html
<!-- templates/quizzes.html -->
{% block scripts %}
<script>
    const questions = {{ questions|tojson }};
    // JavaScript UI logic follows
</script>
{% endblock %}
```

## Frontend Behavior

### User Interaction Flow

1. **Page Load**
   - Template receives 10 questions from backend
   - Questions serialized as JSON in JavaScript

2. **Answering**
   - Click option button
   - Immediately reveals if correct/incorrect
   - Highlights correct answer in green
   - Shows incorrect selection in red
   - Displays explanation and source link

3. **Navigation**
   - "Previous" / "Next" buttons navigate questions
   - Submit button appears on last question

4. **Results**
   - Final score modal shows
   - Score displays as X/10
   - "Retry Assessment" reloads page

## Testing

### Run Tests
```bash
python3 test_quizzes.py
```

### Test Coverage
- ✅ Module returns valid question lists
- ✅ Questions respect limit parameter
- ✅ All questions have required fields
- ✅ Questions have exactly 4 options
- ✅ Correct answer index is valid (0-3)
- ✅ Flask route returns 200 status
- ✅ Template receives JSON
- ✅ No duplicate questions
- ✅ Cache TTL works correctly
- ✅ Fallback questions available

## Deployment

### Prerequisites
```bash
pip install -r requirements.txt
```

### Running Locally
```bash
python3 app.py
# Visits http://localhost:5000/quizzes
```

### Production (with Gunicorn)
```bash
gunicorn app:app --bind 0.0.0.0:5000
```

## Monitoring & Debugging

### Check Cache Status
```python
import quizzes_module
print(quizzes_module._cache)
# Shows: {'fetched_at': datetime, 'questions': [...]}
```

### Clear Cache Manually
```python
quizzes_module._cache = {"fetched_at": None, "questions": []}
```

### Force Refresh Questions
```python
questions = quizzes_module.get_quizzes(force_refresh=True)
```

### Enable Debug Output
```python
# Modify _get_official_questions() to add logging
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Future Enhancements

1. **Database Integration**
   - Replace in-memory cache with Redis or database
   - Enable cross-server cache sharing

2. **Question Difficulty Levels**
   - Filter questions by difficulty
   - Suggest questions based on performance

3. **User Analytics**
   - Track quiz attempts and scores
   - Generate performance reports

4. **Drishti Integration**
   - Add public (non-login) Drishti quiz content when available
   - Current implementation skips authenticated content

5. **Smart Caching**
   - Intelligent TTL based on update frequency
   - Fetch new questions daily at specific times

6. **Answer Explanations**
   - Link to detailed explanation articles
   - Suggest related study materials

## Troubleshooting

### Issue: "pypdf is not installed"
**Solution:** Install pypdf
```bash
pip install pypdf
```

### Issue: Fallback questions showing instead of official
**Reason:** Network issues, PDF parsing failure, or UPSC site structure change
**Solution:** 
1. Check internet connection
2. Verify UPSC URLs are still accessible
3. Check PDF structure hasn't changed
4. Review error logs

### Issue: Same questions every time
**Reason:** Cache is working as intended
**Solution:** 
```python
# Force refresh for testing
questions = quizzes_module.get_quizzes(force_refresh=True)
```

### Issue: Quiz page doesn't load
**Solution:**
1. Check Flask logs: `python3 app.py` (verbose output)
2. Verify `quizzes_module.py` syntax: `python3 -m py_compile quizzes_module.py`
3. Test module directly: `python3 -c "import quizzes_module; quizzes_module.get_quizzes()"`

## Performance Notes

- **First load:** May take 5-30 seconds if fetching official PDFs
- **Cached loads:** <100ms
- **PDF parsing time:** 10-15 seconds per paper (depends on size)
- **Network timeout:** 25 seconds per request

## License & Attribution

- Official UPSC questions: Government of India
- Fallback questions: Curated for educational purposes
- Source attribution maintained for all questions
