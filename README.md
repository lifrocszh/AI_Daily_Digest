# Overview

An automated "Data-Agent" that tracks the latest advancements in AI. Every morning, the agent scrapes research papers and industry news, uses DeepSeek LLM to prioritize content based on my current university projects, and delivers a curated brief via Telegram.

# The Stack

## Automation

GitHub Actions (Cron-scheduled at 00:00 UTC).

## AI Brain

DeepSeek API (OpenAI-compatible SDK).

## Data Sources

ArXiv (cs.LG), Hacker News, Towards Data Science.

## Packages

Python, BeautifulSoup4 (Scraping), Asynchronous Telegram Bot API.

# Quick Start

1. Clone the repository.
2. Install dependencies with `pip install -r requirements.txt`, or `uv sync` if you are using uv as a package manager.
3. Set up your environment variables (`DEEPSEEK_API_KEY`, `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID`).
4. Run the bot with `python main.py`.
