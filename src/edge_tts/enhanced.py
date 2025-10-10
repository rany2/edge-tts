#!/usr/bin/env python3
"""
Enhanced Edge-TTS with Advanced Features

This module provides advanced TTS capabilities including:
- ML-powered voice selection
- Advanced text processing with effects
- Batch processing capabilities
- Voice profiles and recommendations
- Emotion-aware TTS
"""

import asyncio
import json
import logging
import re
from typing import List, Dict, Any, Optional, Union, Tuple, BinaryIO, TextIO
from dataclasses import dataclass
from enum import Enum
from datetime import datetime
from io import BytesIO, TextIOWrapper
from .communicate import Communicate

# Optional ML imports
try:
    import numpy as np
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.ensemble import RandomForestClassifier
    ML_AVAILABLE = True
except ImportError:
    ML_AVAILABLE = False

try:
    from transformers import pipeline
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False

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

class PauseType(Enum):
    """Pause types for text processing"""
    SHORT = "short"
    MEDIUM = "medium"
    LONG = "long"
    EXTRA_LONG = "extra_long"

@dataclass
class VoiceProfile:
    """Voice profile with characteristics"""
    voice_name: str
    gender: str
    age_range: str
    language: str
    region: str
    characteristics: Dict[str, float]
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

@dataclass
class TextEffect:
    """Text effect for processing"""
    effect_type: str
    parameters: Dict[str, Any]
    start_pos: int
    end_pos: int

class ContentAnalyzer:
    """ML-powered content analysis"""
    
    def __init__(self):
        self.content_classifier = None
        self.emotion_classifier = None
        self.sentiment_analyzer = None
        self.language_patterns = {}
        self._initialize_models()
    
    def _initialize_models(self):
        """Initialize ML models"""
        if not ML_AVAILABLE:
            logging.warning("ML libraries not available, using rule-based fallbacks")
            return
        
        self._train_content_classifier()
        self._train_emotion_classifier()
        
        if TRANSFORMERS_AVAILABLE:
            self.sentiment_analyzer = pipeline(
                "sentiment-analysis",
                model="cardiffnlp/twitter-roberta-base-sentiment-latest"
            )
        
        self._initialize_language_detector()
    
    def _train_content_classifier(self):
        """Train content type classifier"""
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
        
        vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')
        X = vectorizer.fit_transform(texts)
        
        self.content_classifier = RandomForestClassifier(n_estimators=100)
        self.content_classifier.fit(X, labels)
        self.vectorizer = vectorizer
    
    def _train_emotion_classifier(self):
        """Train emotion classifier"""
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
        
        vectorizer = TfidfVectorizer(max_features=500, stop_words='english')
        X = vectorizer.fit_transform(texts)
        
        self.emotion_classifier = RandomForestClassifier(n_estimators=50)
        self.emotion_classifier.fit(X, labels)
        self.emotion_vectorizer = vectorizer
    
    def _initialize_language_detector(self):
        """Initialize language detection"""
        self.language_patterns = {
            'en': [r'\b(the|and|or|but|in|on|at|to|for|of|with|by)\b'],
            'es': [r'\b(el|la|de|que|y|en|un|es|se|no|te|lo|le|da|su|por|son|con|para|al|del|los|las)\b'],
            'fr': [r'\b(le|la|de|et|à|un|il|que|ne|se|ce|les|en|du|une|au|des|pour|par|sur|avec)\b'],
            'de': [r'\b(der|die|und|in|den|von|zu|das|mit|sich|nicht|auf|für|eine|als|auch|es|an|werden|aus|oder|war|haben|nach|wenn|aber|nur)\b'],
            'it': [r'\b(il|la|di|e|in|un|che|per|con|da|del|della|dei|delle|al|alla|ai|alle|nel|nella|nei|nelle)\b']
        }
    
    def analyze_content(self, text: str) -> MLAnalysis:
        """Analyze content and return ML insights"""
        content_type = self._classify_content_type(text)
        emotion = self._classify_emotion(text)
        sentiment_score = self._analyze_sentiment(text)
        language = self._detect_language(text)
        complexity_score = self._analyze_complexity(text)
        formality_score = self._analyze_formality(text)
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
            confidence=0.85
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
        words = text.split()
        sentences = text.split('.')
        
        avg_words_per_sentence = len(words) / len(sentences) if sentences else 0
        avg_word_length = sum(len(word) for word in words) / len(words) if words else 0
        
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
        
        base_voice = voice_mapping.get((content_type, language), 'en-US-AriaNeural')
        
        # Adjust based on emotion
        if emotion == EmotionType.EXCITED:
            if content_type == ContentType.ENTERTAINMENT:
                return 'en-US-GuyNeural'
            else:
                return 'en-US-GuyNeural'
        elif emotion == EmotionType.CALM:
            return 'en-US-AriaNeural'
        elif emotion == EmotionType.SAD:
            return 'en-US-JennyNeural'
        elif emotion == EmotionType.ANGRY:
            return 'en-US-GuyNeural'
        elif emotion == EmotionType.SURPRISED:
            if content_type == ContentType.ENTERTAINMENT:
                return 'en-US-JennyNeural'
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

class AdvancedTextProcessor:
    """Advanced text processing with effects"""
    
    def __init__(self):
        self.effect_patterns = {
            'pause': r'\[pause:(short|medium|long|extra_long)\]',
            'emotion': r'\[emotion:(happy|sad|excited|calm|angry|surprised|neutral)\]',
            'laugh': r'\[laugh\]',
            'sigh': r'\[sigh\]',
            'whisper': r'\[whisper\]',
            'shout': r'\[shout\]',
            'speed': r'\[speed:([+-]?\d+)%\]',
            'pitch': r'\[pitch:([+-]?\d+)Hz\]',
            'volume': r'\[volume:([+-]?\d+)%\]'
        }
    
    def process_text(self, text: str) -> Tuple[str, List[TextEffect]]:
        """Process text and extract effects"""
        effects = []
        processed_text = text
        
        for effect_type, pattern in self.effect_patterns.items():
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                effect = TextEffect(
                    effect_type=effect_type,
                    parameters=self._extract_parameters(match, effect_type),
                    start_pos=match.start(),
                    end_pos=match.end()
                )
                effects.append(effect)
                
                # Replace with appropriate SSML or remove
                if effect_type == 'pause':
                    pause_duration = self._get_pause_duration(effect.parameters.get('type', 'short'))
                    processed_text = processed_text.replace(match.group(), f'<break time="{pause_duration}"/>')
                else:
                    processed_text = processed_text.replace(match.group(), '')
        
        return processed_text, effects
    
    def _extract_parameters(self, match, effect_type: str) -> Dict[str, Any]:
        """Extract parameters from effect match"""
        if effect_type == 'pause':
            return {'type': match.group(1)}
        elif effect_type in ['speed', 'pitch', 'volume']:
            return {'value': int(match.group(1))}
        elif effect_type == 'emotion':
            return {'emotion': match.group(1)}
        else:
            return {}
    
    def _get_pause_duration(self, pause_type: str) -> str:
        """Get SSML pause duration"""
        durations = {
            'short': '0.5s',
            'medium': '1s',
            'long': '2s',
            'extra_long': '3s'
        }
        return durations.get(pause_type, '1s')

class EnhancedCommunicate:
    """Enhanced TTS with advanced features"""
    
    def __init__(self, text: str, voice: str = None, **kwargs):
        self.original_text = text
        self.voice = voice
        self.kwargs = kwargs
        
        # Initialize components
        self.analyzer = ContentAnalyzer()
        self.text_processor = AdvancedTextProcessor()
        
        # Process text and get analysis
        self.processed_text, self.effects = self.text_processor.process_text(text)
        self.analysis = self.analyzer.analyze_content(text)
        
        # Determine voice
        if voice is None:
            self.voice = self.analysis.recommended_voice
        else:
            self.voice = voice
        
        # Calculate voice parameters
        self.voice_params = self._calculate_voice_parameters()
        
        # Create base communicate instance
        self.communicate = Communicate(
            self.processed_text,
            self.voice,
            rate=self.voice_params['rate'],
            volume=self.voice_params['volume'],
            pitch=self.voice_params['pitch']
        )
    
    def _calculate_voice_parameters(self) -> Dict[str, str]:
        """Calculate optimal voice parameters based on analysis"""
        base_rate = "+0%"
        base_volume = "+0%"
        base_pitch = "+0Hz"
        
        # Adjust based on emotion
        if self.analysis.emotion == EmotionType.EXCITED:
            base_rate = "+20%"
            base_pitch = "+50Hz"
            base_volume = "+10%"
        elif self.analysis.emotion == EmotionType.SAD:
            base_rate = "-20%"
            base_pitch = "-50Hz"
            base_volume = "-10%"
        elif self.analysis.emotion == EmotionType.CALM:
            base_rate = "-10%"
            base_pitch = "-20Hz"
        elif self.analysis.emotion == EmotionType.ANGRY:
            base_rate = "+10%"
            base_volume = "+15%"
        elif self.analysis.emotion == EmotionType.SURPRISED:
            base_rate = "+15%"
            base_pitch = "+30Hz"
        
        # Adjust based on content type
        if self.analysis.content_type == ContentType.NEWS:
            base_rate = "+5%"
            base_volume = "+5%"
        elif self.analysis.content_type == ContentType.STORY:
            base_rate = "-5%"
            base_pitch = "+10Hz"
        elif self.analysis.content_type == ContentType.TECHNICAL:
            base_rate = "-5%"
        elif self.analysis.content_type == ContentType.ENTERTAINMENT:
            base_rate = "+10%"
            base_volume = "+5%"
        
        # Adjust based on complexity
        if self.analysis.complexity_score > 0.7:
            base_rate = "-10%"
        
        # Adjust based on formality
        if self.analysis.formality_score > 0.7:
            base_rate = "-5%"
        
        return {
            'rate': base_rate,
            'volume': base_volume,
            'pitch': base_pitch
        }
    
    async def save(self, output_file: str):
        """Save audio to file"""
        await self.communicate.save(output_file)
    
    async def saveMore(self, audio_fname: Union[str, bytes, BytesIO, BinaryIO],
                      metadata_fname: Optional[Union[str, bytes, BytesIO, TextIO]] = None):
        """Save audio and metadata using enhanced saveMore method"""
        await self.communicate.saveMore(audio_fname, metadata_fname)
    
    def get_analysis(self) -> MLAnalysis:
        """Get content analysis results"""
        return self.analysis
    
    def get_effects(self) -> List[TextEffect]:
        """Get processed text effects"""
        return self.effects
    
    def get_voice_parameters(self) -> Dict[str, str]:
        """Get calculated voice parameters"""
        return self.voice_params

class BatchProcessor:
    """Batch processing for multiple TTS tasks"""
    
    def __init__(self, max_concurrent: int = 5):
        self.max_concurrent = max_concurrent
        self.semaphore = asyncio.Semaphore(max_concurrent)
    
    async def process_batch(self, texts: List[str], voices: List[str] = None, 
                           output_prefix: str = "batch") -> List[Dict[str, Any]]:
        """Process multiple texts with intelligent voice selection"""
        if voices is None:
            voices = [None] * len(texts)
        
        tasks = []
        for i, (text, voice) in enumerate(zip(texts, voices)):
            task = self._process_single(text, voice, f"{output_prefix}_{i:04d}.mp3")
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        return results
    
    async def _process_single(self, text: str, voice: str, output_file: str) -> Dict[str, Any]:
        """Process a single text"""
        async with self.semaphore:
            try:
                enhanced = EnhancedCommunicate(text, voice)
                await enhanced.save(output_file)
                
                return {
                    'text': text,
                    'voice_used': enhanced.voice,
                    'output_file': output_file,
                    'analysis': enhanced.get_analysis(),
                    'parameters': enhanced.get_voice_parameters(),
                    'success': True
                }
            except Exception as e:
                return {
                    'text': text,
                    'voice_used': voice,
                    'output_file': output_file,
                    'error': str(e),
                    'success': False
                }

# Convenience functions for easy usage
async def speak_intelligently(text: str, output_file: str = None, voice: str = None) -> Dict[str, Any]:
    """Speak text with intelligent voice selection"""
    enhanced = EnhancedCommunicate(text, voice)
    
    if output_file:
        await enhanced.save(output_file)
    
    return {
        'analysis': enhanced.get_analysis(),
        'voice_used': enhanced.voice,
        'parameters': enhanced.get_voice_parameters(),
        'effects': enhanced.get_effects()
    }

async def batch_speak(texts: List[str], voices: List[str] = None, 
                     output_prefix: str = "batch") -> List[Dict[str, Any]]:
    """Batch process multiple texts"""
    processor = BatchProcessor()
    return await processor.process_batch(texts, voices, output_prefix)
