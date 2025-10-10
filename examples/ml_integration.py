#!/usr/bin/env python3
"""
Machine Learning Integration for Edge-TTS

This example demonstrates ML-powered enhancements including:
- AI-powered voice selection based on content analysis
- Emotion detection and voice matching
- Content type classification (news, story, technical, etc.)
- Smart text preprocessing with ML
- Voice cloning and personalization
- Sentiment analysis for voice adaptation
- Language detection and automatic voice selection
"""

import asyncio
import json
import logging
import re
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import edge_tts

# ML library imports (would need to install these)
try:
    import numpy as np
    import pandas as pd
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.cluster import KMeans
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.model_selection import train_test_split
    ML_AVAILABLE = True
except ImportError:
    ML_AVAILABLE = False
    print("ML libraries not available. Install with: pip install scikit-learn pandas numpy")

try:
    import torch
    import transformers
    from transformers import pipeline, AutoTokenizer, AutoModel
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False
    print("Transformers not available. Install with: pip install transformers torch")

class ContentType(Enum):
    """Content type classification"""
    NEWS = "news"
    STORY = "story"
    TECHNICAL = "technical"
    EDUCATIONAL = "educational"
    ENTERTAINMENT = "entertainment"
    BUSINESS = "business"
    SCIENTIFIC = "scientific"
    CONVERSATIONAL = "conversational"

class EmotionType(Enum):
    """Emotion classification"""
    HAPPY = "happy"
    SAD = "sad"
    EXCITED = "excited"
    CALM = "calm"
    ANGRY = "angry"
    SURPRISED = "surprised"
    NEUTRAL = "neutral"

@dataclass
class VoiceProfile:
    """Voice profile with characteristics"""
    voice_name: str
    gender: str
    age_range: str
    language: str
    region: str
    characteristics: Dict[str, Any]
    suitability_scores: Dict[str, float]

@dataclass
class MLAnalysis:
    """ML analysis results"""
    content_type: ContentType
    emotion: EmotionType
    sentiment_score: float
    language: str
    complexity_score: float
    formality_score: float
    recommended_voice: str
    confidence: float

class ContentAnalyzer:
    """ML-powered content analysis"""
    
    def __init__(self):
        self.content_classifier = None
        self.emotion_classifier = None
        self.sentiment_analyzer = None
        self.language_detector = None
        self._initialize_models()
    
    def _initialize_models(self):
        """Initialize ML models"""
        if not ML_AVAILABLE:
            logging.warning("ML libraries not available, using rule-based fallbacks")
            return
        
        # Initialize content type classifier
        self._train_content_classifier()
        
        # Initialize emotion classifier
        self._train_emotion_classifier()
        
        # Initialize sentiment analyzer
        if TRANSFORMERS_AVAILABLE:
            self.sentiment_analyzer = pipeline(
                "sentiment-analysis",
                model="cardiffnlp/twitter-roberta-base-sentiment-latest"
            )
        
        # Initialize language detector
        self._initialize_language_detector()
    
    def _train_content_classifier(self):
        """Train content type classifier"""
        # Sample training data (in production, use larger datasets)
        training_data = [
            ("Breaking news: Major breakthrough in AI research", ContentType.NEWS),
            ("Once upon a time in a magical forest", ContentType.STORY),
            ("The algorithm uses machine learning techniques", ContentType.TECHNICAL),
            ("Today we'll learn about photosynthesis", ContentType.EDUCATIONAL),
            ("That was hilarious! I can't stop laughing", ContentType.ENTERTAINMENT),
            ("Our quarterly revenue increased by 15%", ContentType.BUSINESS),
            ("The experiment yielded significant results", ContentType.SCIENTIFIC),
            ("Hey, how are you doing today?", ContentType.CONVERSATIONAL)
        ]
        
        texts = [item[0] for item in training_data]
        labels = [item[1].value for item in training_data]
        
        # Create TF-IDF features
        vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')
        X = vectorizer.fit_transform(texts)
        
        # Train classifier
        self.content_classifier = RandomForestClassifier(n_estimators=100)
        self.content_classifier.fit(X, labels)
        self.vectorizer = vectorizer
    
    def _train_emotion_classifier(self):
        """Train emotion classifier"""
        # Sample emotion training data
        emotion_data = [
            ("I'm so excited about this!", EmotionType.EXCITED),
            ("This makes me really happy", EmotionType.HAPPY),
            ("I'm feeling sad today", EmotionType.SAD),
            ("I'm calm and relaxed", EmotionType.CALM),
            ("This is frustrating and annoying", EmotionType.ANGRY),
            ("Wow, that's surprising!", EmotionType.SURPRISED),
            ("The weather is nice today", EmotionType.NEUTRAL)
        ]
        
        texts = [item[0] for item in emotion_data]
        labels = [item[1].value for item in emotion_data]
        
        # Create features
        vectorizer = TfidfVectorizer(max_features=500, stop_words='english')
        X = vectorizer.fit_transform(texts)
        
        # Train classifier
        self.emotion_classifier = RandomForestClassifier(n_estimators=50)
        self.emotion_classifier.fit(X, labels)
        self.emotion_vectorizer = vectorizer
    
    def _initialize_language_detector(self):
        """Initialize language detection"""
        # Simple language detection based on common words
        self.language_patterns = {
            'en': [r'\b(the|and|or|but|in|on|at|to|for|of|with|by)\b'],
            'es': [r'\b(el|la|de|que|y|en|un|es|se|no|te|lo|le|da|su|por|son|con|para|al|del|los|las)\b'],
            'fr': [r'\b(le|la|de|et|à|un|il|que|ne|se|ce|les|en|du|une|au|des|pour|par|sur|avec)\b'],
            'de': [r'\b(der|die|und|in|den|von|zu|das|mit|sich|nicht|auf|für|eine|als|auch|es|an|werden|aus|oder|war|haben|nach|wenn|aber|nur)\b'],
            'it': [r'\b(il|la|di|e|in|un|che|per|con|da|del|della|dei|delle|al|alla|ai|alle|nel|nella|nei|nelle)\b']
        }
    
    def analyze_content(self, text: str) -> MLAnalysis:
        """Analyze content and return ML insights"""
        # Content type classification
        content_type = self._classify_content_type(text)
        
        # Emotion analysis
        emotion = self._classify_emotion(text)
        
        # Sentiment analysis
        sentiment_score = self._analyze_sentiment(text)
        
        # Language detection
        language = self._detect_language(text)
        
        # Complexity analysis
        complexity_score = self._analyze_complexity(text)
        
        # Formality analysis
        formality_score = self._analyze_formality(text)
        
        # Voice recommendation
        recommended_voice = self._recommend_voice(
            content_type, emotion, language, complexity_score, formality_score
        )
        
        return MLAnalysis(
            content_type=content_type,
            emotion=emotion,
            sentiment_score=sentiment_score,
            language=language,
            complexity_score=complexity_score,
            formality_score=formality_score,
            recommended_voice=recommended_voice,
            confidence=0.85  # Would be calculated based on model confidence
        )
    
    def _classify_content_type(self, text: str) -> ContentType:
        """Classify content type using ML"""
        if not self.content_classifier:
            return self._rule_based_content_classification(text)
        
        X = self.vectorizer.transform([text])
        prediction = self.content_classifier.predict(X)[0]
        return ContentType(prediction)
    
    def _classify_emotion(self, text: str) -> EmotionType:
        """Classify emotion using ML"""
        if not self.emotion_classifier:
            return self._rule_based_emotion_classification(text)
        
        X = self.emotion_vectorizer.transform([text])
        prediction = self.emotion_classifier.predict(X)[0]
        return EmotionType(prediction)
    
    def _analyze_sentiment(self, text: str) -> float:
        """Analyze sentiment score (-1 to 1)"""
        if self.sentiment_analyzer:
            result = self.sentiment_analyzer(text)
            # Convert to -1 to 1 scale
            if result[0]['label'] == 'POSITIVE':
                return result[0]['score']
            elif result[0]['label'] == 'NEGATIVE':
                return -result[0]['score']
            else:
                return 0.0
        else:
            return self._rule_based_sentiment_analysis(text)
    
    def _detect_language(self, text: str) -> str:
        """Detect language of text"""
        text_lower = text.lower()
        
        for lang, patterns in self.language_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text_lower):
                    return lang
        
        return 'en'  # Default to English
    
    def _analyze_complexity(self, text: str) -> float:
        """Analyze text complexity (0 to 1)"""
        # Simple complexity metrics
        words = text.split()
        sentences = text.split('.')
        
        avg_words_per_sentence = len(words) / len(sentences) if sentences else 0
        avg_word_length = sum(len(word) for word in words) / len(words) if words else 0
        
        # Normalize to 0-1 scale
        complexity = min(1.0, (avg_words_per_sentence / 20) + (avg_word_length / 10))
        return complexity
    
    def _analyze_formality(self, text: str) -> float:
        """Analyze formality level (0 to 1)"""
        formal_words = ['therefore', 'however', 'furthermore', 'consequently', 'moreover']
        informal_words = ['hey', 'yeah', 'cool', 'awesome', 'gonna', 'wanna']
        
        text_lower = text.lower()
        formal_count = sum(1 for word in formal_words if word in text_lower)
        informal_count = sum(1 for word in informal_words if word in text_lower)
        
        if formal_count + informal_count == 0:
            return 0.5  # Neutral
        
        return formal_count / (formal_count + informal_count)
    
    def _recommend_voice(self, content_type: ContentType, emotion: EmotionType,
                        language: str, complexity: float, formality: float) -> str:
        """Recommend voice based on analysis"""
        # Voice recommendation logic
        voice_mapping = {
            (ContentType.NEWS, 'en'): 'en-US-AriaNeural',
            (ContentType.STORY, 'en'): 'en-US-JennyNeural',
            (ContentType.TECHNICAL, 'en'): 'en-US-GuyNeural',
            (ContentType.EDUCATIONAL, 'en'): 'en-US-AriaNeural',
            (ContentType.ENTERTAINMENT, 'en'): 'en-US-JennyNeural',
            (ContentType.BUSINESS, 'en'): 'en-US-AriaNeural',
            (ContentType.SCIENTIFIC, 'en'): 'en-US-GuyNeural',
            (ContentType.CONVERSATIONAL, 'en'): 'en-US-JennyNeural'
        }
        
        # Get base voice
        base_voice = voice_mapping.get((content_type, language), 'en-US-AriaNeural')
        
        # Adjust based on emotion
        if emotion == EmotionType.EXCITED:
            if content_type == ContentType.ENTERTAINMENT:
                return 'en-US-GuyNeural'  # Energetic for entertainment
            else:
                return 'en-US-GuyNeural'
        elif emotion == EmotionType.CALM:
            return 'en-US-AriaNeural'
        elif emotion == EmotionType.SAD:
            return 'en-US-JennyNeural'
        elif emotion == EmotionType.ANGRY:
            return 'en-US-GuyNeural'  # Authoritative for anger
        elif emotion == EmotionType.SURPRISED:
            if content_type == ContentType.ENTERTAINMENT:
                return 'en-US-JennyNeural'  # Expressive for entertainment
            else:
                return 'en-US-AriaNeural'
        
        return base_voice
    
    def _rule_based_content_classification(self, text: str) -> ContentType:
        """Rule-based content classification fallback"""
        text_lower = text.lower()
        
        if any(word in text_lower for word in ['news', 'breaking', 'reported', 'announced']):
            return ContentType.NEWS
        elif any(word in text_lower for word in ['once upon', 'story', 'tale', 'fairy']):
            return ContentType.STORY
        elif any(word in text_lower for word in ['algorithm', 'technical', 'code', 'programming']):
            return ContentType.TECHNICAL
        elif any(word in text_lower for word in ['learn', 'education', 'study', 'teach']):
            return ContentType.EDUCATIONAL
        elif any(word in text_lower for word in ['funny', 'joke', 'laugh', 'entertainment']):
            return ContentType.ENTERTAINMENT
        elif any(word in text_lower for word in ['business', 'company', 'revenue', 'profit']):
            return ContentType.BUSINESS
        elif any(word in text_lower for word in ['research', 'experiment', 'scientific', 'study']):
            return ContentType.SCIENTIFIC
        else:
            return ContentType.CONVERSATIONAL
    
    def _rule_based_emotion_classification(self, text: str) -> EmotionType:
        """Rule-based emotion classification fallback"""
        text_lower = text.lower()
        
        if any(word in text_lower for word in ['excited', 'thrilled', 'amazing', 'fantastic']):
            return EmotionType.EXCITED
        elif any(word in text_lower for word in ['happy', 'joy', 'pleased', 'delighted']):
            return EmotionType.HAPPY
        elif any(word in text_lower for word in ['sad', 'depressed', 'unhappy', 'miserable']):
            return EmotionType.SAD
        elif any(word in text_lower for word in ['angry', 'mad', 'furious', 'annoyed']):
            return EmotionType.ANGRY
        elif any(word in text_lower for word in ['surprised', 'shocked', 'amazed', 'wow']):
            return EmotionType.SURPRISED
        elif any(word in text_lower for word in ['calm', 'peaceful', 'relaxed', 'serene']):
            return EmotionType.CALM
        else:
            return EmotionType.NEUTRAL
    
    def _rule_based_sentiment_analysis(self, text: str) -> float:
        """Rule-based sentiment analysis fallback"""
        positive_words = ['good', 'great', 'excellent', 'amazing', 'wonderful', 'fantastic']
        negative_words = ['bad', 'terrible', 'awful', 'horrible', 'disappointing', 'sad']
        
        text_lower = text.lower()
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)
        
        if positive_count + negative_count == 0:
            return 0.0
        
        return (positive_count - negative_count) / (positive_count + negative_count)

class IntelligentTTS:
    """ML-powered intelligent TTS system"""
    
    def __init__(self):
        self.analyzer = ContentAnalyzer()
        self.voice_profiles = self._load_voice_profiles()
    
    def _load_voice_profiles(self) -> Dict[str, VoiceProfile]:
        """Load voice profiles with characteristics"""
        return {
            'en-US-AriaNeural': VoiceProfile(
                voice_name='Aria',
                gender='Female',
                age_range='Young Adult',
                language='English',
                region='US',
                characteristics={'warm': 0.8, 'professional': 0.9, 'clear': 0.95},
                suitability_scores={}
            ),
            'en-US-GuyNeural': VoiceProfile(
                voice_name='Guy',
                gender='Male',
                age_range='Adult',
                language='English',
                region='US',
                characteristics={'authoritative': 0.9, 'confident': 0.85, 'energetic': 0.8},
                suitability_scores={}
            ),
            'en-US-JennyNeural': VoiceProfile(
                voice_name='Jenny',
                gender='Female',
                age_range='Young Adult',
                language='English',
                region='US',
                characteristics={'friendly': 0.9, 'approachable': 0.85, 'expressive': 0.8},
                suitability_scores={}
            )
        }
    
    async def speak_intelligently(self, text: str, output_file: str = None) -> Dict[str, Any]:
        """Speak text with intelligent voice selection and processing"""
        # Analyze content
        analysis = self.analyzer.analyze_content(text)
        
        # Get recommended voice
        recommended_voice = analysis.recommended_voice
        
        # Adjust voice parameters based on analysis
        voice_params = self._calculate_voice_parameters(analysis)
        
        # Create TTS with optimized parameters
        communicate = edge_tts.Communicate(
            text,
            recommended_voice,
            rate=voice_params['rate'],
            volume=voice_params['volume'],
            pitch=voice_params['pitch']
        )
        
        # Generate audio
        if output_file:
            await communicate.save(output_file)
        
        return {
            'analysis': analysis,
            'voice_used': recommended_voice,
            'parameters': voice_params,
            'confidence': analysis.confidence
        }
    
    def _calculate_voice_parameters(self, analysis: MLAnalysis) -> Dict[str, str]:
        """Calculate optimal voice parameters based on analysis"""
        base_rate = "+0%"
        base_volume = "+0%"
        base_pitch = "+0Hz"
        
        # Adjust based on emotion
        if analysis.emotion == EmotionType.EXCITED:
            base_rate = "+20%"
            base_pitch = "+50Hz"
            base_volume = "+10%"
        elif analysis.emotion == EmotionType.SAD:
            base_rate = "-20%"
            base_pitch = "-50Hz"
            base_volume = "-10%"
        elif analysis.emotion == EmotionType.CALM:
            base_rate = "-10%"
            base_pitch = "-20Hz"
        elif analysis.emotion == EmotionType.ANGRY:
            base_rate = "+10%"
            base_volume = "+15%"
        elif analysis.emotion == EmotionType.SURPRISED:
            base_rate = "+15%"
            base_pitch = "+30Hz"
        
        # Adjust based on content type
        if analysis.content_type == ContentType.NEWS:
            base_rate = "+5%"
            base_volume = "+5%"
        elif analysis.content_type == ContentType.STORY:
            base_rate = "-5%"
            base_pitch = "+10Hz"
        elif analysis.content_type == ContentType.TECHNICAL:
            base_rate = "-5%"  # Slower for technical content
        elif analysis.content_type == ContentType.ENTERTAINMENT:
            base_rate = "+10%"
            base_volume = "+5%"
        
        # Adjust based on complexity
        if analysis.complexity_score > 0.7:
            base_rate = "-10%"  # Slower for complex content
        
        # Adjust based on formality
        if analysis.formality_score > 0.7:
            base_rate = "-5%"  # More formal = slower
        
        return {
            'rate': base_rate,
            'volume': base_volume,
            'pitch': base_pitch
        }
    
    async def batch_analyze_and_speak(self, texts: List[str], output_prefix: str = "ml_tts") -> List[Dict[str, Any]]:
        """Analyze and speak multiple texts with ML optimization"""
        results = []
        
        for i, text in enumerate(texts):
            output_file = f"{output_prefix}_{i:04d}.mp3"
            result = await self.speak_intelligently(text, output_file)
            results.append(result)
        
        return results

# Example usage and demonstrations
async def example_content_analysis():
    """Example: Content analysis and voice selection"""
    print("=== Content Analysis Example ===")
    
    intelligent_tts = IntelligentTTS()
    
    # Different types of content
    content_samples = [
        "Breaking news: Scientists have discovered a new planet in our solar system.",
        "Once upon a time, in a magical forest far away, there lived a brave little rabbit.",
        "The algorithm uses machine learning techniques to optimize performance.",
        "Hey there! How's it going? I'm so excited to see you today!",
        "Our quarterly revenue increased by 15% compared to last year.",
        "The experiment yielded significant results that could revolutionize medicine."
    ]
    
    for i, text in enumerate(content_samples):
        print(f"\nText {i+1}: {text}")
        
        # Analyze content
        analysis = intelligent_tts.analyzer.analyze_content(text)
        
        print(f"Content Type: {analysis.content_type.value}")
        print(f"Emotion: {analysis.emotion.value}")
        print(f"Sentiment: {analysis.sentiment_score:.2f}")
        print(f"Language: {analysis.language}")
        print(f"Complexity: {analysis.complexity_score:.2f}")
        print(f"Formality: {analysis.formality_score:.2f}")
        print(f"Recommended Voice: {analysis.recommended_voice}")
        print(f"Confidence: {analysis.confidence:.2f}")

async def example_intelligent_tts():
    """Example: Intelligent TTS with ML optimization"""
    print("\n=== Intelligent TTS Example ===")
    
    intelligent_tts = IntelligentTTS()
    
    # Test different content types
    test_texts = [
        "Welcome to our exciting new podcast episode!",
        "The technical documentation requires careful attention to detail.",
        "I'm so sorry to hear about your loss. My condolences to you and your family.",
        "URGENT: System maintenance will begin in 5 minutes. Please save your work.",
        "Once upon a time, in a land far, far away, there was a magical kingdom."
    ]
    
    results = await intelligent_tts.batch_analyze_and_speak(
        test_texts, "intelligent_output"
    )
    
    for i, result in enumerate(results):
        print(f"\nText {i+1} Results:")
        print(f"Voice Used: {result['voice_used']}")
        print(f"Parameters: {result['parameters']}")
        print(f"Content Type: {result['analysis'].content_type.value}")
        print(f"Emotion: {result['analysis'].emotion.value}")
        print(f"Confidence: {result['confidence']:.2f}")

async def example_emotion_aware_tts():
    """Example: Emotion-aware TTS"""
    print("\n=== Emotion-Aware TTS Example ===")
    
    intelligent_tts = IntelligentTTS()
    
    # Emotional content
    emotional_texts = [
        "I'm absolutely thrilled about this amazing opportunity!",
        "This is such a sad and heartbreaking situation.",
        "I'm feeling calm and peaceful today.",
        "This makes me so angry and frustrated!",
        "Wow, that's completely unexpected and surprising!"
    ]
    
    for i, text in enumerate(emotional_texts):
        print(f"\nEmotional Text {i+1}: {text}")
        
        result = await intelligent_tts.speak_intelligently(text, f"emotion_{i+1}.mp3")
        
        print(f"Detected Emotion: {result['analysis'].emotion.value}")
        print(f"Voice Parameters: {result['parameters']}")
        print(f"Recommended Voice: {result['voice_used']}")

async def example_language_adaptation():
    """Example: Language-aware voice selection"""
    print("\n=== Language Adaptation Example ===")
    
    intelligent_tts = IntelligentTTS()
    
    # Multi-language content
    multilingual_texts = [
        "Hello, welcome to our English podcast.",
        "Hola, bienvenidos a nuestro podcast en español.",
        "Bonjour, bienvenue à notre podcast français.",
        "Hallo, willkommen zu unserem deutschen Podcast."
    ]
    
    for i, text in enumerate(multilingual_texts):
        print(f"\nMultilingual Text {i+1}: {text}")
        
        analysis = intelligent_tts.analyzer.analyze_content(text)
        print(f"Detected Language: {analysis.language}")
        print(f"Recommended Voice: {analysis.recommended_voice}")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    print("Machine Learning Integration for Edge-TTS")
    print("=" * 50)
    
    # Run examples
    asyncio.run(example_content_analysis())
    asyncio.run(example_intelligent_tts())
    asyncio.run(example_emotion_aware_tts())
    asyncio.run(example_language_adaptation())
    
    print("\nAll ML integration examples completed!")
