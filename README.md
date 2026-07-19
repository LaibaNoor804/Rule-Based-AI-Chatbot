# RuleBot Pro — Rule-Based AI Chatbot

An upgraded version of the classic rule-based chatbot. Instead of a single
Python file with a hardcoded dictionary, this splits the project into
proper layers: data, logic, and interface — with typo-tolerant matching,
conversation memory, and live customization.

## What's different from a basic version?

| Basic chatbot | RuleBot Pro |
|---|---|
| Responses hardcoded in Python | Responses stored in `data/knowledge_base.json` — editable without touching code |
| Exact string match only (`"hello"` ≠ `"helo"`) | Fuzzy matching — typos and rephrasing still work |
| No memory | Full conversation history tracked per session |
| Fixed replies | Multiple possible replies per topic, chosen randomly, so it feels less robotic |
| Terminal only | Terminal **and** a browser chat UI (Streamlit) |
| Not customizable | Users can teach it new Q&A pairs live, which get saved permanently |

## Files — what each one does

```
rulebot_pro/
├── app.py                 # Browser chat interface (streamlit run app.py)
├── chatbot_cli.py          # Terminal chat interface (python3 chatbot_cli.py)
├── requirements.txt        # Libraries needed
├── README.md                # This file
├── data/
│   └── knowledge_base.json  # The bot's "brain" — all Q&A pairs live here
├── core/
│   └── engine.py             # The matching logic (fuzzy matching, teach feature, memory)
└── tests/
    └── test_engine.py         # Automated checks that the logic works correctly
```

## How the matching works (in plain terms)

1. Your message is compared against every known pattern in the knowledge base.
2. If it's an exact or near-exact match (like `"hello"` vs `"helo"`), the
   similarity score will be high.
3. If the highest score clears a threshold (72%), that topic's response is used.
4. If nothing scores high enough, RuleBot admits it doesn't know and suggests
   `help` or teaching it a new response.

This is still "rule-based" (no machine learning model, no external AI) —
it's just smarter rules than a plain dictionary lookup.

## Installation

```bash
cd rulebot_pro
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Usage

### Browser version (recommended)
```bash
streamlit run app.py
```
Opens a real chat interface in your browser, with a sidebar to teach the
bot new responses and clear the conversation.

### Terminal version
```bash
python3 chatbot_cli.py
```

### Teaching RuleBot something new
In either interface, type:
```
teach: what is java => Java is an object-oriented programming language
```
It's saved permanently to `data/knowledge_base.json` — next time you run
the bot, it will remember.

## Testing
```bash
pytest tests/ -v
```
9 automated tests cover exact matching, fuzzy/typo matching, the teach
feature, fallback behavior, and conversation history.

## Limitations & Future Work
- Matching is based on string similarity, not true language understanding —
  it can't handle complex sentences with multiple intents.
- A future version could use sentence embeddings for semantic matching
  (so "what's it cost" and "how much money" would be recognized as related
  even with zero shared words).
- Conversation memory currently resets each session; persisting it to a
  file or database would allow the bot to recall past conversations.

## Author
Laiba Noor — DecodeLabs Industrial Training Kit, Project 1 (Upgraded)
