from openai import OpenAI
import os, re, time, random
from dataclasses import dataclass
from typing import List, Optional, Tuple
from dotenv import load_dotenv
TEMP_A = 0.7
TEMP_B = 0.8
MAX_TOKENS_LINE = 60
SEED = 42
load_dotenv()
AGENT_A_SYSTEM = """You are Agent A, a poetic voice. Output EXACTLY one line (no extra lines).
- You write ODD-numbered lines (1,3,5,...).
- Keep consistent tone, imagery, and meter.
- Your line MUST be grounded in the provided CONTEXT: do not invent facts not supported there.
- Do NOT add numbering, quotes, code fences, or explanations.
- Max ~16 words.
"""


AGENT_B_SYSTEM = """You are Agent B, a complementary poetic voice. Output EXACTLY one line (no extra lines).
- You write EVEN-numbered lines (2,4,6,...), responding to Agent A.
- Maintain continuity (rhyme/imagery) and adhere to the same scene/time.
- Your line MUST be grounded in the provided CONTEXT: no invented facts.
- Do NOT add numbering, quotes, code fences, or explanations.
- Max ~16 words.
"""
JUDGE_SYSTEM = """You are a strict judge of two interleaved poetic voices (Agent A wrote odd lines, Agent B even).
Score the poem on:
1) Grounding (0-5): factual consistency with CONTEXT (no hallucinations).
2) Relevance (0-3): sticks to topic and context.
3) Continuity (0-3): lines reference each other coherently.
4) Poetic quality (0-3): imagery/meter/rhythm, absence of clichés.
5) Constraint adherence (0-3): exactly one line per turn, brevity (~16 words), no quotes/numbering.

Compute totals for A vs B across ONLY their own lines:
- For Grounding and Relevance, penalize any line that contradicts CONTEXT.
- For Continuity and Poetic quality, evaluate each agent’s contributions in aggregate.
- For Constraints, deduct for violations (extra lines, obvious verbosity, quotes/numbering).

Output JSON ONLY:
{"score_A": int, "score_B": int, "winner": "A"|"B"|"tie", "notes": "one short paragraph of rationale"}
"""

client = OpenAI(
    base_url=os.getenv("BASE_URL"),
    api_key=os.getenv("OPENAI_API_KEY"),
)
# Common free models on OpenRouter:
# "meta-llama/llama-3.2-3b-instruct:free"
# "qwen/qwen-2-7b-instruct:free"
# "mistralai/mistral-7b-instruct:free"
MODEL = os.getenv("MODEL", "meta-llama/llama-3.2-3b-instruct:free")

def sanitizer(text: str) -> str:
    """Keep first non-empty line; strip quotes/numbering."""
    first = next((ln for ln in text.splitlines() if ln.strip()), "")
    first = re.sub(r'^\s*["“”\'`]+|["“”\'`]+\s*$', '', first.strip())
    first = re.sub(r'^\s*\d+[\).\s-]*\s*', '', first)
    return first.strip()

def count_words(s: str) -> int:
    return len(re.findall(r"\b\w[\w'-]*\b", s))

async def _call_chat(system_prompt: str, user_prompt: str, temperature: float,
               max_tokens: int = 60,
               stops: Optional[List[str]] = None,
               retries: int = 2) -> str:
    
    """Single-line completion with retry. No newline stop (avoids empty output)."""

   # print(system_prompt)
   # print(user_prompt)

    last_err = None
    for attempt in range(retries + 1):
        try:
            resp = client.chat.completions.create(
                model=MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=temperature,
                max_tokens=max_tokens,
                stop=stops,   # keep as None unless you use a custom token
                seed=SEED,
            )
            text = resp.choices[0].message.content or ""
            print(f"API Response: {text}")
            line = sanitizer(text)
            if not line:
                # fallback: take first non-empty chunk raw
                line = next((ln for ln in text.splitlines() if ln.strip()), "").strip()
            if count_words(line) > 18:
                line = " ".join(line.split()[:16])
            return line or "(...)"
        except Exception as e:
            print(f"API Error on attempt {attempt + 1}: {e}")
            last_err = e
            time.sleep(0.3 * (attempt + 1))
    raise RuntimeError(f"model call failed: {last_err}")


@dataclass
class PoemResult:
    lines: List[str]
    by_agent: List[str]

async def generate_duet_poem(topic: str, lines: int, context_text: str) -> PoemResult:
    poem_lines: List[str] = []
    by_agent: List[str] = []
    context_block = "CONTEXT (authoritative facts; DO NOT CONTRADICT):\n" + context_text

    for i in range(1, lines + 1):
        is_A = (i % 2 == 1)
        system = AGENT_A_SYSTEM if is_A else AGENT_B_SYSTEM
        temp = TEMP_A if is_A else TEMP_B
        role = "A" if is_A else "B"

        prompt = (
            f"TOPIC: {topic}\n"
            f"{context_block}\n\n"
            "POEM SO FAR:\n" +
            ("\n".join(poem_lines) if poem_lines else "(none)") +
            f"\n\nWrite exactly ONE NEW LINE for line {i}."
        )

        line = await _call_chat(system, prompt, temperature=temp)
        poem_lines.append(line)
        by_agent.append(role)

    return PoemResult(lines=poem_lines, by_agent=by_agent)


def judge_poem(pr: PoemResult, context_text: str) -> dict:
    poem_text = "\n".join(pr.lines)
    judge_user = (
        "Evaluate this duet poem.\n\n"
        "POEM (odd=A, even=B):\n" + poem_text + "\n\n" +
        "CONTEXT (facts to ground against):\n" + context_text
    )
    resp = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": JUDGE_SYSTEM},
            {"role": "user", "content": judge_user},
        ],
        temperature=0.2,
        max_tokens=40,
        seed=SEED,
    )
    raw = resp.choices[0].message.content or "{}"
    m = re.search(r'\{.*\}', raw, re.S)
    data = {"score_A": 0, "score_B": 0, "winner": "tie", "notes": "no output"}
    if m:
        import json
        try:
            data = json.loads(m.group(0))
        except Exception:
            pass
    return data
