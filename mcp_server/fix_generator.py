"""
OpenAI API integration for generating secure code fixes.
"""

from typing import Dict, List, Optional
from openai import OpenAI


class FixGenerator:
    """Generates secure code fixes using OpenAI API."""
    
    def __init__(self, api_key: str):
        """
        Initialize fix generator.
        
        Args:
            api_key: OpenAI API key
        """
        self.client = OpenAI(api_key=api_key)
        self.model = "gpt-4-turbo-preview"  # or "gpt-3.5-turbo" for faster/cheaper
    
    async def generate_fix(
        self,
        vulnerability: Dict[str, any],
        original_code: str,
        context: Optional[str] = None
    ) -> Dict[str, str]:
        """
        Generate a secure fix for a vulnerability.
        
        Args:
            vulnerability: Vulnerability dict with type, description, code_snippet
            original_code: The original vulnerable code
            context: Additional context about the codebase
            
        Returns:
            Dict with 'fixed_code', 'explanation', and 'recommendations'
        """
        prompt = self._build_prompt(vulnerability, original_code, context)
        
        try:
            # OpenAI API call (sync, but we're in async context - OpenAI SDK is sync)
            response = self.client.chat.completions.create(
                model=self.model,
                max_tokens=2000,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a security expert specializing in code vulnerability analysis and secure code fixes."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.3  # Lower temperature for more consistent, focused responses
            )
            
            response_text = response.choices[0].message.content
            
            # Parse response (simplified - in production, use structured output)
            return self._parse_response(response_text, vulnerability)
        except Exception as e:
            return {
                'fixed_code': original_code,  # Fallback to original
                'explanation': f"Error generating fix: {str(e)}",
                'recommendations': "Please review the code manually.",
            }
    
    def _build_prompt(
        self,
        vulnerability: Dict[str, any],
        original_code: str,
        context: Optional[str]
    ) -> str:
        """Build the prompt for OpenAI."""
        vuln_type = vulnerability.get('type', 'unknown')
        description = vulnerability.get('description', '')
        code_snippet = vulnerability.get('code_snippet', '')
        file_path = vulnerability.get('file', 'unknown')
        line_num = vulnerability.get('line', 'unknown')
        
        prompt = f"""You are a security expert helping to fix a {vuln_type.replace('_', ' ')} vulnerability.

Vulnerability Details:
- Type: {vuln_type}
- File: {file_path}
- Line: {line_num}
- Description: {description}
- Vulnerable Code: {code_snippet}

Original Code Context:
```python
{original_code}
"""

        if context:
            prompt += f"\nAdditional Context:\n{context}\n"

        prompt += """
Please provide:
1. A secure version of the code that fixes the vulnerability
2. A clear explanation of what was wrong and how the fix addresses it
3. Best practices recommendations to prevent similar issues

Format your response as:
FIXED_CODE:
[your fixed code here]

EXPLANATION:
[your explanation here]

RECOMMENDATIONS:
[your recommendations here]
"""
        return prompt
    
    def _parse_response(self, response_text: str, vulnerability: Dict) -> Dict[str, str]:
        """Parse OpenAI's response into structured format."""
        # Simple parsing - in production, use structured output or more robust parsing
        sections = {
            'fixed_code': '',
            'explanation': '',
            'recommendations': '',
        }
        
        current_section = None
        for line in response_text.split('\n'):
            if line.startswith('FIXED_CODE:'):
                current_section = 'fixed_code'
            elif line.startswith('EXPLANATION:'):
                current_section = 'explanation'
            elif line.startswith('RECOMMENDATIONS:'):
                current_section = 'recommendations'
            elif current_section and line.strip():
                sections[current_section] += line + '\n'
        
        # Fallback if parsing fails
        if not sections['fixed_code']:
            sections['fixed_code'] = vulnerability.get('code_snippet', '')
            sections['explanation'] = response_text
            sections['recommendations'] = "Review the code manually for security best practices."
        
        return sections
    
    async def generate_fixes_batch(
        self,
        vulnerabilities: List[Dict],
        code_context: Dict[str, str]
    ) -> List[Dict[str, any]]:
        """
        Generate fixes for multiple vulnerabilities.
        
        Args:
            vulnerabilities: List of vulnerability dicts
            code_context: Dict mapping file paths to full file content
            
        Returns:
            List of fix dicts with vulnerability info and fixes
        """
        fixes = []
        for vuln in vulnerabilities:
            file_path = vuln.get('file', '')
            original_code = code_context.get(file_path, vuln.get('code_snippet', ''))
            
            fix = await self.generate_fix(vuln, original_code)
            fixes.append({
                'vulnerability': vuln,
                'fix': fix,
            })
        
        return fixes

