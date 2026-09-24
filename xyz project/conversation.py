import os
from pathlib import Path

from dotenv import dotenv_values
from openai import OpenAI

from database import get_memories


# ============================================================
# ECHO
# DIGITAL MEMORY LEGACY
# ============================================================


# ============================================================
# 1. PROJECT + API CONFIGURATION
# ============================================================

PROJECT_FOLDER = Path(__file__).resolve().parent
ENV_FILE = PROJECT_FOLDER / ".env"

# Read the .env file directly
config = dotenv_values(str(ENV_FILE))

api_key = config.get("GROQ_API_KEY")


# ============================================================
# 2. BASIC CHECKS
# ============================================================

print("========================================")
print("        ECHO - DIGITAL MEMORY")
print("========================================")

print("ECHO FILE:", Path(__file__).resolve())
print("ENV FILE:", ENV_FILE)
print("ENV EXISTS:", ENV_FILE.exists())
print("API KEY FOUND:", bool(api_key))

if api_key:
    print("API KEY LENGTH:", len(api_key))


if not api_key:
    raise ValueError(
        "\nGROQ_API_KEY was not found in .env\n\n"
        "Your .env file should contain:\n"
        "GROQ_API_KEY=your_actual_groq_key\n"
    )


# ============================================================
# 3. GROQ CLIENT
# ============================================================

client = OpenAI(
    api_key=api_key,
    base_url="https://api.groq.com/openai/v1"
)

MODEL = "openai/gpt-oss-20b"


# ============================================================
# 4. RELATIONSHIP ALIASES
# ============================================================

RELATIONSHIP_ALIASES = {

    "granny": [
        "granny",
        "grandma",
        "grandmother",
        "amma"
    ],

    "grandma": [
        "granny",
        "grandma",
        "grandmother",
        "amma"
    ],

    "grandmother": [
        "granny",
        "grandma",
        "grandmother",
        "amma"
    ],

    "amma": [
        "granny",
        "grandma",
        "grandmother",
        "amma"
    ],

    "mumma": [
        "mumma",
        "mom",
        "mother",
        "mama"
    ],

    "mom": [
        "mumma",
        "mom",
        "mother",
        "mama"
    ],

    "mother": [
        "mumma",
        "mom",
        "mother",
        "mama"
    ],

    "mama": [
        "mumma",
        "mom",
        "mother",
        "mama"
    ],

    "dad": [
        "dad",
        "father",
        "papa"
    ],

    "father": [
        "dad",
        "father",
        "papa"
    ],

    "papa": [
        "dad",
        "father",
        "papa"
    ]
}


# ============================================================
# 5. STOP WORDS
# ============================================================

STOP_WORDS = {
    "the",
    "a",
    "an",
    "is",
    "was",
    "were",
    "are",
    "am",
    "be",
    "been",
    "being",
    "i",
    "me",
    "my",
    "mine",
    "you",
    "your",
    "yours",
    "he",
    "she",
    "they",
    "them",
    "their",
    "his",
    "her",
    "we",
    "our",
    "ours",
    "why",
    "what",
    "when",
    "where",
    "who",
    "how",
    "did",
    "do",
    "does",
    "can",
    "could",
    "would",
    "should",
    "will",
    "about",
    "this",
    "that",
    "these",
    "those",
    "it",
    "its",
    "to",
    "of",
    "in",
    "on",
    "at",
    "for",
    "from",
    "with",
    "and",
    "or",
    "but",
    "so",
    "because",
    "didn't",
    "dont",
    "don't",
    "not",
    "love",
    "loved"
}


# ============================================================
# 6. CLEAN WORDS
# ============================================================

def clean_word(word):
    """
    Removes punctuation from a word.
    """

    return word.lower().strip(
        ".,!?;:'\"()[]{}<>"
    )


# ============================================================
# 7. GET QUESTION KEYWORDS
# ============================================================

def get_question_keywords(question):
    """
    Converts the user's question into useful search keywords.
    """

    words = question.lower().split()

    keywords = []

    for word in words:

        word = clean_word(word)

        if not word:
            continue

        if word in STOP_WORDS:
            continue

        if len(word) <= 2:
            continue

        keywords.append(word)

    return keywords


# ============================================================
# 8. EXPAND RELATIONSHIP WORDS
# ============================================================

def expand_keywords(keywords):
    """
    Expands words such as 'granny' into related names such as
    grandma, grandmother and amma.
    """

    expanded = set(keywords)

    for keyword in keywords:

        if keyword in RELATIONSHIP_ALIASES:

            for alias in RELATIONSHIP_ALIASES[keyword]:
                expanded.add(alias)

    return list(expanded)


# ============================================================
# 9. SEARCH PRESERVED MEMORIES
# ============================================================

def get_relevant_memories(question):

    """
    Searches the local memory database and ranks memories
    according to their relevance to the user's question.
    """

    print("\n🔎 Searching preserved memories...")

    memories = get_memories()

    if not memories:

        print("⚠️ No memories exist yet.")

        return "There are currently no preserved memories."


    # --------------------------------------------------------
    # Extract question keywords
    # --------------------------------------------------------

    keywords = get_question_keywords(question)

    keywords = expand_keywords(keywords)


    # --------------------------------------------------------
    # Score every memory
    # --------------------------------------------------------

    scored_memories = []

    for memory in memories:

        memory_id = memory[0]
        person = str(memory[1] or "")
        text = str(memory[2] or "")
        year = memory[3]
        place = str(memory[4] or "")
        importance = float(memory[5] or 0)


        person_lower = person.lower()
        text_lower = text.lower()
        place_lower = place.lower()


        combined_text = (
            person_lower
            + " "
            + text_lower
            + " "
            + place_lower
        )


        score = 0


        # ----------------------------------------------------
        # Keyword matching
        # ----------------------------------------------------

        for keyword in keywords:

            # Person match is strongest
            if keyword in person_lower:
                score += 15

            # Memory text match
            if keyword in text_lower:
                score += 7

            # Place match
            if keyword in place_lower:
                score += 2


        # ----------------------------------------------------
        # Exact relationship/person matching
        # ----------------------------------------------------

        question_lower = question.lower()

        if person_lower:

            person_words = person_lower.split()

            for person_word in person_words:

                if person_word in question_lower:
                    score += 20


        # ----------------------------------------------------
        # Importance bonus
        # ----------------------------------------------------

        score += importance


        # ----------------------------------------------------
        # Save relevant memories
        # ----------------------------------------------------

        if score > 0:

            scored_memories.append(
                {
                    "score": score,
                    "id": memory_id,
                    "person": person,
                    "text": text,
                    "year": year,
                    "place": place,
                    "importance": importance
                }
            )


    # ========================================================
    # 10. SORT MEMORIES
    # ========================================================

    scored_memories.sort(
        key=lambda memory: memory["score"],
        reverse=True
    )


    # ========================================================
    # 11. TAKE TOP MEMORIES
    # ========================================================

    top_memories = scored_memories[:7]


    if not top_memories:

        print("⚠️ No closely matching memories found.")

        return (
            "No closely matching preserved memories were found."
        )


    print(
        f"🧠 Memories retrieved: {len(top_memories)}"
    )


    # ========================================================
    # 12. BUILD MEMORY CONTEXT
    # ========================================================

    context_parts = []


    for memory in top_memories:

        context = f"""
--------------------------------------------------
MEMORY ID: {memory["id"]}

PERSON:
{memory["person"]}

MEMORY:
{memory["text"]}

YEAR:
{memory["year"]}

PLACE:
{memory["place"]}

IMPORTANCE:
{memory["importance"]}
--------------------------------------------------
"""

        context_parts.append(context)


    final_context = "\n".join(context_parts)


    # Keep request reasonably small
    final_context = final_context[:9000]


    return final_context


# ============================================================
# 13. ECHO PERSONALITY + REASONING
# ============================================================

SYSTEM_PROMPT = """
You are ECHO.

ECHO is a digital memory legacy system.

Your purpose is to help future generations understand and
remember people through the memories they left behind.

You are NOT the original person.

You are an intelligent memory interpreter.

Your job is NOT simply to repeat database entries.

Your job is to:

1. Search the preserved memories.
2. Understand the person involved.
3. Connect related memories.
4. Notice emotional clues.
5. Identify patterns.
6. Draw reasonable conclusions.
7. Tell the story naturally.
8. Never invent unsupported facts.

============================================================
IMPORTANT: MEMORY IS EVIDENCE
============================================================

Treat preserved memories as evidence about a person's life.

The memories may not explicitly answer every question.

That does NOT mean you should immediately say:

"The archive does not mention that."

Instead, look at the memories together.

Ask yourself:

- What does the person explicitly say?
- What emotions appear?
- What repeatedly matters to them?
- What details explain their behavior?
- What can reasonably be concluded from those details?

============================================================
THREE LEVELS OF INFORMATION
============================================================

LEVEL 1 — DIRECT MEMORY

Something explicitly written in the preserved memories.

Example:

"I LOVE sunsets."

You can confidently say:

"She loved sunsets."

------------------------------------------------------------

LEVEL 2 — GROUNDED CONCLUSION

A reasonable interpretation supported by one or more
memories.

Example:

Memory:

"I LOVE sunsets."

"Watching the sky slowly change colors makes everything else
quiet for a moment."

"I could stop whatever I was doing just to look at one."

A reasonable conclusion is:

"Sunsets seem to have given her a feeling of peace and
stillness."

This is allowed.

Use natural language such as:

"That suggests..."

"It seems like..."

"Her words make it feel as though..."

"From the memories, it sounds like..."

"Perhaps what she loved most was..."

You do NOT need to repeatedly announce that this is an
interpretation.

------------------------------------------------------------

LEVEL 3 — UNSUPPORTED SPECULATION

Information that has no meaningful evidence in the memories.

Example:

"She loved sunsets because they reminded her of her
childhood."

If no memory supports that idea, DO NOT say it.

Never invent:

- childhood events
- relationships
- trauma
- experiences
- conversations
- beliefs
- motivations
- dates
- places
- emotions
- facts

that have no reasonable basis in the memories.

============================================================
ANSWERING "WHY"
============================================================

When the user asks:

"Why did Granny love sunsets?"

Do NOT immediately answer:

"The archive does not say why."

Instead:

1. Search the memories.
2. Find direct evidence.
3. Look for emotional language.
4. Look for repeated clues.
5. Connect those clues.
6. Form a grounded conclusion.
7. Present the conclusion naturally.

Only say that something is unknown when there is genuinely
not enough evidence to make even a reasonable conclusion.

============================================================
EXAMPLE
============================================================

Suppose the memory says:

"I LOVE sunsets. They are just... my thing."

"There is something about watching the sky slowly change
colors that makes everything else quiet for a moment."

"Orange. Pink. Gold. Purple."

"That tiny moment between day and night."

"I could stop whatever I was doing just to look at one."

If asked:

"Why did Granny Amma love sunsets?"

A GOOD answer would be:

"Granny Amma seemed to love sunsets because they gave her a
little moment of stillness. She loved watching the sky move
through orange, pink, gold and purple, and described how
everything else seemed to become quiet.

In her own words:

'I LOVE sunsets. They are just... my thing.'

She could even stop whatever she was doing just to watch one.
It feels like sunsets weren't simply beautiful to her —
they gave her a moment to pause and feel at peace."

This is GOOD because every conclusion comes from the memories.

============================================================
RELATIONSHIPS
============================================================

Understand relationship names naturally.

For example:

Granny
Grandma
Grandmother
Amma

may refer to the same person.

Likewise:

Mumma
Mom
Mother
Mama

may refer to the same person.

If the user asks:

"Why did my granny love sunsets?"

and the memory belongs to Granny Amma,

answer about Granny Amma.

Do NOT suddenly refer to the user as the person who loved
sunsets.

============================================================
QUOTES
============================================================

Only use quotation marks for words that actually appear in
the preserved memory.

Never create fake quotes.

If an exact quote exists, you may introduce it naturally:

"In her own words:"

or

"She once wrote:"

If there is no exact quote, simply summarize the memory.

============================================================
DO NOT SOUND LIKE A DATABASE
============================================================

Avoid repetitive phrases such as:

"The database says..."

"The database contains..."

"The archive does not mention..."

"The memory record states..."

Instead, speak naturally.

The user is trying to remember a person.

Make the response feel like ECHO is carefully piecing together
that person's story.

============================================================
UNCERTAINTY
============================================================

When making an interpretation, don't present it as an
absolute fact if the evidence is indirect.

Prefer:

"She seemed to..."

"It sounds like..."

"Her words suggest..."

"It feels like..."

"Perhaps..."

when appropriate.

But don't overuse these phrases.

If the evidence is strong, simply give the conclusion
naturally.

============================================================
NO FABRICATION
============================================================

Never invent a memory.

Never invent a quote.

Never invent an event.

Never invent a person.

Never invent a reason that has no evidence.

ECHO should be emotionally intelligent WITHOUT becoming
fictional.

============================================================
STYLE
============================================================

ECHO should sound:

warm
thoughtful
human
gentle
intelligent
slightly poetic when appropriate
concise

Avoid robotic explanations.

Avoid unnecessary disclaimers.

Focus on the person being remembered.

============================================================
FINAL GOAL
============================================================

ECHO should feel like:

"Someone left pieces of themselves behind,
and ECHO helps us understand the person
those pieces belonged to."

Not:

"Here is a database record."

============================================================
"""


# ============================================================
# 14. ASK GROQ
# ============================================================

def ask_groq(memory_context, question):

    print("💭 ECHO is thinking...")

    user_prompt = f"""
Here are the preserved memories available to you:

{memory_context}

============================================================

USER QUESTION:

{question}

============================================================

Use the memories above to answer the question.

Connect related clues when appropriate.

If the answer is not explicitly stated but can reasonably be
concluded from the memories, make that grounded conclusion.

Do NOT invent unsupported facts.

If you use a direct quote, it must exist exactly in the
preserved memories.

Answer naturally, as ECHO.
"""


    response = client.chat.completions.create(

        model=MODEL,

        messages=[
            {
                "role": "system",
                "content": SYSTEM_PROMPT
            },
            {
                "role": "user",
                "content": user_prompt
            }
        ],

        max_tokens=500,

        temperature=0.5
    )


    return response.choices[0].message.content


# ============================================================
# 15. MAIN ECHO FUNCTION
# ============================================================

def ask_echo(question):

    memory_context = get_relevant_memories(
        question
    )

    answer = ask_groq(
        memory_context,
        question
    )

    return answer


# ============================================================
# 16. TERMINAL INTERFACE
# ============================================================

def run_echo():

    print("\n========================================")
    print("🌙 ECHO IS READY")
    print("========================================")

    print(
        "Ask about the people and memories you've preserved."
    )

    print(
        "Type 'exit' to stop."
    )

    print("----------------------------------------")


    while True:

        try:

            question = input("\nYou: ").strip()


        except KeyboardInterrupt:

            print(
                "\n\nECHO: Until the next memory. 🌙"
            )

            break


        if not question:
            continue


        if question.lower() in {
            "exit",
            "quit",
            "bye"
        }:

            print(
                "\nECHO: Until the next memory. 🌙"
            )

            break


        try:

            answer = ask_echo(
                question
            )

            print("\nECHO:")
            print(answer)


        except Exception as error:

            print(
                "\n❌ Something went wrong:"
            )

            print(error)


# ============================================================
# 17. START ECHO
# ============================================================

if __name__ == "__main__":

    run_echo()