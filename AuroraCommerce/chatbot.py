import json
import os
import re
import logging
import random
from typing import Dict, List, Tuple, Optional
from collections import Counter

# NLTK imports
import nltk
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.tag import pos_tag

# Scikit-learn imports for ML
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

# OpenAI integration
try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    logging.warning("OpenAI not available. Install with: pip install openai")

class AuroraChatbot:
    def __init__(self):
        """Initialize Aurora E-commerce Chatbot with NLTK and ML capabilities"""
        self.logger = logging.getLogger(__name__)
        
        # Download required NLTK data
        self._download_nltk_data()
        
        # Initialize NLTK components
        self.lemmatizer = WordNetLemmatizer()
        self.stop_words = set(stopwords.words('english'))
        
        # Load FAQ dataset
        self.faq_data = self._load_faq_dataset()
        
        # Initialize ML components
        self.vectorizer = TfidfVectorizer(
            max_features=5000,
            stop_words='english',
            ngram_range=(1, 2),
            lowercase=True
        )
        
        # Prepare dataset for ML
        self._prepare_ml_dataset()
        
        # Initialize OpenAI if available
        self.openai_client = None
        if OPENAI_AVAILABLE:
            api_key = os.environ.get("OPENAI_API_KEY")
            if api_key:
                self.openai_client = OpenAI(api_key=api_key)
        
        # Response confidence threshold (lowered for better matching)
        self.confidence_threshold = 0.15
        
        self.logger.info("Aurora Chatbot initialized successfully")
    
    def _download_nltk_data(self):
        """Download required NLTK datasets"""
        required_data = [
            'punkt_tab', 'stopwords', 'wordnet', 'averaged_perceptron_tagger',
            'vader_lexicon', 'omw-1.4'
        ]
        
        for data in required_data:
            try:
                nltk.download(data, quiet=True)
            except Exception as e:
                self.logger.warning(f"Failed to download NLTK data {data}: {e}")
    
    def _load_faq_dataset(self) -> Dict:
        """Load FAQ dataset from JSON file"""
        try:
            with open('faq_dataset.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
            self.logger.info(f"Loaded {len(data.get('faqs', []))} FAQ entries")
            return data
        except FileNotFoundError:
            self.logger.error("FAQ dataset file not found")
            return {"faqs": [], "categories": []}
        except json.JSONDecodeError as e:
            self.logger.error(f"Error parsing FAQ dataset: {e}")
            return {"faqs": [], "categories": []}
    
    def _prepare_ml_dataset(self):
        """Prepare dataset for machine learning operations"""
        self.questions = []
        self.answers = []
        self.categories = []
        self.question_category_map = {}
        
        for faq in self.faq_data.get('faqs', []):
            question = faq.get('question', '')
            answer = faq.get('answer', '')
            category = faq.get('category', 'general')
            
            if question and answer:
                processed_question = self._preprocess_text(question)
                self.questions.append(processed_question)
                self.answers.append(answer)
                self.categories.append(category)
                self.question_category_map[len(self.questions) - 1] = category
        
        # Fit TF-IDF vectorizer
        if self.questions:
            self.tfidf_matrix = self.vectorizer.fit_transform(self.questions)
            self.logger.info(f"TF-IDF matrix created with shape: {self.tfidf_matrix.shape}")
        else:
            self.tfidf_matrix = None
            self.logger.warning("No questions available for TF-IDF vectorization")
    
    def _preprocess_text(self, text: str) -> str:
        """Advanced text preprocessing using NLTK"""
        if not text:
            return ""
        
        # Convert to lowercase
        text = text.lower()
        
        # Remove special characters and digits
        text = re.sub(r'[^a-zA-Z\s]', '', text)
        
        # Simple tokenization fallback if NLTK fails
        try:
            tokens = word_tokenize(text)
        except LookupError:
            # Fallback to simple split if NLTK data is not available
            tokens = text.split()
        
        # Remove stopwords and lemmatize
        processed_tokens = []
        for token in tokens:
            if token not in self.stop_words and len(token) > 2:
                try:
                    lemmatized = self.lemmatizer.lemmatize(token)
                    processed_tokens.append(lemmatized)
                except:
                    # Fallback to original token if lemmatization fails
                    processed_tokens.append(token)
        
        return ' '.join(processed_tokens)
    
    def _find_best_match(self, user_input: str) -> Tuple[str, float, str]:
        """Find best matching FAQ using TF-IDF and cosine similarity"""
        if self.tfidf_matrix is None or not user_input.strip():
            return "", 0.0, "unknown"
        
        # Preprocess user input
        processed_input = self._preprocess_text(user_input)
        if not processed_input.strip():
            return "", 0.0, "unknown"
        
        # Transform user input using the fitted vectorizer
        try:
            user_vector = self.vectorizer.transform([processed_input])
        except Exception as e:
            self.logger.error(f"Error transforming user input: {e}")
            return "", 0.0, "unknown"
        
        # Calculate cosine similarities
        similarities = cosine_similarity(user_vector, self.tfidf_matrix).flatten()
        
        # Find best match
        best_match_idx = int(np.argmax(similarities))
        best_score = float(similarities[best_match_idx])
        
        self.logger.debug(f"Best match score: {best_score}, threshold: {self.confidence_threshold}")
        
        if best_score >= self.confidence_threshold:
            answer = self.answers[best_match_idx]
            category = self.question_category_map.get(best_match_idx, "unknown")
            return answer, best_score, category
        
        return "", best_score, "unknown"
    
    def _get_openai_response(self, user_input: str) -> Optional[str]:
        """Get response from OpenAI when local matching fails"""
        if not self.openai_client:
            return None
        
        try:
            # Create context about Aurora and e-commerce
            system_prompt = """You are AURORA, a professional e-commerce customer service assistant. 
            You help customers with questions about products, shipping, returns, payments, and accounts.
            Provide helpful, accurate, and concise responses. If you don't know something specific about 
            the company's policies, politely direct them to contact customer service for detailed information.
            Keep responses friendly but professional, and under 150 words."""
            
            response = self.openai_client.chat.completions.create(
                model="gpt-4o",  # the newest OpenAI model is "gpt-4o" which was released May 13, 2024. do not change this unless explicitly requested by the user
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_input}
                ],
                max_tokens=200,
                temperature=0.7
            )
            
            response_content = response.choices[0].message.content
            return response_content.strip() if response_content else None
        
        except Exception as e:
            self.logger.error(f"OpenAI API error: {e}")
            return None
    
    def get_response(self, user_input: str, use_rag: bool = False) -> Dict:
        """Get chatbot response using hybrid approach"""
        if not user_input.strip():
            return {
                'response': "I'd be happy to help! Please ask me a question about products, shipping, returns, payments, or your account.",
                'source': 'prompt',
                'confidence': 0.0
            }
        
        # First, try to find a match in the FAQ dataset
        answer, confidence, category = self._find_best_match(user_input)
        
        if answer and confidence >= self.confidence_threshold:
            return {
                'response': answer,
                'source': f'faq-{category}',
                'confidence': round(confidence, 3)
            }
        
        # If no good match found and OpenAI is available, use it as fallback
        if use_rag or confidence < self.confidence_threshold:
            openai_response = self._get_openai_response(user_input)
            if openai_response:
                return {
                    'response': openai_response,
                    'source': 'ai-assistant',
                    'confidence': 0.8
                }
        
        # Fallback to generic responses based on keywords
        generic_response = self._get_generic_response(user_input)
        return {
            'response': generic_response,
            'source': 'fallback',
            'confidence': 0.2
        }
    
    def _get_generic_response(self, user_input: str) -> str:
        """Generate generic response based on keywords"""
        user_input_lower = user_input.lower()
        
        # Keyword-based responses
        keyword_responses = {
            'shipping': "For shipping information, please check your order status in your account or contact our shipping department. We offer various shipping options including standard and express delivery.",
            'return': "Our return policy allows returns within 30 days of purchase. Items must be in original condition. Please visit our returns page or contact customer service for assistance.",
            'payment': "We accept all major credit cards, PayPal, and bank transfers. If you're having payment issues, please check your payment method or contact our billing department.",
            'account': "For account-related questions, please log into your account dashboard or contact customer support. We can help with password resets, profile updates, and order history.",
            'product': "For specific product information, please check the product page or use our search function. Our customer service team can also provide detailed product specifications.",
            'order': "To track your order or check order status, please log into your account or use our order tracking system. Contact support if you need additional assistance.",
            'cancel': "To cancel an order, please contact customer service as soon as possible. Cancellation may not be possible if the order has already been processed or shipped.",
            'refund': "Refunds are typically processed within 5-7 business days after we receive your returned item. Check your account for refund status or contact our billing department."
        }
        
        # Check for keywords
        for keyword, response in keyword_responses.items():
            if keyword in user_input_lower:
                return response
        
        # Default response
        return "I'd be happy to help you with your e-commerce question! Could you please provide more specific details about what you're looking for? I can assist with products, shipping, returns, payments, and account issues."
    
    def get_categories(self) -> List[str]:
        """Get available FAQ categories"""
        return self.faq_data.get('categories', ['Account', 'Payments', 'Products', 'Returns', 'Shipping'])
    
    def get_category_questions(self, category: str) -> List[str]:
        """Get questions for a specific category"""
        category_questions = []
        
        for faq in self.faq_data.get('faqs', []):
            if faq.get('category', '').lower() == category.lower():
                question = faq.get('question', '')
                if question:
                    category_questions.append(question)
        
        # Shuffle and return up to 15 questions
        random.shuffle(category_questions)
        return category_questions[:15]
    
    def get_conversation_stats(self) -> Dict:
        """Get chatbot statistics"""
        return {
            'total_faqs': len(self.faq_data.get('faqs', [])),
            'categories': len(self.get_categories()),
            'vectorizer_features': self.vectorizer.max_features if hasattr(self, 'vectorizer') else 0,
            'confidence_threshold': self.confidence_threshold,
            'openai_available': self.openai_client is not None
        }
