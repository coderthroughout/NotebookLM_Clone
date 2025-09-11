import os
import json
from typing import List, Dict, Any, Optional, Tuple
import requests
from dotenv import load_dotenv

load_dotenv()

class QuestionAPIClient:
    """Client for fetching questions from the external database API"""
    def __init__(self) -> None:
        self.base_url = "http://65.1.219.251:7002/api/questions"
        self.headers = {"Content-Type": "application/json"}
        self.allowed_qids = self._load_allowed_qids()

    def _load_allowed_qids(self) -> List[str]:
        env_qids = os.getenv("ALLOWED_QIDS")
        if env_qids:
            return [qid.strip() for qid in env_qids.split(",") if qid.strip()]
        qids_file = os.getenv("ALLOWED_QIDS_FILE", "config/allowed_qids.txt")
        if os.path.exists(qids_file):
            with open(qids_file, "r", encoding="utf-8") as f:
                return [line.strip() for line in f if line.strip()]
        return [
            "168427", "655546", "659338", "704507", "534447", "652758",
            "652834", "472717", "704497", "57475", "600010", "651377",
            "650574", "237867", "651217", "704527", "653178", "650327",
            "472160", "650341", "57308", "576954", "652438", "704565",
            "10235", "650539", "652412", "531437", "653220", "704575",
            "652718", "467416", "650530", "601490", "484432", "665813",
            "704541", "704500", "533101", "479838", "653185", "653163",
            "704558", "540479", "688270", "652855", "57211", "667845",
            "667957", "704476", "667555", "59108", "14194", "509842",
            "651203", "704437", "650450", "537589", "57276", "13257",
            "668019", "650307", "10002", "6129", "5089", "3345",
            "651513", "534044", "650421", "449573", "57363", "653632",
            "651196", "653130", "617126", "19912", "651125", "472644",
            "57219", "704480", "605204", "653154", "667765", "176539",
            "57147", "295336", "57250", "704468", "704568", "650321",
            "659496", "650577", "704582", "652722", "665805", "57045",
            "652759", "651381", "46964", "527264"
        ]

    @staticmethod
    def _clean_html_content(html_content: str) -> str:
        if not html_content:
            return ""
        import re
        import html
        content = html.unescape(html_content)
        entities = {
            '&nbsp;': ' ', '&#160;': ' ', '&amp;': '&', '&lt;': '<', '&gt;': '>', '&quot;': '"',
            '&#39;': "'", '&#8201;': ' ', '&#215;': '×', '&#8722;': '−', '&ndash;': '–',
            '&rsquo;': "'", '&ldquo;': '"', '&rdquo;': '"', '&times;': '×', '&divide;': '÷'
        }
        for k, v in entities.items():
            content = content.replace(k, v)
        content = re.sub(r'<sub[^>]*>(.*?)</sub>', r'_\1', content)
        content = re.sub(r'<sup[^>]*>(.*?)</sup>', r'^\1', content)
        content = re.sub(r'</p>', '\n\n', content)
        content = re.sub(r'<br[^>]*>', '\n', content)
        content = re.sub(r'<[^>]+>', '', content)
        content = re.sub(r'\n\s*\n', '\n\n', content)
        content = re.sub(r'[ \t]+', ' ', content)
        return content.strip()

    def fetch_questions(self, qids: List[str], max_retries: int = 3) -> List[Dict[str, Any]]:
        valid_qids = [qid for qid in qids if qid in self.allowed_qids]
        if not valid_qids:
            raise ValueError("No valid QIDs provided.")
        payload = json.dumps({"qids": ", ".join(valid_qids)})
        last_error: Optional[Exception] = None
        for attempt in range(max_retries):
            try:
                resp = requests.post(self.base_url, headers=self.headers, data=payload, timeout=30)
                resp.raise_for_status()
                data = resp.json()
                return self._transform_api_response(data, valid_qids)
            except Exception as e:
                last_error = e
        if last_error:
            raise last_error
        return []

    def _transform_api_response(self, api_data: Any, requested_qids: List[str]) -> List[Dict[str, Any]]:
        questions: List[Dict[str, Any]] = []
        api_questions: List[Any]
        if isinstance(api_data, dict):
            if "questions" in api_data:
                api_questions = api_data["questions"]
            elif "data" in api_data:
                api_questions = api_data["data"]
            else:
                api_questions = [api_data]
        elif isinstance(api_data, list):
            api_questions = api_data
        else:
            return []

        for item in api_questions:
            try:
                qid = str(item.get("qid") or item.get("id") or item.get("question_id") or item.get("eng_hint_id", ""))
                question_text = (
                    item.get("q_text") or item.get("question_text") or item.get("question") or item.get("problem") or item.get("statement") or ""
                )
                solution_text = (
                    item.get("sol_text") or item.get("solution_text") or item.get("solution") or item.get("answer") or item.get("explanation") or ""
                )
                subject_name = item.get("sub_name", "Unknown")
                question_text = self._clean_html_content(question_text) if question_text else ""
                solution_text = self._clean_html_content(solution_text) if solution_text else ""
                if qid and question_text:
                    questions.append({
                        "id": qid,
                        "question": question_text,
                        "solution": solution_text,
                        "subject": subject_name,
                        "difficulty": "Intermediate",
                        "options": ["Option A", "Option B", "Option C", "Option D"],
                        "correct_answer": 0
                    })
            except Exception:
                continue
        return questions

    def fetch_random_questions(self, count: int = 5) -> List[Dict[str, Any]]:
        import random
        selected = random.sample(self.allowed_qids, min(count, len(self.allowed_qids)))
        return self.fetch_questions(selected)

    def get_allowed_qids(self) -> List[str]:
        return list(self.allowed_qids)

    def validate_qids(self, qids: List[str]) -> Tuple[List[str], List[str]]:
        valid = [q for q in qids if q in self.allowed_qids]
        invalid = [q for q in qids if q not in self.allowed_qids]
        return valid, invalid
