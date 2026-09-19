import logging

from pydantic import ValidationError

from app.core.config import settings
from app.schemas.analysis import AIResponseModel

logger = logging.getLogger(__name__)

async def analyze_impact(payload: dict) -> dict:
    if settings.MOCK_AI:
        raw_response = {
          "forecast": {
            "costRange": "+$10 to +$50/mo",
            "performanceRange": "No significant change expected"
          },
          "confidence": 0.85,
          "evidence": [{"source": "mock_cloudwatch", "metric": "cpu_utilization", "value": "45%"}],
          "assumptions": ["Traffic remains constant"],
          "recommendations": [
            {
              "action": "Monitor DynamoDB consumed capacity",
              "reason": "New query pattern might increase costs",
              "priority": "MEDIUM",
              "affectedResource": "DynamoDB Table"
            }
          ]
        }
    else:
        # In a real scenario, this would call the AI endpoint and parse JSON.
        # For this MVP, if MOCK_AI is false but not implemented, return empty.
        # Person 1 will implement this.
        raw_response = {}

    try:
        # Validate using Pydantic
        validated_data = AIResponseModel(**raw_response)
        return validated_data.model_dump()
    except ValidationError as e:
        logger.error(f"AI Response Validation Error: {e}")
        raise ValueError("AI response failed schema validation")
