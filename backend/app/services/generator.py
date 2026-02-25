import json
import logging
import re
from typing import List

from groq import Groq

from app.config import settings

logger = logging.getLogger(__name__)

_client = Groq(api_key=settings.groq_api_key)
MODEL = "llama-3.3-70b-versatile"

# Transcript character limits to avoid token overflows
NOTES_LIMIT = 8000
CARDS_LIMIT = 6000
CONCEPT_LIMIT = 3000


# ---------------------------------------------------------------------------
# Core Groq caller
# ---------------------------------------------------------------------------

def _call_groq(prompt: str, max_tokens: int = 4096, temperature: float = 0.3) -> str:
    response = _client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=max_tokens,
        temperature=temperature,
    )
    return response.choices[0].message.content.strip()


def _extract_json(text: str) -> str:
    """Pull out the first JSON array or object from a response string."""
    match = re.search(r"\[[\s\S]*\]", text)
    if match:
        return match.group(0)
    match = re.search(r"\{[\s\S]*\}", text)
    if match:
        return match.group(0)
    return text


# ---------------------------------------------------------------------------
# Notes
# ---------------------------------------------------------------------------

def generate_notes(transcript: str) -> str:
    """Generate structured Markdown notes from a transcript."""
    prompt = f"""You are an expert academic note-taker for college students in India.

Given the lecture transcript below, write comprehensive, well-structured study notes in Markdown.

Requirements:
- Use clear hierarchical headers (##, ###)
- Bullet points for key concepts and sub-points
- Bold (**text**) for definitions and important terms
- Format math expressions in LaTeX: inline $x^2$ or block $$E=mc^2$$
- Code snippets in fenced code blocks with language tag
- Keep the logical flow of the original lecture
- Be thorough but concise — a student should be able to revise from these notes alone

TRANSCRIPT:
{transcript[:NOTES_LIMIT]}

---
Generate Markdown notes now:"""

    try:
        return _call_groq(prompt, max_tokens=4000, temperature=0.2)
    except Exception as e:
        logger.error("Notes generation failed: %s", e)
        return (
            "# Lecture Notes\n\n"
            "> ⚠️ Notes could not be generated automatically. "
            "Please re-process this lecture.\n\n"
            f"**Error:** `{e}`"
        )


# ---------------------------------------------------------------------------
# Flashcards
# ---------------------------------------------------------------------------

def generate_flashcards(transcript: str, count: int = 12) -> List[dict]:
    """Return a list of {question, answer} dicts."""
    prompt = f"""You are an expert educator creating study flashcards for college students.

Based on the lecture transcript below, create exactly {count} high-quality flashcards.

Rules:
- Cover key definitions, theorems, formulas, concepts, and important facts
- Questions must be clear and specific (no vague questions like "What is important?")
- Answers should be concise but complete (2–4 sentences)
- Vary question types: "What is...", "How does...", "Why...", "Compare...", "Define..."

Return ONLY a valid JSON array, no markdown, no extra text:
[
  {{"question": "...", "answer": "..."}},
  {{"question": "...", "answer": "..."}}
]

TRANSCRIPT:
{transcript[:CARDS_LIMIT]}

JSON array ({count} flashcards):"""

    try:
        raw = _call_groq(prompt, max_tokens=3000, temperature=0.4)
        cards = json.loads(_extract_json(raw))
        if isinstance(cards, list):
            valid = [
                {"question": c["question"].strip(), "answer": c["answer"].strip()}
                for c in cards
                if isinstance(c, dict) and c.get("question") and c.get("answer")
            ]
            if valid:
                return valid[:15]
    except Exception as e:
        logger.error("Flashcard parsing failed: %s", e)

    return [{"question": "Flashcard generation failed.", "answer": "Please re-process this lecture."}]


# ---------------------------------------------------------------------------
# MCQs
# ---------------------------------------------------------------------------

def generate_mcqs(transcript: str, count: int = 8) -> List[dict]:
    """Return a list of {question, options, correct_index, explanation} dicts."""
    prompt = f"""You are an expert exam question writer for college students in India.

Based on the lecture transcript below, create exactly {count} multiple-choice questions (MCQs).

Rules:
- Test conceptual understanding, not just memorization
- Exactly 4 options (index 0–3), exactly one correct answer
- Distractors should be plausible but clearly wrong on reflection
- Include a detailed explanation (2–3 sentences) for the correct answer
- Mix easy, medium, and hard questions

Return ONLY a valid JSON array, no markdown, no extra text:
[
  {{
    "question": "...",
    "options": ["option A", "option B", "option C", "option D"],
    "correct_index": 1,
    "explanation": "..."
  }}
]

TRANSCRIPT:
{transcript[:CARDS_LIMIT]}

JSON array ({count} MCQs):"""

    try:
        raw = _call_groq(prompt, max_tokens=3000, temperature=0.4)
        mcqs = json.loads(_extract_json(raw))
        if isinstance(mcqs, list):
            valid = []
            for m in mcqs:
                if (
                    isinstance(m, dict) and
                    m.get("question") and
                    isinstance(m.get("options"), list) and
                    len(m["options"]) == 4 and
                    isinstance(m.get("correct_index"), int) and
                    0 <= m["correct_index"] <= 3 and
                    m.get("explanation")
                ):
                    valid.append({
                        "question": m["question"].strip(),
                        "options": [str(o).strip() for o in m["options"]],
                        "correct_index": m["correct_index"],
                        "explanation": m["explanation"].strip(),
                    })
            if valid:
                return valid[:10]
    except Exception as e:
        logger.error("MCQ parsing failed: %s", e)

    return [{
        "question": "MCQ generation failed for this lecture.",
        "options": ["Re-process", "Contact support", "Try again", "All of the above"],
        "correct_index": 3,
        "explanation": "MCQ generation failed. Please try re-processing this lecture.",
    }]


# ---------------------------------------------------------------------------
# Key concept extraction (used for resource linking)
# ---------------------------------------------------------------------------

def extract_key_concepts(transcript: str) -> List[str]:
    """Return 5–8 searchable topic strings for YouTube/docs lookup."""
    prompt = f"""Extract the 5–8 most important, specific, searchable topics from this lecture transcript.

Rules:
- Return a JSON array of short strings (2–5 words each)
- Be specific: "binary search tree" not "trees"
- Focus on things a student would Google to learn more
- Avoid generic terms like "introduction" or "overview"

TRANSCRIPT:
{transcript[:CONCEPT_LIMIT]}

Return ONLY a JSON array:"""

    try:
        raw = _call_groq(prompt, max_tokens=400, temperature=0.2)
        concepts = json.loads(_extract_json(raw))
        if isinstance(concepts, list):
            return [str(c).strip() for c in concepts if c][:8]
    except Exception as e:
        logger.error("Concept extraction failed: %s", e)

    return []
