# agents/scanner.py

import google.generativeai as genai
import json
from google.generativeai.types import HarmCategory, HarmBlockThreshold

model = genai.GenerativeModel('models/gemini-2.5-flash-lite')

def scan_code(code: str) -> dict:
    """
    Enhanced Scanner Agent: Detects ALL types of code issues with safety overrides.
    """
    from utils.prompts import SCANNER_PROMPT
    
    if not code or not code.strip():
        return {
            "success": False,
            "error": "⚠️ Please enter some code to analyze"
        }
    
    try:
        prompt = SCANNER_PROMPT.format(code=code)
        
        # Configure safety settings to allow analysis of security vulnerabilities
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
        
        # Ensure all required fields exist
        if "issues" not in result:
            result["issues"] = []
        if "total_found" not in result:
            result["total_found"] = len(result.get("issues", []))
        if "summary" not in result:
            count = result["total_found"]
            result["summary"] = f"Found {count} issues" if count > 0 else "Code looks good!"
        
        # Calculate severity counts if missing
        if "critical_count" not in result:
            result["critical_count"] = sum(1 for i in result["issues"] if i.get("severity") == "Critical")
        if "high_count" not in result:
            result["high_count"] = sum(1 for i in result["issues"] if i.get("severity") == "High")
        if "medium_count" not in result:
            result["medium_count"] = sum(1 for i in result["issues"] if i.get("severity") == "Medium")
        if "low_count" not in result:
            result["low_count"] = sum(1 for i in result["issues"] if i.get("severity") == "Low")
        
        return {
            "success": True,
            "data": result
        }
        
    except json.JSONDecodeError as e:
        return {
            "success": False,
            "error": "❌ AI response parsing failed",
            "details": str(e),
            "raw_response": result_text if 'result_text' in locals() else response.text,
            "suggestion": "Try again with different code or simplify your input"
        }
    
    except Exception as e:
        error_msg = str(e).lower()
        if "dangerous_content" in error_msg or "safety" in error_msg:
            return {
                "success": False,
                "error": "🛡️ Safety Block: The content was flagged as dangerous.",
                "suggestion": "Ensure safety_settings are properly applied to the API call."
            }
        elif "quota" in error_msg or "limit" in error_msg:
            return {
                "success": False,
                "error": "⏱️ API rate limit reached",
                "suggestion": "Please wait a few seconds and try again"
            }
        else:
            return {
                "success": False,
                "error": f"❌ Scanner error: {str(e)}",
                "suggestion": "Please try again or contact support"
            }