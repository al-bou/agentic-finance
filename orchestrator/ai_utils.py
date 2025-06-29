import openai
import os
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

def generate_price_comment(result: dict) -> str:
    """
    Generate a price movement comment using OpenAI API.
    """
    if not openai.api_key:
        return "⚠ No OpenAI API key configured."

    prompt = (
        f"The stock {result['ticker']} has an open-close delta of {result['metrics'].get('delta_oc', 'N/A')}% "
        f"and a high-low delta of {result['metrics'].get('delta_hl', 'N/A')}%. "
        f"The alert status is {'TRIGGERED' if result['alert'] else 'not triggered'}. "
        f"Comment on this movement in simple financial terms."
    )

    try:
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a financial analyst bot."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=100
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"⚠ Error generating AI comment: {str(e)}"
