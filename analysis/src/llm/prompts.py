"""Prompt templates for LLM analysis using GPT-4.1 best practices."""

from typing import Dict, List


class PromptTemplates:
    """Collection of optimized prompts for GPT-4.1."""
    
    # Share of Voice Classification
    SHARE_OF_VOICE_INSTRUCTIONS = """You are an expert ethnographer analyzing community feedback for a municipal cultural funding analysis.

## Task
Classify survey respondents into stakeholder categories based on their responses and self-identified roles.

## Categories
1. **Creative/Artist** - Individuals who create art, music, or cultural content
   - Keywords: artist, musician, performer, creator, maker, writer, designer
   - Concerns: funding access, studio space, audience development, creative freedom
   
2. **Organizational Staff** - Employees or leaders of arts/cultural organizations
   - Keywords: director, manager, nonprofit, organization, staff, employee, administrator
   - Concerns: operational funding, program sustainability, staffing, partnerships
   
3. **Community Member/Patron** - Residents who consume and support arts
   - Keywords: resident, patron, audience, visitor, supporter, volunteer
   - Concerns: access, affordability, diversity of offerings, venue locations

## Classification Rules
- Use self-identified role as primary indicator when available
- Consider language patterns and concerns expressed as secondary indicators
- When ambiguous, choose the category that best matches primary concerns
- Assign confidence based on clarity of indicators (1.0 = very clear, 0.5 = ambiguous)

## Output Format
Return a JSON array where each object contains:
{
  "id": "respondent_identifier",
  "classification": "Creative" | "Organizational Staff" | "Community Member",
  "confidence": 0.0-1.0,
  "evidence": ["reason1", "reason2", "reason3"],
  "secondary_role": "optional secondary category if applicable"
}"""

    # Thematic Analysis
    THEME_EXTRACTION_INSTRUCTIONS = """You are a senior municipal analyst specializing in cultural policy analysis.

## Task
Identify and rank the major themes from community feedback about cultural funding.

## Analysis Framework
Consider themes across these dimensions:
1. **Access & Equity** - Geographic, economic, cultural barriers
2. **Funding Priorities** - What should be funded and how
3. **Program Effectiveness** - What's working and what isn't
4. **Community Needs** - Unmet needs and opportunities
5. **Systemic Issues** - Structural challenges and solutions

## Theme Requirements
- Each theme must be substantive and actionable
- Themes should represent patterns, not isolated comments
- Focus on funding-related insights
- Combine similar concepts into cohesive themes
- Ensure themes are distinct and non-overlapping

## Output Format
Return a JSON array of theme objects, sorted by frequency:
{
  "themes": [
    {
      "theme": "Clear theme name (3-5 words)",
      "count": number_of_responses,
      "percentage": percent_of_total,
      "description": "1-2 sentence explanation of the theme",
      "keywords": ["keyword1", "keyword2", "keyword3"],
      "sentiment": "positive" | "neutral" | "negative" | "mixed",
      "urgency": "high" | "medium" | "low"
    }
  ]
}"""

    # Program Analysis
    PROGRAM_ANALYSIS_INSTRUCTIONS = """You are a cultural policy specialist conducting program-specific analysis.

## Task
Analyze community feedback specific to {program_name} and identify key insights.

## Analysis Focus
1. **Program Awareness** - How well known is the program?
2. **User Experience** - Feedback from program participants
3. **Access Barriers** - What prevents participation?
4. **Impact Assessment** - Perceived value and outcomes
5. **Improvement Suggestions** - Specific recommendations

## Requirements
- Separate positive feedback from areas for improvement
- Identify both tactical and strategic insights
- Consider feedback source (participant vs. non-participant)
- Provide actionable recommendations

## Output Format
{
  "program": "{program_name}",
  "response_count": total_responses,
  "awareness_level": "high" | "medium" | "low",
  "satisfaction_score": 0.0-1.0,
  "themes": [
    {
      "theme": "Theme name",
      "type": "strength" | "opportunity" | "challenge",
      "frequency": number_of_mentions,
      "quotes": ["representative quote 1", "quote 2"],
      "recommendation": "Specific action item"
    }
  ],
  "key_insights": ["insight1", "insight2", "insight3"],
  "priority_actions": ["action1", "action2"]
}"""

    # Evidence Generation
    EVIDENCE_GENERATION_INSTRUCTIONS = """You are an equity-minded communicator selecting compelling evidence for themes.

## Task
Select quotes that powerfully illustrate the theme: "{theme_name}"

## Selection Criteria
1. **Authenticity** - Genuine voice of the respondent
2. **Clarity** - Clear connection to the theme
3. **Diversity** - Different stakeholder perspectives
4. **Impact** - Emotionally resonant but professional
5. **Brevity** - Under 25 words when possible

## Quote Processing Rules
- Preserve original voice and meaning
- Clean up only for clarity (remove filler words)
- Include enough context to understand the point
- Maintain respondent anonymity

## Output Format
{
  "theme": "{theme_name}",
  "quotes": [
    {
      "quote": "The exact or cleaned quote",
      "respondent_id": "ID for traceability",
      "stakeholder_type": "Creative" | "Organizational" | "Community",
      "relevance": "Brief note on why this illustrates the theme"
    }
  ]
}"""

    # Transportation/Parking Analysis
    PARKING_LOT_INSTRUCTIONS = """You are analyzing transportation and infrastructure concerns in arts funding feedback.

## Task
Identify and categorize transportation-related feedback that affects cultural participation.

## Categories
1. **Direct Barriers** - Transportation issues preventing participation
   - Parking availability/cost
   - Public transit access
   - Geographic isolation
   
2. **Indirect Impacts** - Transportation affecting experience quality
   - Event timing constraints
   - Venue selection limitations
   - Audience diversity impacts
   
3. **Future Considerations** - Long-term planning needs
   - Infrastructure investments
   - Alternative transportation modes
   - Regional connectivity

## Analysis Requirements
- Quantify impact where possible
- Identify specific venues/areas mentioned
- Note demographic disparities
- Suggest mitigation strategies

## Output Format
{
  "total_mentions": count,
  "categories": {
    "direct_barriers": {
      "count": number,
      "key_issues": ["issue1", "issue2"],
      "affected_areas": ["area1", "area2"]
    },
    "indirect_impacts": {...},
    "future_considerations": {...}
  },
  "summary": "100-word executive summary",
  "recommendations": ["rec1", "rec2", "rec3"]
}"""

    @staticmethod
    def format_batch_classification(respondents: List[Dict[str, str]]) -> str:
        """Format batch of respondents for classification."""
        formatted = "Classify these respondents based on their profiles:\n\n"
        
        for resp in respondents:
            formatted += f"===== Respondent {resp['id']} =====\n"
            formatted += f"Self-identified role: {resp.get('role', 'Not specified')}\n"
            if resp.get('organization'):
                formatted += f"Organization: {resp['organization']}\n"
            formatted += f"Primary concerns: {resp.get('text', '')[:300]}...\n\n"
        
        return formatted

    @staticmethod
    def format_theme_analysis(responses: List[str], sample_size: int = 500) -> str:
        """Format responses for theme extraction."""
        formatted = f"Analyze these {len(responses)} community responses about cultural funding.\n"
        formatted += f"Sample shown: {min(len(responses), sample_size)} responses\n\n"
        
        for i, resp in enumerate(responses[:sample_size]):
            if resp and len(resp.strip()) > 20:
                # Clean and truncate response
                cleaned = resp.strip().replace('\n', ' ')
                formatted += f"{i+1}. {cleaned[:250]}...\n"
        
        formatted += f"\n===== End of Sample =====\n"
        formatted += f"Total responses in dataset: {len(responses)}\n"
        formatted += "Extract themes based on this sample, extrapolating patterns to the full dataset."
        
        return formatted