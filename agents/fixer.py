# agents/fixer.py

import google.generativeai as genai
import json
from google.generativeai.types import HarmCategory, HarmBlockThreshold

model = genai.GenerativeModel('models/gemini-2.5-flash-lite')

def fix_code(code: str, issues: dict) -> dict:
    """
    Enhanced Fixer Agent: Fixes ALL types of code issues with safety overrides.
    """
    from utils.prompts import FIXER_PROMPT
    
    if not code or not code.strip():
        return {
            "success": False,
            "error": "⚠️ No code to fix"
        }
    
    if not issues or not issues.get("issues"):
        return {
            "success": True,
            "data": {
                "fixed_code": code,
                "fixes_applied": [],
                "improvements_summary": "No issues detected, code is already good!"
            }
        }
    
    try:
        issues_text = json.dumps(issues, indent=2)
        prompt = FIXER_PROMPT.format(code=code, issues=issues_text)
        
        # Configure safety settings to allow generation of secure code patterns
        safety_settings = {
            HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
        }
        
        response = model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=0.4,
                top_p=0.9,
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
        
        if "fixed_code" not in result or not result["fixed_code"]:
            return {
                "success": False,
                "error": "❌ AI couldn't generate fixed code",
                "raw_response": result_text
            }
        
        if "fixes_applied" not in result:
            result["fixes_applied"] = []
        if "improvements_summary" not in result:
            result["improvements_summary"] = f"Applied {len(result['fixes_applied'])} fixes"
        
        return {
            "success": True,
            "data": result
        }
        
    except json.JSONDecodeError as e:
        return {
            "success": False,
            "error": "❌ Failed to parse AI response",
            "details": str(e),
            "raw_response": result_text if 'result_text' in locals() else response.text
        }
    
    except Exception as e:
        return {
            "success": False,
            "error": f"❌ Fixer error: {str(e)}"
        }