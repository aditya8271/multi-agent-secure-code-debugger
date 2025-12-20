# agents/validator.py

import google.generativeai as genai
import json
from google.generativeai.types import HarmCategory, HarmBlockThreshold

model = genai.GenerativeModel('models/gemini-2.5-flash-lite')

def validate_fix(original_code: str, fixed_code: str, issues: dict) -> dict:
    """
    Enhanced Validator Agent: Comprehensive code validation with safety overrides.
    """
    from utils.prompts import VALIDATOR_PROMPT
    
    try:
        issues_text = json.dumps(issues, indent=2)
        prompt = VALIDATOR_PROMPT.format(
            original_code=original_code,
            fixed_code=fixed_code,
            issues=issues_text
        )
        
        # Configure safety settings to allow validation of security fixes
        safety_settings = {
            HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
        }
        
        response = model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=0.3,
                top_p=0.8,
                top_k=40,
            ),
            safety_settings=safety_settings
        )
        
        result_text = response.text.strip()
        
        # Extract JSON
        if "```json" in result_text:
            result_text = result_text.split("```json")[1].split("```")[0].strip()
        elif "```" in result_text:
            result_text = result_text.split("```")[1].split("```")[0].strip()
        
        result = json.loads(result_text)
        
        # Ensure all fields exist
        defaults = {
            "validation_status": "UNKNOWN",
            "overall_score": 0,
            "syntax_score": 0,
            "logic_score": 0,
            "security_score": 0,
            "performance_score": 0,
            "readability_score": 0,
            "issues_fixed": 0,
            "remaining_issues": [],
            "new_issues": [],
            "recommendations": [],
            "summary": "Validation completed"
        }
        
        for key, default_value in defaults.items():
            if key not in result:
                result[key] = default_value
        
        return {
            "success": True,
            "data": result
        }
        
    except json.JSONDecodeError as e:
        return {
            "success": False,
            "error": "❌ Failed to parse validation response",
            "details": str(e),
            "raw_response": result_text if 'result_text' in locals() else response.text
        }
    
    except Exception as e:
        return {
            "success": False,
            "error": f"❌ Validator error: {str(e)}"
        }