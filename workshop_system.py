import json
import os

from dotenv import load_dotenv

# Load variables from the .env file (e.g. OPENAI_API_KEY)
load_dotenv()

API_KEY = os.getenv("OPENAI_API_KEY")
USE_REAL_AI = bool(API_KEY) and API_KEY != "your-key-here"

if USE_REAL_AI:
    from openai import OpenAI

    client = OpenAI(api_key=API_KEY)

MODEL = "gpt-4o-mini"  # check your provider's docs for current model names

workshop_system = """You are a Jua Kali workshop assistant for Kamau Metalworks, Gikomba.
When a client describes a job, return ONLY a JSON object with these keys:
item (str), material (str), est_kes (int), days_to_complete (int), deposit_kes (int).
No other text."""

REQUIRED_KEYS = ["item", "material", "est_kes", "days_to_complete", "deposit_kes"]

job_requests = [
    "I need a sliding gate, about 10 feet wide, mild steel.",
    "Window grills for three windows, 3*4 feet wide, mild steel.",
    "A steel door frame for a standard door, hollow tube.",
]

# Used when there is no real API key. One response per request, in the same order.
simulated_responses = [
    '{"item": "sliding gate", "material": "mild steel", "est_kes": 38000, "days_to_complete": 5, "deposit_kes": 19000}',
    '{"item": "window grills x3", "material": "angle iron", "est_kes": 21000, "days_to_complete": 3, "deposit_kes": 10500}',
    '{"item": "door frame", "material": "hollow tube", "est_kes": 9800, "days_to_complete": 2, "deposit_kes": 4900}',
]


def get_quote(request, index):
    """Return a quote dict, from the real AI if a key is set, otherwise from simulation."""
    if USE_REAL_AI:
        completion = client.chat.completions.create(
            model=MODEL,
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": workshop_system},
                {"role": "user", "content": request},
            ],
        )
        raw = completion.choices[0].message.content
    else:
        raw = simulated_responses[index]

    quote = json.loads(raw)

    missing = [key for key in REQUIRED_KEYS if key not in quote]
    if missing:
        raise ValueError(f"Response is missing keys: {missing}")
    return quote


def print_quote(quote):
    print(f"  Item:      {quote['item']}")
    print(f"  Material:  {quote['material']}")
    print(f"  Quote:     KES {quote['est_kes']:,}")
    print(f"  Deposit:   KES {quote['deposit_kes']:,}")
    print(f"  Ready in:  {quote['days_to_complete']} days")
    print()


def main():
    mode = "live AI" if USE_REAL_AI else "simulated responses"
    print(f"Kamau Metalworks: AI Quotation Assistant ({mode})\n")

    for index, request in enumerate(job_requests):
        print(f"Client: {request}")
        try:
            quote = get_quote(request, index)
            print_quote(quote)
        except (json.JSONDecodeError, ValueError) as error:
            print(f"  Could not read the quote: {error}\n")
        except Exception as error:
            print(f"  Request failed: {error}\n")


if __name__ == "__main__":
    main()