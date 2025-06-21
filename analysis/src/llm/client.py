"""OpenAI client wrapper for GPT-4.1 API with response caching."""

import json
import os
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
import hashlib
from tenacity import retry, stop_after_attempt, wait_exponential

from openai import OpenAI, AzureOpenAI
from pydantic import BaseModel
from rich.console import Console

from ..config import settings
from ..validation.audit import AuditLogger

console = Console()


class LLMResponse(BaseModel):
    """Structured response from LLM."""
    content: str
    model: str
    tokens_used: Optional[Dict[str, int]] = None
    raw_response: Optional[Any] = None


# Structured output models for GPT-4.1
class Classification(BaseModel):
    """Classification result for a single respondent."""
    id: str
    classification: str
    confidence: float
    evidence: List[str]


class ClassificationResponse(BaseModel):
    """Response containing multiple classifications."""
    classifications: List[Classification]


class Theme(BaseModel):
    """A single theme extracted from responses."""
    theme: str
    count: int
    percentage: float
    description: str
    keywords: List[str]
    sentiment: str
    urgency: str


class ThemesResponse(BaseModel):
    """Response containing multiple themes."""
    themes: List[Theme]


class Quote(BaseModel):
    """A supporting quote for a theme."""
    quote: str
    respondent_id: str
    context: str


class EvidenceResponse(BaseModel):
    """Response containing supporting quotes."""
    quotes: List[Quote]


class ProgramTheme(BaseModel):
    """Theme specific to a program."""
    theme: str
    sentiment: str
    frequency: int
    key_points: List[str]
    recommendation: str


class ProgramAnalysis(BaseModel):
    """Analysis for a specific program."""
    program: str
    response_count: int
    themes: List[ProgramTheme]


class TransportationIssue(BaseModel):
    """Transportation/parking issue category."""
    count: int
    key_issues: List[str]
    affected_areas: List[str]


class ParkingLotAnalysis(BaseModel):
    """Analysis of transportation and parking issues."""
    total_mentions: int
    categories: Dict[str, TransportationIssue]
    summary: str
    recommendations: List[str]


class LLMClient:
    """Client for interacting with GPT-4.1 using the new responses API."""
    
    def __init__(self, audit_logger: Optional[AuditLogger] = None):
        self.audit_logger = audit_logger or AuditLogger()
        
        # Set up cache directory
        self.cache_dir = settings.data_dir / "llm_cache"
        self.cache_dir.mkdir(exist_ok=True, parents=True)
        
        # Initialize Azure OpenAI client if Azure credentials are available
        if settings.azure_openai_api_key and settings.azure_openai_endpoint:
            try:
                self.client = AzureOpenAI(
                    azure_endpoint=settings.azure_openai_endpoint,
                    api_key=settings.azure_openai_api_key,
                    api_version=settings.azure_openai_api_version
                )
                self.model = settings.azure_openai_deployment_name
                self.using_azure = True
                self.audit_logger.log_operation(
                    operation="llm_client_init",
                    provider="azure",
                    deployment=self.model
                )
            except Exception as e:
                self.audit_logger.log_error(
                    operation="azure_llm_client_init",
                    error_type=type(e).__name__,
                    error_message=str(e)
                )
                self.client = None
                self.using_azure = False
        # Fall back to standard OpenAI if Azure not configured
        elif settings.openai_api_key:
            try:
                self.client = OpenAI(api_key=settings.openai_api_key)
                self.model = settings.openai_model
                self.using_azure = False
                self.audit_logger.log_operation(
                    operation="llm_client_init",
                    provider="openai",
                    model=self.model
                )
            except Exception as e:
                self.audit_logger.log_error(
                    operation="llm_client_init",
                    error_type=type(e).__name__,
                    error_message=str(e)
                )
                self.client = None
                self.using_azure = False
        else:
            self.client = None
            self.using_azure = False
            self.audit_logger.log_warning(
                operation="llm_client_init",
                message="Neither Azure OpenAI nor OpenAI API keys configured"
            )
    
    def _clean_json_response(self, content: str) -> str:
        """Clean JSON response by removing markdown code blocks."""
        content = content.strip()
        
        # Remove markdown code blocks
        if content.startswith("```json"):
            content = content[7:]  # Remove ```json
        elif content.startswith("```"):
            content = content[3:]  # Remove ```
            
        if content.endswith("```"):
            content = content[:-3]  # Remove trailing ```
            
        # Also handle cases where there might be newlines
        content = content.strip()
        
        return content
    
    def _generate_cache_key(self, prompt: str, instructions: Optional[str], 
                          temperature: float, model: str) -> str:
        """Generate a unique cache key for the request."""
        cache_data = {
            "prompt": prompt,
            "instructions": instructions or "",
            "temperature": temperature,
            "model": model
        }
        cache_str = json.dumps(cache_data, sort_keys=True)
        return hashlib.sha256(cache_str.encode()).hexdigest()
    
    def _save_to_cache(self, cache_key: str, response_data: Dict[str, Any]) -> None:
        """Save LLM response to cache."""
        cache_file = self.cache_dir / f"{cache_key}.json"
        
        # Add metadata
        response_data["cached_at"] = datetime.now().isoformat()
        response_data["cache_key"] = cache_key
        
        with open(cache_file, 'w') as f:
            json.dump(response_data, f, indent=2)
            
        self.audit_logger.log_operation(
            operation="llm_cache_save",
            cache_key=cache_key,
            file_path=str(cache_file)
        )
    
    def _load_from_cache(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """Load LLM response from cache if available."""
        cache_file = self.cache_dir / f"{cache_key}.json"
        
        if cache_file.exists():
            with open(cache_file, 'r') as f:
                data = json.load(f)
                
            self.audit_logger.log_operation(
                operation="llm_cache_hit",
                cache_key=cache_key,
                cached_at=data.get("cached_at")
            )
            
            return data
        
        return None
    
    @retry(
        stop=stop_after_attempt(settings.llm_retry_attempts),
        wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    def generate_response(
        self,
        prompt: str,
        instructions: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        response_format: Optional[BaseModel] = None
    ) -> LLMResponse:
        """
        Generate a response using GPT-4.1's new API.
        
        Args:
            prompt: The main input/query
            instructions: System-level instructions (developer role)
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            response_format: Optional Pydantic model for structured output
            
        Returns:
            LLMResponse object with generated content
        """
        temperature = temperature or settings.llm_temperature
        max_tokens = max_tokens or settings.llm_max_tokens
        
        # Check cache first
        cache_key = self._generate_cache_key(prompt, instructions, temperature, self.model)
        cached_response = self._load_from_cache(cache_key)
        
        if cached_response:
            console.print(f"[dim]Using cached LLM response (key: {cache_key[:8]}...)[/dim]")
            return LLMResponse(
                content=cached_response["content"],
                model=cached_response["model"],
                tokens_used=cached_response.get("tokens_used"),
                raw_response=cached_response
            )
        
        try:
            if not self.client:
                raise ValueError("LLM client not initialized. Please set AZURE_OPENAI_API_KEY and AZURE_OPENAI_ENDPOINT or OPENAI_API_KEY environment variables.")
            
            # Build messages
            messages = []
            if instructions:
                messages.append({"role": "system", "content": instructions})
            messages.append({"role": "user", "content": prompt})
            
            # Build request parameters
            params = {
                "model": self.model,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens
            }
            
            # Use structured outputs with response_format if provided
            if response_format:
                # For now, just ask for JSON in the prompt
                # The GPT-4 models support JSON mode
                params["response_format"] = {"type": "json_object"}
                
                # Add schema description to the prompt
                schema_desc = f"\n\nIMPORTANT: Return a valid JSON object that matches this Pydantic model structure:\n{response_format.__name__}: {response_format.model_json_schema()}"
                messages[-1]["content"] += schema_desc
            
            # Call the chat completions API
            response = self.client.chat.completions.create(**params)
            
            # Extract text content
            content = response.choices[0].message.content
            
            # Clean JSON if we're expecting structured output
            if response_format and content:
                content = self._clean_json_response(content)
            
            # Calculate token usage if available
            tokens_used = None
            if hasattr(response, 'usage') and response.usage:
                try:
                    usage_dict = {}
                    if hasattr(response.usage, 'prompt_tokens'):
                        usage_dict["input_tokens"] = response.usage.prompt_tokens
                    if hasattr(response.usage, 'completion_tokens'):
                        usage_dict["output_tokens"] = response.usage.completion_tokens
                    if hasattr(response.usage, 'total_tokens'):
                        usage_dict["total_tokens"] = response.usage.total_tokens
                    
                    if usage_dict:
                        tokens_used = usage_dict
                except AttributeError:
                    pass
            
            # Prepare response data for caching
            response_data = {
                "content": content,
                "model": self.model,
                "tokens_used": tokens_used,
                "prompt": prompt,
                "instructions": instructions,
                "temperature": temperature,
                "timestamp": datetime.now().isoformat()
            }
            
            # Save to cache
            self._save_to_cache(cache_key, response_data)
            
            # Log the LLM call
            self.audit_logger.log_llm_call(
                prompt=prompt,
                response=content,
                model=self.model,
                parameters={
                    "temperature": temperature,
                    "max_tokens": max_tokens,
                    "has_instructions": bool(instructions)
                },
                tokens_used=tokens_used
            )
            
            return LLMResponse(
                content=content,
                model=self.model,
                tokens_used=tokens_used,
                raw_response=response_data
            )
            
        except Exception as e:
            self.audit_logger.log_error(
                operation="llm_generate_response",
                error_type=type(e).__name__,
                error_message=str(e),
                context={"prompt_preview": prompt[:200]}
            )
            raise
    
    def classify_respondents(
        self,
        responses: List[Dict[str, str]],
        batch_size: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Classify survey respondents into categories using GPT-4.1.
        
        Args:
            responses: List of respondent data
            batch_size: Number of responses to process at once
            
        Returns:
            List of classifications with confidence scores
        """
        instructions = """You are an expert ethnographer analyzing community feedback.

Task: Classify each respondent into one of these categories based on their complete profile:
1. Creative/Artist - Individuals who create art, music, or cultural content
2. Organizational Staff - Employees of arts/cultural organizations  
3. Community Member/Patron - Residents who consume/support arts

Consider:
- Self-identified role
- Language patterns
- Concerns expressed
- Programs mentioned

For classification values, use exactly one of: "Creative", "Organizational Staff", or "Community Member"."""
        
        classifications = []
        
        # Process in batches
        for i in range(0, len(responses), batch_size):
            batch = responses[i:i + batch_size]
            
            # Format batch data
            prompt = "Classify these respondents:\n\n"
            for resp in batch:
                prompt += f"ID: {resp['id']}\n"
                prompt += f"Role: {resp.get('role', 'Not specified')}\n"
                prompt += f"Response: {resp.get('text', '')[:500]}...\n\n"
            
            # Get classification using structured outputs
            response = self.generate_response(
                prompt=prompt,
                instructions=instructions,
                temperature=0.3,
                response_format=ClassificationResponse
            )
            
            try:
                # Parse the structured response
                batch_results = json.loads(response.content)
                classifications.extend(batch_results["classifications"])
            except (json.JSONDecodeError, KeyError) as e:
                self.audit_logger.log_error(
                    operation="parse_classification_response",
                    error_type=type(e).__name__,
                    error_message=str(e),
                    context={"response_preview": response.content[:200]}
                )
        
        return classifications
    
    def extract_themes(
        self,
        responses: List[str],
        num_themes: int = 10,
        min_frequency: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Extract major themes from text responses using GPT-4.1.
        
        Args:
            responses: List of text responses
            num_themes: Number of themes to extract
            min_frequency: Minimum frequency for theme inclusion
            
        Returns:
            List of themes with counts and descriptions
        """
        min_frequency = min_frequency or settings.min_theme_frequency
        
        instructions = f"""You are a senior municipal analyst specializing in cultural policy.

Task: Identify the top {num_themes} themes from community responses about cultural funding.

Requirements:
- Each theme should appear in at least {min_frequency} responses
- Themes should be distinct and actionable
- Focus on funding priorities, barriers, and opportunities
- For sentiment, use exactly one of: "positive", "negative", "neutral", or "mixed"
- For urgency, use exactly one of: "high", "medium", or "low" """
        
        # Prepare sample of responses for analysis
        sample_size = min(len(responses), 500)
        sampled_responses = responses[:sample_size]
        
        prompt = f"Analyze these {len(sampled_responses)} community responses about cultural funding:\n\n"
        for i, resp in enumerate(sampled_responses):
            if resp and len(resp.strip()) > 20:  # Skip very short responses
                prompt += f"{i+1}. {resp[:200]}...\n"
        
        prompt += f"\n\nTotal responses analyzed: {len(responses)}"
        
        # Get themes using structured outputs
        response = self.generate_response(
            prompt=prompt,
            instructions=instructions,
            temperature=0.4,
            response_format=ThemesResponse
        )
        
        try:
            # Parse the structured response
            themes_data = json.loads(response.content)
            return themes_data["themes"]
        except (json.JSONDecodeError, KeyError) as e:
            self.audit_logger.log_error(
                operation="parse_themes_response",
                error_type=type(e).__name__,
                error_message=str(e),
                context={"response_length": len(response.content)}
            )
            return []
    
    def generate_theme_evidence(
        self,
        theme: str,
        responses: List[Dict[str, str]],
        num_examples: int = 5
    ) -> List[str]:
        """
        Generate supporting evidence quotes for a theme.
        
        Args:
            theme: Theme name
            responses: List of responses with IDs
            num_examples: Number of examples to generate
            
        Returns:
            List of supporting quotes
        """
        instructions = f"""You are an equity-minded communicator analyzing community feedback.

Task: Select {num_examples} compelling quotes that illustrate the theme "{theme}".

Requirements:
- Direct quotes under 25 words each
- Include respondent ID for traceability
- Show diverse perspectives (creative, organizational, community)
- Choose emotionally resonant but professional examples"""
        
        # Prepare relevant responses
        prompt = f"Theme: {theme}\n\nResponses to analyze:\n\n"
        for resp in responses[:100]:  # Limit to prevent token overflow
            prompt += f"ID: {resp['id']}\n{resp['text'][:300]}...\n\n"
        
        # Get evidence using structured outputs
        response = self.generate_response(
            prompt=prompt,
            instructions=instructions,
            temperature=0.5,
            response_format=EvidenceResponse
        )
        
        try:
            # Parse the structured response
            evidence_data = json.loads(response.content)
            return [q["quote"] for q in evidence_data["quotes"]]
        except (json.JSONDecodeError, KeyError) as e:
            self.audit_logger.log_error(
                operation="parse_evidence_response",
                error_type=type(e).__name__,
                error_message=str(e)
            )
            return []
    
    def analyze_program_themes(
        self,
        program_name: str,
        responses: List[str],
        top_n: int = 3
    ) -> Dict[str, Any]:
        """
        Analyze themes specific to a program.
        
        Args:
            program_name: Name of the program
            responses: Responses mentioning this program
            top_n: Number of top themes to return
            
        Returns:
            Program-specific theme analysis
        """
        instructions = f"""You are a cultural policy specialist analyzing feedback for {program_name}.

Task: Identify the top {top_n} themes specific to this program.

Requirements:
- Focus on program-specific feedback
- Include both positive feedback and areas for improvement
- Provide actionable insights
- For sentiment, use exactly one of: "positive", "neutral", or "negative" """
        
        prompt = f"Analyze feedback for {program_name}:\n\n"
        for i, resp in enumerate(responses[:100]):
            prompt += f"{i+1}. {resp[:200]}...\n"
        
        prompt += f"\n\nProgram name: {program_name}\nTotal responses: {len(responses)}"
        
        # Get program analysis using structured outputs
        response = self.generate_response(
            prompt=prompt,
            instructions=instructions,
            temperature=0.4,
            response_format=ProgramAnalysis
        )
        
        try:
            # Parse the structured response
            return json.loads(response.content)
        except json.JSONDecodeError as e:
            self.audit_logger.log_error(
                operation="parse_program_themes",
                error_type="JSONDecodeError",
                error_message=str(e)
            )
            return {
                "program": program_name,
                "response_count": len(responses),
                "themes": [],
                "error": "Failed to parse response"
            }