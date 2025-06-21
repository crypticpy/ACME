# ACME Cultural Funding Analysis - Implementation Plan

## Executive Summary

The current analysis implementation is inadequate for research-grade insights. This plan outlines a complete rebuild of the qualitative analysis system to meet PhD-level standards.

## GPT-4.1 and Structured Outputs Integration

*Note: For full implementation details, refer to the OpenAI documentation files:*
- `gpt_41.md` - GPT-4.1 model capabilities and prompt engineering
- `structured_responses.md` - Structured outputs with JSON schema validation

### Model Selection: GPT-4.1
As per the documentation, we will use the `gpt-4.1` model which offers:
- Solid combination of intelligence, speed, and cost effectiveness
- Optimized for agentic workflows and tool calling
- 1M token context window for handling large batches of responses
- Strong performance with structured output schemas

### Structured Outputs Architecture
All LLM analysis will use the new OpenAI Responses API with structured outputs to ensure:
1. **Reliable type-safety**: No validation or retry for incorrectly formatted responses
2. **Explicit refusals**: Safety-based model refusals are programmatically detectable
3. **Simpler prompting**: No need for strongly worded prompts to achieve consistent formatting

### Implementation Using Pydantic Models
We'll define structured response schemas for each analysis type:

```python
from pydantic import BaseModel
from typing import List, Optional
from enum import Enum

class SentimentType(str, Enum):
    positive = "positive"
    negative = "negative"
    neutral = "neutral"
    mixed = "mixed"

class StakeholderType(str, Enum):
    artist = "artist"
    organization = "organization"
    resident = "resident"
    educator = "educator"
    business_owner = "business_owner"
    unknown = "unknown"

class UrgencyLevel(str, Enum):
    high = "high"
    medium = "medium"
    low = "low"

class ResponseFeatures(BaseModel):
    """Features extracted from a single survey response"""
    sentiment: SentimentType
    sentiment_confidence: float
    themes: List[str]
    urgency: UrgencyLevel
    stakeholder_type: StakeholderType
    stakeholder_confidence: float
    key_phrases: List[str]
    intent: str
    contains_actionable_feedback: bool

class QuestionTheme(BaseModel):
    """Theme identified within a question's responses"""
    theme: str
    count: int
    percentage: float
    representative_quotes: List[str]
    sentiment_distribution: dict[SentimentType, int]

class QuestionAnalysis(BaseModel):
    """Aggregated analysis for a single question"""
    question_id: str
    question_text: str
    response_count: int
    dominant_themes: List[QuestionTheme]
    sentiment_distribution: dict[SentimentType, int]
    urgency_distribution: dict[UrgencyLevel, int]
    stakeholder_distribution: dict[StakeholderType, int]
    key_insights: List[str]
    recommendations: List[str]

class CrossQuestionInsight(BaseModel):
    """Insights that span multiple questions"""
    insight_type: str
    description: str
    supporting_questions: List[str]
    evidence_count: int
    confidence: float
    implications: List[str]

class ProgramFeedback(BaseModel):
    """Feedback specific to a cultural program"""
    program_name: str
    mention_count: int
    sentiment_summary: dict[SentimentType, int]
    strengths: List[str]
    improvement_areas: List[str]
    specific_requests: List[str]
    representative_quotes: List[str]
```

### API Usage Pattern
Following the GPT-4.1 documentation (see `gpt_41.md` and `structured_responses.md`), we'll use the Responses API with structured outputs:

```python
from openai import OpenAI

client = OpenAI()

# For individual response analysis
response = client.responses.create(
    model="gpt-4.1",
    input=[
        {
            "role": "system", 
            "content": "Extract detailed features from this survey response..."
        },
        {
            "role": "user",
            "content": f"Question: {question_text}\nResponse: {response_text}"
        }
    ],
    text={
        "format": {
            "type": "json_schema",
            "name": "response_features",
            "schema": ResponseFeatures.model_json_schema(),
            "strict": True
        }
    }
)

features = json.loads(response.output_text)
```

### Prompt Engineering for GPT-4.1
Based on the documentation's best practices:

1. **System Prompt Structure**:
   - Clear identity and purpose
   - Explicit instructions with examples
   - Context positioning at the end

2. **Required Reminders** (for agentic behavior):
   ```
   ## PERSISTENCE
   Keep analyzing until all features are thoroughly extracted.
   
   ## PLANNING
   Think step-by-step about what features to extract before processing.
   
   ## ACCURACY
   Base all extracted features on explicit evidence in the text.
   ```

3. **Use Long Context Effectively**:
   - Process batches of up to 100 responses per API call
   - Use XML delimiters to separate responses
   - Place instructions at both top and bottom for optimal performance

## Core Problems with Current Implementation

1. **Context Loss**: All 10,588 text responses are mixed together, losing question context
2. **Sampling Bias**: Only 500 responses analyzed out of 10,588 (4.7%)
3. **Shallow Analysis**: Single LLM call extracts generic themes
4. **No Feature Engineering**: Missing sentiment, urgency, stakeholder classification
5. **Poor Evidence**: No systematic quote extraction or validation

## Proposed Architecture

### Phase 1: Deep Feature Extraction (40-60 hours of compute)

#### 1.1 Response-Level Analysis
For each of the 10,588 text responses:
```python
{
    "response_id": "survey_123_q5",
    "question_id": "q5_equal_access", 
    "respondent_id": "resp_123",
    "raw_text": "No, accessibility is a major issue...",
    "features": {
        "sentiment": "negative",
        "sentiment_confidence": 0.92,
        "themes": ["accessibility", "equity", "barriers"],
        "urgency": "high",
        "stakeholder_type": "artist",
        "stakeholder_confidence": 0.87,
        "key_phrases": ["major issue", "transportation barriers"],
        "intent": "problem_identification",
        "word_count": 45,
        "readability_score": 8.2
    }
}
```

#### 1.2 Question-Level Aggregation
For each of the 18 questions:
```python
{
    "question_id": "q5_equal_access",
    "question_text": "Do you feel that all Austin residents have equal access...",
    "response_count": 1145,
    "aggregated_features": {
        "dominant_themes": [
            {"theme": "transportation_barriers", "count": 423, "percentage": 36.9},
            {"theme": "cost_barriers", "count": 387, "percentage": 33.8},
            {"theme": "geographic_inequity", "count": 298, "percentage": 26.0}
        ],
        "sentiment_distribution": {
            "negative": 782,
            "neutral": 234, 
            "positive": 129
        },
        "urgency_scores": {
            "high": 567,
            "medium": 423,
            "low": 155
        },
        "representative_quotes": [
            {
                "text": "Transportation is the biggest barrier for East Austin residents",
                "respondent_type": "community_member",
                "theme": "transportation_barriers"
            }
        ]
    }
}
```

### Phase 2: Multi-Pass LLM Analysis

#### Pass 1: Individual Response Processing
- **Input**: Single response + question context
- **Output**: Structured features (sentiment, themes, urgency)
- **Volume**: 10,588 LLM calls (cached)
- **Cost**: ~$50-100 in API costs

#### Pass 2: Question-Level Synthesis  
- **Input**: All responses for one question
- **Output**: Patterns, contradictions, consensus points
- **Volume**: 18 LLM calls (one per question)

#### Pass 3: Cross-Question Analysis
- **Input**: Aggregated features across questions
- **Output**: Meta-themes, strategic insights
- **Volume**: 5-10 LLM calls

#### Pass 4: Program-Specific Analysis
- **Input**: Responses mentioning specific programs
- **Output**: Program-specific recommendations
- **Volume**: 6 LLM calls (one per program)

### Phase 3: Feature Storage Architecture

```
data/
├── features/
│   ├── responses/          # Individual response features
│   │   ├── q1/            # Organized by question
│   │   │   ├── batch_001.json
│   │   │   └── batch_002.json
│   │   └── q2/
│   ├── questions/         # Question-level aggregations
│   │   ├── q1_aggregated.json
│   │   └── q2_aggregated.json
│   ├── themes/            # Cross-question themes
│   │   ├── transportation.json
│   │   └── funding_barriers.json
│   └── programs/          # Program-specific insights
│       ├── nexus.json
│       └── thrive.json
├── llm_cache/            # Raw LLM responses
└── analysis_runs/        # Versioned analysis results
```

## Implementation Steps

### Step 1: Build Feature Extraction Module (Week 1)
```python
class ResponseFeatureExtractor:
    def extract_features(self, response: str, question: str) -> ResponseFeatures:
        # 1. Clean and preprocess text
        # 2. Extract basic features (length, readability)
        # 3. Call LLM for semantic features
        # 4. Validate and structure output
        # 5. Cache results
```

### Step 2: Implement Question Analyzer (Week 1-2)
```python
class QuestionAnalyzer:
    def analyze_question(self, question_id: str, responses: List[str]) -> QuestionInsights:
        # 1. Load all responses for question
        # 2. Extract features for each response
        # 3. Aggregate patterns
        # 4. Identify representative quotes
        # 5. Generate question-specific visualizations
```

### Step 3: Build Cross-Question Synthesizer (Week 2)
```python
class CrossQuestionSynthesizer:
    def synthesize_insights(self, all_questions: Dict) -> StrategicInsights:
        # 1. Identify common themes across questions
        # 2. Find contradictions and tensions
        # 3. Map stakeholder perspectives
        # 4. Generate strategic recommendations
```

### Step 4: Create Program Analyzer (Week 3)
```python
class ProgramAnalyzer:
    def analyze_program(self, program_name: str) -> ProgramInsights:
        # 1. Filter responses mentioning program
        # 2. Extract program-specific feedback
        # 3. Identify improvement opportunities
        # 4. Generate targeted recommendations
```

## Quality Assurance Plan

### 1. Validation Framework
- **Human Review**: Sample 10% of extracted features for validation
- **Inter-rater Reliability**: Multiple reviewers for theme extraction
- **Statistical Validation**: Chi-square tests for theme significance

### 2. Audit Trail
- Every feature extraction logged with timestamp
- LLM prompts and responses preserved
- Version control for all analysis iterations

### 3. Reproducibility
- Deterministic random seeds
- Cached LLM responses
- Documented analysis parameters

## Resource Requirements

### Compute Resources
- **LLM API Calls**: ~10,000 calls @ $0.01/call = $100
- **Processing Time**: 40-60 hours (with caching)
- **Storage**: ~5GB for features and cache

### Human Resources
- **Lead Analyst**: 80 hours
- **Quality Reviewer**: 20 hours
- **Domain Expert**: 10 hours consultation

## Deliverables

### 1. Feature Database
- Structured JSON files with all extracted features
- Searchable by question, theme, stakeholder, program

### 2. Analysis Reports
- Question-by-question deep dives
- Cross-question synthesis
- Program-specific recommendations
- Stakeholder perspective analysis

### 3. Visualization Suite
- Question-specific dashboards
- Theme evolution charts
- Stakeholder comparison matrices
- Program performance indicators

### 4. Executive Insights
- Top 10 strategic findings
- Evidence-based recommendations
- Risk and opportunity analysis
- Implementation roadmap

## Success Criteria

1. **Coverage**: 100% of responses analyzed (no sampling)
2. **Depth**: Multi-dimensional features for each response  
3. **Accuracy**: 90%+ validation accuracy on sample
4. **Actionability**: Specific, evidence-based recommendations
5. **Traceability**: Every insight linked to source data

## Timeline

- **Week 1**: Feature extraction module + question analyzer
- **Week 2**: Cross-question synthesis + validation framework
- **Week 3**: Program analysis + report generation
- **Week 4**: Quality assurance + final deliverables

## Risk Mitigation

1. **LLM Failures**: Implement retry logic and fallback extractors
2. **Data Quality**: Build robust cleaning and validation pipeline
3. **Bias**: Use multiple prompts and validate with domain experts
4. **Cost Overrun**: Implement caching and batch processing

## Next Steps

1. Review and approve this plan
2. Set up development environment
3. Begin implementation of ResponseFeatureExtractor
4. Schedule weekly progress reviews

---

This plan ensures we deliver PhD-quality analysis that provides deep, actionable insights for ACME's strategic planning.