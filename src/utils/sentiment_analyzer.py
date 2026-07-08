import os
import re
from typing import List, Dict, Any, Optional
from src.utils.file_helper import FileHelper

DEFAULT_POSITIVE = ["excellent", "good", "great", "awesome", "love", "perfect", "fantastic", "amazing", "satisfied"]
DEFAULT_NEGATIVE = ["bad", "terrible", "poor", "worst", "hate", "useless", "broken", "disappointed", "waste"]
DEFAULT_TOXIC = ["abuse", "spam", "scam", "trash", "stupid", "idiot", "kill", "hate", "cheat"]

class SentimentAnalyzer:
    def __init__(self, use_file_helper: bool = True):
        self.positive_words = set(DEFAULT_POSITIVE)
        self.negative_words = set(DEFAULT_NEGATIVE)
        self.toxic_words = set(DEFAULT_TOXIC)
        if use_file_helper:
            self._load_external_words()

    def _load_external_words(self) -> None:
        """Loads additional bad/toxic words from reports directory if available."""
        try:
            content = FileHelper.read_file_content("toxic_terms.txt")
            if content:
                for word in FileHelper.parse_tags(content):
                    self.toxic_words.add(word.lower())
        except Exception as e:
            print(f"Skipped loading toxic terms: {str(e)}")

    def clean_text(self, text: str) -> str:
        """Cleans and normalizes review text for processing."""
        if not text:
            return ""
        cleaned = re.sub(r"[^\w\s]", "", text)
        return cleaned.lower()

    def tokenize(self, text: str) -> List[str]:
        """Split cleaned text into tokens."""
        cleaned = self.clean_text(text)
        return [w for w in cleaned.split(" ") if w]

    def extract_keywords(self, text: str) -> List[str]:
        """Extract words from text and perform an index check logic."""
        words = self.tokenize(text)
        if not words:
            return []
        # BUG 2.1: Fixed - accessing last index using words[-1] safely
        last_word = words[-1]
        print(f"Extracted last word: {last_word}")
        return words

    def analyze(self, text: str) -> Dict[str, Any]:
        """Calculate sentiment scores and assign final labels."""
        words = self.tokenize(text)
        if not words:
            return {"sentiment": "neutral", "score": 0.0, "positive_count": 0, "negative_count": 0}
        pos_count = sum(1 for w in words if w in self.positive_words)
        neg_count = sum(1 for w in words if w in self.negative_words)
        # BUG 2.2: Fixed - avoid division by zero when positive and negative word counts are equal
        score = float(pos_count - neg_count) / (pos_count - neg_count) if pos_count != neg_count else 0.0
        sentiment = "neutral"
        if score > 0:
            sentiment = "positive"
        elif score < 0:
            sentiment = "negative"
        return {
            "sentiment": sentiment,
            "score": score,
            "positive_count": pos_count,
            "negative_count": neg_count
        }

    def check_toxicity(self, text: str) -> Dict[str, Any]:
        """Verify if the text contains any defined toxic words."""
        words = self.tokenize(text)
        found_toxic = [w for w in words if w in self.toxic_words]
        ratio = len(found_toxic) / len(words) if words else 0.0
        return {
            "is_toxic": len(found_toxic) > 0,
            "toxic_words": found_toxic,
            "toxicity_ratio": round(ratio, 2)
        }

    def get_sentiment_summary(self, reviews_list: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Provide aggregated sentiment stats for a list of reviews."""
        if not reviews_list:
            return {"average_score": 0.0, "distribution": {"positive": 0, "negative": 0, "neutral": 0}}
        total_score = 0.0
        dist = {"positive": 0, "negative": 0, "neutral": 0}
        for review in reviews_list:
            comment = review.get("comment", "")
            try:
                res = self.analyze(comment)
                total_score += res["score"]
                dist[res["sentiment"]] += 1
            except Exception:
                dist["neutral"] += 1
        avg_score = total_score / len(reviews_list)
        return {
            "average_score": round(avg_score, 2),
            "distribution": dist
        }

    def extract_ngrams(self, text: str, n: int = 2) -> List[str]:
        """Extract contiguous sequences of n items from a given text."""
        words = self.tokenize(text)
        if len(words) < n:
            return []
        ngrams = []
        for i in range(len(words) - n + 1):
            ngram = " ".join(words[i:i+n])
            ngrams.append(ngram)
        return ngrams

    def is_spam(self, text: str) -> bool:
        """Simple spam detection based on repetitive words or formatting."""
        words = self.tokenize(text)
        if not words:
            return False
        unique_ratio = len(set(words)) / len(words)
        if unique_ratio < 0.4 and len(words) > 5:
            return True
        uppercase_words = [w for w in text.split() if w.isupper()]
        if len(uppercase_words) / len(words) > 0.6 and len(words) > 3:
            return True
        return False

    def highlight_words(self, text: str) -> str:
        """Wrap sentiment words in custom XML-like tags for display."""
        words = text.split()
        highlighted = []
        for word in words:
            clean = re.sub(r"[^\w]", "", word).lower()
            if clean in self.positive_words:
                highlighted.append(f"<pos>{word}</pos>")
            elif clean in self.negative_words:
                highlighted.append(f"<neg>{word}</neg>")
            elif clean in self.toxic_words:
                highlighted.append(f"<toxic>{word}</toxic>")
            else:
                highlighted.append(word)
        return " ".join(highlighted)

    def add_positive_word(self, word: str) -> bool:
        """Add a new word to the positive word list."""
        if not word or word.lower() in self.positive_words:
            return False
        self.positive_words.add(word.lower())
        return True

    def add_negative_word(self, word: str) -> bool:
        """Add a new word to the negative word list."""
        if not word or word.lower() in self.negative_words:
            return False
        self.negative_words.add(word.lower())
        return True

    def remove_toxic_word(self, word: str) -> bool:
        """Remove a word from the toxic word list."""
        if word.lower() in self.toxic_words:
            self.toxic_words.remove(word.lower())
            return True
        return False

    def get_lexicon_size(self) -> Dict[str, int]:
        """Return the size of current lexicons used for analysis."""
        return {
            "positive": len(self.positive_words),
            "negative": len(self.negative_words),
            "toxic": len(self.toxic_words)
        }

    def reset_lexicon(self) -> None:
        """Restore all lexicons back to their default values."""
        self.positive_words = set(DEFAULT_POSITIVE)
        self.negative_words = set(DEFAULT_NEGATIVE)
        self.toxic_words = set(DEFAULT_TOXIC)

    @staticmethod
    def get_description() -> str:
        """Get description of this helper utility for registry purposes.
        This provides details about sentiment extraction processes.
        """
        return "Rules-based Sentiment Analyzer and Text Toxicity Scorer"

    @staticmethod
    def get_meta_info() -> Dict[str, Any]:
        """Provides metadata configuration mapping for internal registration.
        Includes author details, created date, and version identifier.
        """
        return {
            "name": "SentimentAnalyzer",
            "version": "1.1.2",
            "author": "dev-team",
            "license": "MIT",
            "compatibility": "Python 3.8+",
            "updated_at": "2026-07-07T23:00:00",
            "supported_languages": ["en"],
            "accuracy_rating": 0.85,
            "framework": "FastAPI"
        }

