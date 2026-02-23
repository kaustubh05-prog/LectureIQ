import logging
from typing import List

from app.config import settings

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Hardcoded documentation map — topic keyword → official doc URL
# ---------------------------------------------------------------------------
DOC_MAP = {
    "python": ("Python Official Docs", "https://docs.python.org/3/"),
    "javascript": ("MDN JavaScript Guide", "https://developer.mozilla.org/en-US/docs/Web/JavaScript"),
    "react": ("React Official Docs", "https://react.dev/"),
    "java": ("Java SE Docs", "https://docs.oracle.com/en/java/"),
    "c++": ("C++ Reference", "https://en.cppreference.com/"),
    "django": ("Django Docs", "https://docs.djangoproject.com/"),
    "fastapi": ("FastAPI Docs", "https://fastapi.tiangolo.com/"),
    "numpy": ("NumPy Docs", "https://numpy.org/doc/stable/"),
    "pandas": ("Pandas Docs", "https://pandas.pydata.org/docs/"),
    "scikit-learn": ("scikit-learn Docs", "https://scikit-learn.org/stable/"),
    "tensorflow": ("TensorFlow API Docs", "https://www.tensorflow.org/api_docs"),
    "pytorch": ("PyTorch Docs", "https://pytorch.org/docs/stable/"),
    "sql": ("SQL Tutorial — W3Schools", "https://www.w3schools.com/sql/"),
    "html": ("MDN HTML Guide", "https://developer.mozilla.org/en-US/docs/Web/HTML"),
    "css": ("MDN CSS Guide", "https://developer.mozilla.org/en-US/docs/Web/CSS"),
    "machine learning": ("scikit-learn User Guide", "https://scikit-learn.org/stable/user_guide.html"),
    "data structures": ("GeeksforGeeks — DSA", "https://www.geeksforgeeks.org/data-structures/"),
    "algorithms": ("GeeksforGeeks — Algorithms", "https://www.geeksforgeeks.org/fundamentals-of-algorithms/"),
    "calculus": ("Paul's Online Math Notes", "https://tutorial.math.lamar.edu/"),
    "linear algebra": ("Khan Academy — Linear Algebra", "https://www.khanacademy.org/math/linear-algebra"),
    "probability": ("Khan Academy — Statistics", "https://www.khanacademy.org/math/statistics-probability"),
    "os": ("Operating Systems — OSTEP", "https://pages.cs.wisc.edu/~remzi/OSTEP/"),
    "networking": ("Computer Networking — Kurose", "https://gaia.cs.umass.edu/kurose_ross/"),
    "database": ("PostgreSQL Docs", "https://www.postgresql.org/docs/"),
    "git": ("Git Official Docs", "https://git-scm.com/doc"),
    "docker": ("Docker Docs", "https://docs.docker.com/"),
}

# ---------------------------------------------------------------------------
# Practice problems map
# ---------------------------------------------------------------------------
PRACTICE_MAP = {
    "data structures": ("DSA Practice — LeetCode", "https://leetcode.com/explore/learn/"),
    "algorithms": ("Algorithm Problems — LeetCode", "https://leetcode.com/problemset/"),
    "sorting": ("Sorting Problems — LeetCode", "https://leetcode.com/tag/sorting/"),
    "dynamic programming": ("DP Problems — LeetCode", "https://leetcode.com/tag/dynamic-programming/"),
    "graph": ("Graph Problems — LeetCode", "https://leetcode.com/tag/graph/"),
    "tree": ("Tree Problems — LeetCode", "https://leetcode.com/tag/tree/"),
    "binary search": ("Binary Search — LeetCode", "https://leetcode.com/tag/binary-search/"),
    "linked list": ("Linked List — LeetCode", "https://leetcode.com/tag/linked-list/"),
    "recursion": ("Recursion Problems — LeetCode", "https://leetcode.com/tag/recursion/"),
    "array": ("Array Problems — LeetCode", "https://leetcode.com/tag/array/"),
    "string": ("String Problems — LeetCode", "https://leetcode.com/tag/string/"),
    "math": ("Math Problems — LeetCode", "https://leetcode.com/tag/math/"),
    "python": ("Python Practice — HackerRank", "https://www.hackerrank.com/domains/python"),
    "sql": ("SQL Practice — HackerRank", "https://www.hackerrank.com/domains/sql"),
}


def _get_youtube_client():
    key = settings.youtube_api_key
    if not key or key in ("your_youtube_api_key", "AIzaYOUR_KEY", ""):
        return None
    try:
        from googleapiclient.discovery import build
        return build("youtube", "v3", developerKey=key)
    except Exception as e:
        logger.warning("YouTube client build failed: %s", e)
        return None


def find_youtube_videos(topic: str, max_results: int = 2) -> List[dict]:
    youtube = _get_youtube_client()
    if not youtube:
        return []

    try:
        from googleapiclient.errors import HttpError
        response = youtube.search().list(
            part="snippet",
            q=f"{topic} tutorial explained",
            maxResults=max_results + 2,
            type="video",
            videoCategoryId="27",    # Education
            order="relevance",
            relevanceLanguage="en",
        ).execute()

        results = []
        for item in response.get("items", []):
            video_id = item.get("id", {}).get("videoId")
            if not video_id:
                continue
            snippet = item["snippet"]
            results.append({
                "type": "youtube",
                "title": snippet.get("title", "")[:200],
                "url": f"https://www.youtube.com/watch?v={video_id}",
                "thumbnail_url": snippet.get("thumbnails", {}).get("medium", {}).get("url"),
                "topic": topic,
                "relevance_score": 1.0,
            })
            if len(results) >= max_results:
                break

        logger.info("YouTube: %d videos for '%s'", len(results), topic)
        return results

    except Exception as e:
        logger.warning("YouTube search failed for '%s': %s", topic, e)
        return []


def find_documentation(topic: str) -> List[dict]:
    topic_lower = topic.lower()
    results = []
    for keyword, (title, url) in DOC_MAP.items():
        if keyword in topic_lower or topic_lower in keyword:
            results.append({
                "type": "documentation",
                "title": title,
                "url": url,
                "thumbnail_url": None,
                "topic": topic,
                "relevance_score": 0.9,
            })
    return results[:1]


def find_practice_problems(topic: str) -> List[dict]:
    topic_lower = topic.lower()
    results = []
    for keyword, (title, url) in PRACTICE_MAP.items():
        if keyword in topic_lower or topic_lower in keyword:
            results.append({
                "type": "practice",
                "title": title,
                "url": url,
                "thumbnail_url": None,
                "topic": topic,
                "relevance_score": 0.8,
            })
    return results[:1]


def get_resources_for_topics(topics: List[str], max_total: int = 5) -> List[dict]:
    """
    Fetch YouTube + docs + practice resources for the top topics.
    Returns a deduplicated list capped at max_total.
    """
    all_resources: List[dict] = []
    seen_urls: set = set()

    for topic in topics[:3]:     # cap at 3 topics to preserve YouTube quota
        for resource in [
            *find_youtube_videos(topic),
            *find_documentation(topic),
            *find_practice_problems(topic),
        ]:
            if resource["url"] not in seen_urls:
                all_resources.append(resource)
                seen_urls.add(resource["url"])

        if len(all_resources) >= max_total:
            break

    # Sort by relevance
    all_resources.sort(key=lambda r: r["relevance_score"], reverse=True)
    return all_resources[:max_total]
