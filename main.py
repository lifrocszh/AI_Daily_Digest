import os
from dotenv import load_dotenv
from datetime import datetime
import feedparser
import requests
import asyncio
from bs4 import BeautifulSoup
from openai import OpenAI
from telegram import Bot

load_dotenv()

DEEPSEEK_KEY = os.getenv("DEEPSEEK_API_KEY")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
# CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

client = OpenAI(api_key=DEEPSEEK_KEY, base_url="https://api.deepseek.com")

def get_subscribers():
    raw_list = os.getenv("SUBSCRIBER_LIST", "")
    subscriber_ids = [s.strip() for s in raw_list.split(",") if s.strip()]
    return subscriber_ids

def get_article_content(url):
    try:
        response = requests.get(url, timeout=10, headers={'User-Agent': 'Mozilla/5.0'})
        soup = BeautifulSoup(response.content, 'html.parser')

        # Remove noise (scripts, styles, nav, footers)
        for element in soup(['script', 'style', 'nav', 'footer', 'header']):
            element.decompose()

        # Get text and limit to 2000 words to avoid token limits
        text = soup.get_text(separator=' ', strip=True)
        return text[:8000]
    except Exception as e:
        return f"Could not scrape: {e}"


async def run_digest():
    feeds = ["https://news.ycombinator.com/rss",
        "http://export.arxiv.org/rss/cs.LG",
        "https://towardsdatascience.com/feed"]
    entries = []
    for url in feeds:
        f = feedparser.parse(url)
        entries.extend(f.entries[:2])

    # Prepare data for LLM
    data_for_ai = []
    for e in entries:
        content = get_article_content(e.link)
        data_for_ai.append(f"Title: {e.title}\nLink: {e.link}\nContent: {content}\n---")

    prompt = f"""
    Format the response for a Telegram user:
    1. Use a clear title with an emoji for each article.
    2. Provide 2 short and concise bullet points per article.
    3. Ensure there is a horizontal line or clear spacing between articles.
    4. Include a link to the article.
    Articles:
    {chr(10).join(data_for_ai)}
    """

    print(f'Prompt length: {len(prompt)}')

    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7
    )

    ai_summary = response.choices[0].message.content
    usage = response.usage
    formatted_date = datetime.now().strftime("%b %d, %Y")
    header = f"🚀 *Daily AI Research Digest*\n📅 {formatted_date}\n\n"

    stats_footer = (
        f"\n\n`──────────────────────────`"
        f"\n🤖 **System Stats**"
        f"\n`Prompt tokens:     {usage.prompt_tokens}`"
        f"\n`Completion tokens: {usage.completion_tokens}`"
        f"\n`Total tokens:      {usage.total_tokens}`"
    )

    final_message = header + ai_summary + stats_footer
    user_ids = get_subscribers()

    bot = Bot(token=TELEGRAM_TOKEN)
    for user_id in user_ids:
        try:
            await bot.send_message(chat_id=user_id, text=final_message, parse_mode='Markdown')
            # Small sleep to avoid Telegram rate limits (30 msgs/second)
            await asyncio.sleep(0.05)
        except Exception as e:
            print(f"Failed to send to {user_id}: {e}")

if __name__ == "__main__":
    asyncio.run(run_digest())
