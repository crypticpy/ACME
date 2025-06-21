"""Feature extractor for deep qualitative analysis using GPT-4.1 structured outputs."""

import json
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime
import hashlib

from openai import OpenAI, AzureOpenAI
from pydantic import ValidationError
from rich.console import Console

from ..config import settings
from ..validation.audit import AuditLogger
from ..llm.client import LLMClient
from .models import (
    ResponseFeatures, 
    QuestionAnalysis, 
    CrossQuestionInsight,
    ProgramFeedback,
    QuestionTheme,
    SentimentType,
    StakeholderType,
    UrgencyLevel
)

console = Console()


class ResponseFeatureExtractor:
    """
    Extracts deep features from survey responses using GPT-4.1 with structured outputs.
    
    This class implements the feature extraction strategy outlined in PROJECT_PLAN.md,
    using the new OpenAI Responses API with Pydantic models for type-safe outputs.
    """
    
    def __init__(self, audit_logger: Optional[AuditLogger] = None):
        """Initialize the feature extractor with GPT-4.1 client."""
        self.audit_logger = audit_logger or AuditLogger()
        
        # Set up feature cache directory
        self.feature_cache_dir = settings.data_dir / "features" / "responses"
        self.feature_cache_dir.mkdir(exist_ok=True, parents=True)
        
        # Initialize LLM client (handles Azure OpenAI automatically)
        self.llm_client = LLMClient(audit_logger=self.audit_logger)
        self.model = self.llm_client.model
    
    def _generate_cache_key(self, response_text: str, question_text: str) -> str:
        """Generate a unique cache key for a response."""
        cache_data = {
            "response": response_text,
            "question": question_text,
            "model": self.model,
            "extractor_version": "1.0"
        }
        cache_str = json.dumps(cache_data, sort_keys=True)
        return hashlib.sha256(cache_str.encode()).hexdigest()
    
    def _save_features_to_cache(self, cache_key: str, features: ResponseFeatures, 
                               question_id: str) -> None:
        """Save extracted features to cache."""
        # Organize by question
        question_cache_dir = self.feature_cache_dir / question_id
        question_cache_dir.mkdir(exist_ok=True, parents=True)
        
        cache_file = question_cache_dir / f"{cache_key}.json"
        
        # Convert to dict and add metadata
        features_dict = features.model_dump()
        features_dict["cached_at"] = datetime.now().isoformat()
        features_dict["cache_key"] = cache_key
        features_dict["model"] = self.model
        
        with open(cache_file, 'w') as f:
            json.dump(features_dict, f, indent=2)
            
        self.audit_logger.log_operation(
            operation="feature_cache_save",
            cache_key=cache_key,
            question_id=question_id,
            file_path=str(cache_file)
        )
    
    def _load_features_from_cache(self, cache_key: str, question_id: str) -> Optional[ResponseFeatures]:
        """Load features from cache if available."""
        question_cache_dir = self.feature_cache_dir / question_id
        cache_file = question_cache_dir / f"{cache_key}.json"
        
        if cache_file.exists():
            with open(cache_file, 'r') as f:
                data = json.load(f)
                
            self.audit_logger.log_operation(
                operation="feature_cache_hit",
                cache_key=cache_key,
                question_id=question_id,
                cached_at=data.get("cached_at")
            )
            
            # Remove metadata before creating model
            data.pop("cached_at", None)
            data.pop("cache_key", None)
            data.pop("model", None)
            
            try:
                return ResponseFeatures(**data)
            except ValidationError as e:
                self.audit_logger.log_error(
                    operation="feature_cache_validation_error",
                    error_type="ValidationError",
                    error_message=str(e),
                    cache_key=cache_key
                )
                return None
        
        return None
    
    def extract_features(self, response: str, question: str, response_id: str,
                        question_id: str) -> Optional[ResponseFeatures]:
        """
        Extract deep features from a single survey response using GPT-4.1.
        
        Args:
            response: The survey response text
            question: The question text for context
            response_id: Unique identifier for the response
            question_id: Unique identifier for the question
            
        Returns:
            ResponseFeatures object with extracted features, or None if extraction fails
        """
        # Check cache first
        cache_key = self._generate_cache_key(response, question)
        cached_features = self._load_features_from_cache(cache_key, question_id)
        if cached_features:
            console.print(f"[dim]Using cached features for {response_id} (key: {cache_key[:8]}...)[/dim]")
            return cached_features
        
        if not self.llm_client.client:
            self.audit_logger.log_error(
                operation="extract_features",
                error_type="ClientNotInitialized",
                error_message="LLM client not initialized"
            )
            return None
        
        # Prepare the prompt following GPT-4.1 best practices
        system_prompt = """You are an expert ethnographer and municipal policy analyst specializing in cultural funding.

## Identity
You analyze community feedback with empathy, nuance, and attention to power dynamics.

## Instructions
Extract detailed features from this survey response about cultural funding in Austin:

1. **Sentiment Analysis**: Determine the overall emotional tone with confidence
2. **Theme Identification**: Extract 3-7 specific themes (not generic categories)
3. **Urgency Assessment**: Evaluate how urgent the issues raised are
4. **Stakeholder Classification**: Identify the respondent type with confidence
5. **Key Phrases**: Extract verbatim phrases that capture core ideas
6. **Intent Recognition**: Determine the primary purpose of the response
7. **Actionable Feedback**: Identify if specific actions are requested
8. **Program Mentions**: List any cultural programs mentioned by name
9. **Barriers**: Identify specific obstacles to cultural participation
10. **Solutions**: Extract any specific improvements suggested

## PERSISTENCE
Analyze thoroughly - extract all relevant features even from brief responses.

## ACCURACY
Base all features on explicit evidence in the text. Do not infer beyond what is stated."""

        user_prompt = f"""Question: {question}

Response ID: {response_id}
Response Text: {response}

Extract comprehensive features following the schema."""

        try:
            # Add JSON schema to the prompt
            schema_prompt = f"\n\nPlease respond with a valid JSON object that matches this schema:\n{json.dumps(ResponseFeatures.model_json_schema(), indent=2)}"
            
            # Use LLMClient with structured output format
            response = self.llm_client.generate_response(
                prompt=user_prompt + schema_prompt,
                instructions=system_prompt,
                temperature=0.3,
                response_format=ResponseFeatures
            )
            
            # Parse the structured response
            features_dict = json.loads(response.content)
            features = ResponseFeatures(**features_dict)
            
            # Save to cache
            self._save_features_to_cache(cache_key, features, question_id)
            
            # Log the extraction
            self.audit_logger.log_operation(
                operation="feature_extraction_success",
                response_id=response_id,
                question_id=question_id,
                themes_count=len(features.themes),
                sentiment=features.sentiment.value,
                urgency=features.urgency.value,
                tokens_used=response.tokens_used
            )
            
            return features
            
        except json.JSONDecodeError as e:
            self.audit_logger.log_error(
                operation="feature_extraction_json_error",
                error_type="JSONDecodeError",
                error_message=str(e),
                response_id=response_id
            )
            return None
            
        except ValidationError as e:
            self.audit_logger.log_error(
                operation="feature_extraction_validation_error",
                error_type="ValidationError",
                error_message=str(e),
                response_id=response_id
            )
            return None
            
        except Exception as e:
            self.audit_logger.log_error(
                operation="feature_extraction_error",
                error_type=type(e).__name__,
                error_message=str(e),
                response_id=response_id,
                question_id=question_id
            )
            return None
    
    def batch_extract_features(self, responses: List[Dict[str, str]], 
                             batch_size: int = 10) -> List[Dict[str, Any]]:
        """
        Extract features from multiple responses in batches.
        
        Args:
            responses: List of dicts with 'id', 'text', 'question_id', 'question_text'
            batch_size: Number of responses to process concurrently
            
        Returns:
            List of response features with metadata
        """
        extracted_features = []
        total_responses = len(responses)
        
        console.print(f"\n[bold]Extracting features from {total_responses} responses...[/bold]")
        
        with console.status("[bold green]Processing responses...") as status:
            for i, response_data in enumerate(responses):
                status.update(f"Processing response {i+1}/{total_responses}")
                
                features = self.extract_features(
                    response=response_data['text'],
                    question=response_data['question_text'],
                    response_id=response_data['id'],
                    question_id=response_data['question_id']
                )
                
                if features:
                    extracted_features.append({
                        'response_id': response_data['id'],
                        'question_id': response_data['question_id'],
                        'features': features.model_dump()
                    })
                
                # Progress update every 10 responses
                if (i + 1) % 10 == 0:
                    console.print(f"[dim]Processed {i+1}/{total_responses} responses[/dim]")
        
        success_rate = len(extracted_features) / total_responses * 100 if total_responses > 0 else 0
        console.print(f"\n[green]✓[/green] Feature extraction complete: {len(extracted_features)}/{total_responses} successful ({success_rate:.1f}%)")
        
        return extracted_features