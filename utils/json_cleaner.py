def clean_json_response(response: str) -> str:
    """
    Robustly extracts a JSON array or object from an LLM response string.
    Finds the outer-most brackets and returns the enclosed substring.
    """
    cleaned = response.strip()
    
    # Find first '[' or '{'
    start_arr = cleaned.find('[')
    start_obj = cleaned.find('{')
    
    start_idx = -1
    end_char = ''
    if start_arr != -1 and (start_obj == -1 or start_arr < start_obj):
        start_idx = start_arr
        end_char = ']'
    elif start_obj != -1:
        start_idx = start_obj
        end_char = '}'
        
    if start_idx != -1:
        end_idx = cleaned.rfind(end_char)
        if end_idx != -1 and end_idx > start_idx:
            return cleaned[start_idx:end_idx + 1]
            
    # Fallback to standard stripping if no delimiters found
    if cleaned.startswith("```json"):
        cleaned = cleaned[7:]
    if cleaned.endswith("```"):
        cleaned = cleaned[:-3]
    return cleaned.strip()
