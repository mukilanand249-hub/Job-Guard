import torch
from transformers import pipeline
from bs4 import BeautifulSoup
import requests
import whois
import pytesseract
from PIL import Image
from datetime import datetime
import io
from urllib.parse import urlparse

from django.conf import settings

tesseract_cmd = getattr(settings, "TESSERACT_CMD", "").strip()
if tesseract_cmd:
    pytesseract.pytesseract.tesseract_cmd = tesseract_cmd

class FraudDetector:
    _instance = None
    _classifier = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(FraudDetector, cls).__new__(cls)
            cls._classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")
        return cls._instance

    def scrape_url(self, url):
        try:
            from selenium import webdriver
            from selenium.webdriver.chrome.options import Options
            
            options = Options()
            options.add_argument("--headless")
            options.add_argument("--disable-gpu")
            options.add_argument("--no-sandbox")
            options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
            
            driver = webdriver.Chrome(options=options)
            driver.get(url)
            driver.implicitly_wait(5)
            text = driver.find_element("tag name", "body").text
            driver.quit()
            
            if not text:
                print(f"Warning: No text content found for URL: {url}")
            return text
        except ImportError:
            print("Selenium not installed. Falling back to requests.")
            try:
                headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
                response = requests.get(url, headers=headers, timeout=10)
                response.raise_for_status()
                soup = BeautifulSoup(response.content, 'html.parser')
                return soup.body.get_text(separator=' ', strip=True)
            except Exception as e:
                print(f"Fallback scraping error: {e}")
                return ""
        except Exception as e:
            print(f"Selenium scraping error for {url}: {e}")
            return ""

    def extract_text_from_image(self, image_bytes):
        try:
            image = Image.open(io.BytesIO(image_bytes))
            text = pytesseract.image_to_string(image)
            return text
        except Exception as e:
            print(f"OCR Error: {e}")
            return ""

    def check_domain_age(self, url):
        import concurrent.futures
        
        def _get_whois():
            return whois.whois(url)

        try:
            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
                domain_name = urlparse(url).hostname or url
                future = executor.submit(lambda: whois.whois(domain_name))
                domain = future.result(timeout=5)  # 5 second timeout
                
            creation_date = domain.creation_date
            if isinstance(creation_date, list):
                creation_date = creation_date[0]
            
            if not creation_date:
                return None, "Unknown"

            age = (datetime.now() - creation_date).days
            return age, creation_date.strftime('%Y-%m-%d')
        except concurrent.futures.TimeoutError:
            print(f"Whois lookup timed out for {url}")
            return None, "Timeout"
        except Exception as e:
            print(f"Whois Error: {e}")
            return None, "Error"

    def analyze(self, text, url=None):
        heuristic_score, red_flags, green_flags = self._heuristic_check(text)
        
        # Domain Age Check
        if url:
            age, created_date = self.check_domain_age(url)
            if age is not None:
                if age < 90: # Less than 3 months
                    heuristic_score -= 30
                    red_flags.append(f"Domain is very new ({age} days old). Created: {created_date}")
                else:
                    green_flags.append(f"Domain age verified ({age} days old).")

        # Zero-shot classification
        labels = ["fraudulent scam job posting", "legitimate safe job", "not a job description", "satirical or joke job posting"]
        # truncate text to avoid memory issues and pipeline token limits (usually 512 for bart)
        truncated_text = text[:1500] 
        result = self._classifier(truncated_text, candidate_labels=labels)
        
        scores_map = dict(zip(result['labels'], result['scores']))
        
        if scores_map["not a job description"] > 0.45:
            return {
                "trust_score": 0,
                "verdict": "INVALID",
                "recommendation": "Scan a Job Page",
                "analysis_summary": "The AI determined that the content on this page is not a job description. Please navigate to a valid job posting and try again.",
                "red_flags": ["Page content is irrelevant"],
                "green_flags": []
            }

        # Check for overly satirical or AI-generated joke descriptions
        if scores_map.get("satirical or joke job posting", 0) > 0.4:
            heuristic_score -= 40
            red_flags.append("AI detected satirical, overly exaggerated, or AI-generated joke content")

        # Combine scam and joke probabilities as negative indicators
        scam_and_joke_score = scores_map.get("fraudulent scam job posting", 0) + scores_map.get("satirical or joke job posting", 0)
        legit_prob = scores_map["legitimate safe job"] / (scores_map["legitimate safe job"] + scam_and_joke_score + 1e-9)
        legit_score = legit_prob * 100 

        final_score = (heuristic_score * 0.6) + (legit_score * 0.4)

        # Force a SCAM verdict if the text contains 3 or more severe red flags
        if len(red_flags) >= 3:
            final_score = min(final_score, 35)
        
        verdict = "LEGIT" if final_score > 70 else "SCAM" if final_score < 40 else "SUSPICIOUS"

        recommendation = "Safe to Apply" if verdict == "LEGIT" else "Proceed with Caution" if verdict == "SUSPICIOUS" else "Do Not Apply"
        
        reasoning = []
        if verdict == "SCAM":
            reasoning.append("This job posting exhibits multiple high-risk indicators common in fraudulent listings.")
        elif verdict == "SUSPICIOUS":
            reasoning.append("This posting has some concerning elements but isn't definitively a scam.")
        else:
            reasoning.append("This job posting appears to be legitimate based on standard indicators.")
            
        if red_flags:
            reasoning.append(f"Key concerns include: {', '.join(red_flags)}.")
        if green_flags:
            reasoning.append(f"Positive signals: {', '.join(green_flags)}.")

        return {
            "trust_score": int(final_score),
            "verdict": verdict,
            "red_flags": red_flags,
            "green_flags": green_flags,
            "recommendation": recommendation,
            "analysis_summary": " ".join(reasoning)
        }

    def _heuristic_check(self, text):
        score = 50
        red_flags = []
        green_flags = []
        
        suspicious_keywords = [
            "wire transfer", "offshore", "check processing", "urgent", 
            "money order", "telegram", "whatsapp",
            "synergy", "ninja", "disrupt the", "unlimited earning", 
            "buzzword", "blockchain-enabled", "scrum, waterfall, and chaos"
        ]
        legit_keywords = [
            "equal opportunity", "benefits", "401k", "insurance", "requirements", 
            "dental", "vision", "inclusive", "culture", "professional development", 
            "interview", "resume", "responsibilities", "qualifications", "salary", 
            "experience", "paid time off", "pto", "diversity", "apply online"
        ]

        text_lower = text.lower()

        for kw in suspicious_keywords:
            if kw in text_lower:
                score -= 10
                red_flags.append(f"Suspicious keyword: {kw}")

        for kw in legit_keywords:
            if kw in text_lower:
                score += 5
                green_flags.append(f"Legitimacy indicator: {kw}")

        if len(text) < 100:
            score -= 20
            red_flags.append("Text too short")
        
        if len(text) > 500:
            score += 10
            green_flags.append("Detailed description")

        return max(0, min(100, score)), red_flags, green_flags
