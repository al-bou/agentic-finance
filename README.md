# Agentic Finance

💹 **Agentic Finance** is an open-source project demonstrating how to build a smart financial assistant powered by an *agentic RAG* (Retrieval-Augmented Generation) architecture.

## 🌟 Project Goal
Create a prototype that:
- Retrieves real-time stock prices
- Extracts key KPIs from quarterly report PDFs
- Collects the latest financial news
- Generates actionable summaries using an LLM

This project serves as the foundation for a YouTube series on building an AI-augmented financial assistant.

## 🚀 Quick Start

1 Clone the repository:
```bash
git clone https://github.com/al-bou/agentic-finance.git
cd agentic-finance
````

2 Install dependencies:
```python
pip install -r requirements.txt
````

3 Run a basic agent:

```bash
python agents/price_agent.py
````

📹 Follow the YouTube series
➡ [YouTube channel](https://www.youtube.com/channel/UCQiHRJlmZrxg0AaEvwJpMNg/)

## ⚙️ Conda environment setup (optional but recommended)

```bash
conda env create -f environment.yml
conda activate agentic-finance
````

![CI](https://github.com/al-bou/agentic-finance/actions/workflows/ci.yml/badge.svg)

📜 License
MIT