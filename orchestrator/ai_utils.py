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

def generate_investment_decision(result: dict, stats: dict, trend: dict, news: str = ...) -> str:
    """
    Generate an investment decision with 52-week context.
    """
    if not openai.api_key:
        return "⚠ No OpenAI API key configured."

    trend_text = ""

    for period in ["5d", "30d", "90d", "180d", "365d"]:
        trend_text += (
            f"{period} => "
            f"mean_delta_oc={trend.get(f'mean_delta_oc_{period}', 'N/A')}%, "
            f"mean_delta_hl={trend.get(f'mean_delta_hl_{period}', 'N/A')}%, "
            f"mean_close={trend.get(f'mean_close_{period}', 'N/A')}, "
            f"close_slope={trend.get(f'close_slope_{period}', 'N/A')}\n"
        )

    # Exemple d'assemblage final dans le prompt
    prompt = (
        f"You are a financial analyst advising a trader.\n"
        f"Stock: {result['ticker']}\n"
        f"Current metrics: delta_oc={result['metrics'].get('delta_oc', 'N/A')}%, "
        f"delta_hl={result['metrics'].get('delta_hl', 'N/A')}%\n"
        f"Alert status: {'TRIGGERED' if result['alert'] else 'not triggered'}\n"
        f"52-week stats: mean_delta_oc={stats.get('mean_delta_oc', 'N/A')}%, std_delta_oc={stats.get('std_delta_oc', 'N/A')}%, "
        f"90th_delta_oc={stats.get('90th_delta_oc', 'N/A')}%, mean_delta_hl={stats.get('mean_delta_hl', 'N/A')}%, "
        f"std_delta_hl={stats.get('std_delta_hl', 'N/A')}%, 90th_delta_hl={stats.get('90th_delta_hl', 'N/A')}%\n"
        f"Trend indicators:\n{trend_text}"
        f"News context: {news}\n"
        f"Based on this information, advise buy, hold, or sell. "
        f"Explain reasoning. Return JSON: "
        f'{{"decision": "...", "confidence": 0.0, "reasoning": "...", "key_factors": ["...", "..."]}}'
    )


    try:
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a financial analyst bot."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=300
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"⚠ Error generating decision: {str(e)}"


