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

def generate_investment_decision(result: dict, history: list) -> str:
    """
    Generate an investment decision using OpenAI based on the current result and history.
    """
    if not openai.api_key:
        return "⚠ No OpenAI API key configured."

    history_text = "\n".join([
        f"{h['timestamp']}: alert={h['alert']}, delta_oc={h['delta_oc']}%, delta_hl={h['delta_hl']}%"
        for h in history
    ])

    prompt = (
        f"Stock: {result['ticker']}\n"
        f"Current metrics: delta_oc={result['metrics'].get('delta_oc', 'N/A')}%, "
        f"delta_hl={result['metrics'].get('delta_hl', 'N/A')}%\n"
        f"Alert status: {'TRIGGERED' if result['alert'] else 'not triggered'}\n\n"
        f"Recent history:\n{history_text}\n\n"
        f"Based on this information, advise a decision: buy, hold, or sell. "
        f"Explain the reasoning in one paragraph. Return JSON in this format: "
        f'{{"decision": "...", "confidence": 0.0, "reasoning": "..."}}'
    )

    try:
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a financial analyst bot."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=200
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"⚠ Error generating decision: {str(e)}"
