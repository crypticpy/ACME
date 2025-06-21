"""Pydantic models for structured feature extraction with GPT-4.1."""

from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from enum import Enum


class SentimentType(str, Enum):
    """Types of sentiment in survey responses."""
    positive = "positive"
    negative = "negative"
    neutral = "neutral"
    mixed = "mixed"


class StakeholderType(str, Enum):
    """Types of stakeholders in the cultural funding ecosystem."""
    artist = "artist"
    organization = "organization"
    resident = "resident"
    educator = "educator"
    business_owner = "business_owner"
    funder = "funder"
    venue_operator = "venue_operator"
    unknown = "unknown"


class UrgencyLevel(str, Enum):
    """Urgency levels for issues and feedback."""
    high = "high"
    medium = "medium"
    low = "low"


class ResponseFeatures(BaseModel):
    """Features extracted from a single survey response."""
    sentiment: SentimentType = Field(description="Overall sentiment of the response")
    sentiment_confidence: float = Field(ge=0.0, le=1.0, description="Confidence in sentiment classification")
    themes: List[str] = Field(description="Key themes identified in the response")
    urgency: UrgencyLevel = Field(description="Urgency level of issues raised")
    stakeholder_type: StakeholderType = Field(description="Type of stakeholder providing feedback")
    stakeholder_confidence: float = Field(ge=0.0, le=1.0, description="Confidence in stakeholder classification")
    key_phrases: List[str] = Field(description="Important phrases that capture key ideas")
    intent: str = Field(description="Primary intent of the response (e.g., problem_identification, solution_proposal)")
    contains_actionable_feedback: bool = Field(description="Whether response contains specific actionable items")
    mentioned_programs: List[str] = Field(default_factory=list, description="Cultural programs mentioned by name")
    barriers_identified: List[str] = Field(default_factory=list, description="Specific barriers to access or participation")
    solutions_proposed: List[str] = Field(default_factory=list, description="Specific solutions or improvements suggested")


class QuestionTheme(BaseModel):
    """Theme identified within a question's responses."""
    theme: str = Field(description="Name of the theme")
    count: int = Field(ge=0, description="Number of responses containing this theme")
    percentage: float = Field(ge=0.0, le=100.0, description="Percentage of responses with this theme")
    representative_quotes: List[str] = Field(description="Quotes that best represent this theme")
    sentiment_distribution: Dict[SentimentType, int] = Field(description="Sentiment breakdown for this theme")
    urgency_score: float = Field(ge=0.0, le=1.0, description="Average urgency score for this theme")
    stakeholder_breakdown: Dict[StakeholderType, int] = Field(description="Which stakeholders mention this theme")


class QuestionAnalysis(BaseModel):
    """Aggregated analysis for a single question."""
    question_id: str = Field(description="Unique identifier for the question")
    question_text: str = Field(description="Full text of the question")
    response_count: int = Field(ge=0, description="Total number of responses analyzed")
    dominant_themes: List[QuestionTheme] = Field(description="Top themes identified, ordered by frequency")
    sentiment_distribution: Dict[SentimentType, int] = Field(description="Overall sentiment breakdown")
    urgency_distribution: Dict[UrgencyLevel, int] = Field(description="Distribution of urgency levels")
    stakeholder_distribution: Dict[StakeholderType, int] = Field(description="Types of stakeholders responding")
    key_insights: List[str] = Field(description="Major insights derived from responses")
    recommendations: List[str] = Field(description="Actionable recommendations based on analysis")
    contradictions: List[str] = Field(default_factory=list, description="Conflicting viewpoints identified")
    consensus_points: List[str] = Field(default_factory=list, description="Areas of broad agreement")


class CrossQuestionInsight(BaseModel):
    """Insights that span multiple questions."""
    insight_type: str = Field(description="Type of insight (e.g., 'recurring_barrier', 'systemic_issue')")
    description: str = Field(description="Detailed description of the insight")
    supporting_questions: List[str] = Field(description="Question IDs that support this insight")
    evidence_count: int = Field(ge=0, description="Number of responses supporting this insight")
    confidence: float = Field(ge=0.0, le=1.0, description="Statistical confidence in this insight")
    implications: List[str] = Field(description="Strategic implications of this insight")
    affected_stakeholders: List[StakeholderType] = Field(description="Stakeholders most affected")
    severity_score: float = Field(ge=0.0, le=1.0, description="Severity/importance score")


class ProgramFeedback(BaseModel):
    """Feedback specific to a cultural program."""
    program_name: str = Field(description="Name of the cultural program")
    mention_count: int = Field(ge=0, description="Number of times program is mentioned")
    sentiment_summary: Dict[SentimentType, int] = Field(description="Sentiment breakdown for program mentions")
    strengths: List[str] = Field(description="Identified strengths of the program")
    improvement_areas: List[str] = Field(description="Areas needing improvement")
    specific_requests: List[str] = Field(description="Specific requests or suggestions")
    representative_quotes: List[str] = Field(description="Notable quotes about the program")
    impact_statements: List[str] = Field(description="Statements about program impact")
    accessibility_issues: List[str] = Field(default_factory=list, description="Accessibility concerns raised")
    demographic_reach: Dict[str, int] = Field(default_factory=dict, description="Demographics served or underserved")