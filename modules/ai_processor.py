from openai import OpenAI
from config.settings import OPENROUTER_API_KEY, OPENROUTER_BASE_URL, MODEL_NAME
import time

class AIProcessor:
    def __init__(self):
        self.client = OpenAI(
            base_url=OPENROUTER_BASE_URL,
            api_key=OPENROUTER_API_KEY
        )

    def rewrite_content(self, original_text):
        """Use AI to rewrite/rephrase the content."""
        prompt = f"""
        Please rewrite the following content while preserving its core meaning and style.
        Maintain the original structure but improve clarity and flow where needed.
        Do not add new information or remove key details.
        
        Original Content:
        {original_text}
        
        Rewritten Version:
        """
        response = self._get_ai_response(prompt)
        return response

    def review_content(self, content):
        """Use AI to review and suggest improvements for the content."""
        prompt = f"""
        Please review the following content and provide an improved version with corrections:
        - Fix any grammatical errors
        - Improve clarity and coherence
        - Suggest better word choices where appropriate
        - Ensure consistent style and tone
        
        Content to Review:
        {content}
        
        Reviewed Version with Improvements:
        """
        response = self._get_ai_response(prompt)
        return response

    def _get_ai_response(self, prompt):
        """Get response from the AI model with error handling."""
        try:
            completion = self.client.chat.completions.create(
                extra_headers={
                    "HTTP-Referer": "https://github.com/yourusername/content-rewriter",
                    "X-Title": "Content Rewriter System"
                },
                model=MODEL_NAME,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,
                max_tokens=2000
            )
            return completion.choices[0].message.content
        except Exception as e:
            print(f"Error getting AI response: {e}")
            # Retry once after a short delay
            time.sleep(2)
            try:
                completion = self.client.chat.completions.create(
                    extra_headers={
                        "HTTP-Referer": "https://github.com/yourusername/content-rewriter",
                        "X-Title": "Content Rewriter System"
                    },
                    model=MODEL_NAME,
                    messages=[
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    temperature=0.7,
                    max_tokens=2000
                )
                return completion.choices[0].message.content
            except Exception as e:
                print(f"Second attempt failed: {e}")
                return None
