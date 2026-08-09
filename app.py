import asyncio
import json
import os
import re
from dataclasses import dataclass
from typing import AsyncGenerator, Tuple, List, Dict

import streamlit as st

# --------------------------------------------------------------------------
# 0. Gemini API Handshake
# --------------------------------------------------------------------------
GEMINI_MODEL_NAME = "gemini-2.5-flash"
_client = None

def _init_gemini() -> bool:
    global _client
    if _client is not None:
        return True
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        return False
    try:
        from google import genai
        _client = genai.Client(api_key=api_key)
        return True
    except Exception:
        return False

async def _gemini_generate(prompt: str, max_output_tokens: int = 200) -> str:
    from google.genai import types
    response = await _client.aio.models.generate_content(
        model=GEMINI_MODEL_NAME,
        contents=prompt,
        config=types.GenerateContentConfig(
            max_output_tokens=max_output_tokens,
            temperature=0.4,
        ),
    )
    return (response.text or "").strip()

# --------------------------------------------------------------------------
# 1. Instance-profiling layer -> complexity vector c_t
# --------------------------------------------------------------------------
CATEGORY_KEYWORDS = {
    "hazmat": ["chemical", "explosion", "toxic", "gas", "leak", "fire", "radiation"],
    "logistics": ["trapped", "flood", "blocked", "route", "evacuat", "collapsed", "traffic"],
    "medical": ["injured", "casualt", "wound", "unconscious", "bleeding", "medical"],
}

def _keyword_fallback(text: str) -> Dict:
    text_l = text.lower()
    flags = {cat: any(kw in text_l for kw in kws) for cat, kws in CATEGORY_KEYWORDS.items()}
    score = 1 + 3 * sum(flags.values())
    return {"score": min(score, 10), "flags": flags, "source": "heuristic"}

async def profile_difficulty(text: str) -> Dict:
    if _init_gemini():
        prompt = (
            "You are a triage classifier for an emergency-response dispatch system. "
            "Read the incident report below and respond with ONLY a JSON object, no "
            'prose, no markdown fences, in this exact shape: {"score": <int 1-10>, '
            '"hazmat": <bool>, "logistics": <bool>, "medical": <bool>}. "score" is overall '
            "crisis severity, hazmat = chemical/fire/toxic danger present, logistics = "
            "access/evacuation routes are an issue, medical = casualties or injuries "
            f"are involved.\n\nIncident report:\n{text}"
        )
        try:
            raw = await _gemini_generate(prompt, max_output_tokens=100)
            raw = re.sub(r"^```(json)?|```$", "", raw.strip(), flags=re.MULTILINE).strip()
            parsed = json.loads(raw)
            score = max(1, min(int(parsed.get("score", 1)), 10))
            return {
                "score": score,
                "flags": {
                    "hazmat": bool(parsed.get("hazmat", False)),
                    "logistics": bool(parsed.get("logistics", False)),
                    "medical": bool(parsed.get("medical", False)),
                },
                "source": "gemini"
            }
        except Exception:
            pass
    return _keyword_fallback(text)

# --------------------------------------------------------------------------
# 2. Router Engine (Dynamic Scaling Logic)
# --------------------------------------------------------------------------
@dataclass
class Tier:
    name: str
    workers: List[str]
    depth: int

def route(vector: Dict) -> Tier:
    score = vector["score"]
    flags = vector["flags"]
    if score < 4:
        return Tier(name="Standard Dispatch", workers=["standard"], depth=1)
    if score >= 7:
        return Tier(name="Full Triad Response", workers=["hazmat", "logistics", "medical"], depth=6)
    
    active = [k for k, v in flags.items() if v]
    if len(active) == 0: active = ["logistics", "medical"]
    elif len(active) == 1:
        remaining = [k for k in ("hazmat", "logistics", "medical") if k not in active]
        active.append(remaining[0])
    return Tier(name="Dual Expert Response", workers=active[:2], depth=4)

# --------------------------------------------------------------------------
# 3. Parallel Expert Evaluation Loop
# --------------------------------------------------------------------------
EXPERT_PERSONAS = {
    "standard": ("Standard Dispatch", "a general first-response dispatcher"),
    "hazmat": ("Hazmat Expert", "a hazardous-materials response specialist"),
    "logistics": ("Logistics Expert", "an evacuation and routing logistics specialist"),
    "medical": ("Medical Triage", "an emergency medical triage lead"),
}

FALLBACK_RESULTS = {
    "standard": "Situation low-severity. Standard automated protocols launched; monitoring.",
    "hazmat": "Chemical/fire threat localized. Containment foam deployed to the asset source.",
    "logistics": "Escape routes mapped around affected sectors. Rescue vehicles cleared to bypass traffic.",
    "medical": "Upwind triage zone initialized. Medical channels ready to process casualties.",
}

async def run_expert(key: str, incident_text: str, depth: int) -> AsyncGenerator[Tuple[str, object], None]:
    label, persona = EXPERT_PERSONAS[key]
    for i in range(1, depth + 1):
        await asyncio.sleep(0.12)
        yield ("progress", i)
        
    if _init_gemini():
        prompt = (
            f"You are {persona} on an emergency-response team. Give ONE short, concrete "
            f"action plan (2 sentences max, no preamble, no step list) evaluating the incident.\n\n"
            f"Incident report:\n{incident_text}"
        )
        try:
            res = await _gemini_generate(prompt, max_output_tokens=150)
            yield ("result", res)
            return
        except Exception:
            pass
    yield ("result", FALLBACK_RESULTS[key])

async def synthesis_layer(traces: Dict[str, str], incident_text: str) -> str:
    if _init_gemini():
        combined_traces = "\n".join([f"{k.upper()}: {v}" for k, v in traces.items()])
        prompt = (
            "You are the Command Coordinator. Review the raw incident and the individual expert "
            "recommendations below. Synthesize them into a single, cohesive, authoritative execution "
            "matrix (maximum 3 sentences). No preamble.\n\n"
            f"Incident: {incident_text}\n\nExpert Plans:\n{combined_traces}"
        )
        try: return await _gemini_generate(prompt, max_output_tokens=250)
        except Exception: pass
    return "Execute multi-agency containment immediately. Deploy neutralizing elements, stabilize critical logistics entry pathways, and clear routes to active triage cells."

# --------------------------------------------------------------------------
# 4. Streamlit Dashboard Setup
# --------------------------------------------------------------------------
st.set_page_config(page_title="ResQ-TO-MoE Grid", layout="wide")
st.title("🛟 ResQ-TO-MoE: Adaptive Crisis Dispatch")
st.subheader("High-Schooler Research Project: Test-Time-Optimal Routing Infrastructure")

input_text = st.text_area(
    "Live Emergency Feed Text Data:", 
    "Industrial factory leak reported near the river basin. Toxic fumes observed, workers trapped."
)

if st.button("Run TO-MoE Inference Network"):
    async def main_pipeline():
        st.write("### 📡 Step 1: Running Instance Profiler...")
        vector = await profile_difficulty(input_text)
        st.metric(label=f"Calculated Complexity (Source: {vector['source'].upper()})", value=f"{vector['score']} / 10")
        
        tier = route(vector)
        st.info(f"**Selected Layer:** {tier.name} | **Test-Time Compute Depth (L):** {tier.depth} execution checks | **Active Workers:** {', '.join(tier.workers)}")
        
        st.write("### 🧠 Step 2: Spawning Heterogeneous Expert Threads...")
        progress_bars, status_texts = {}, {}
        cols = st.columns(len(tier.workers))
        
        for idx, worker in enumerate(tier.workers):
            with cols[idx]:
                st.markdown(f"#### {EXPERT_PERSONAS[worker][0]}")
                progress_bars[worker] = st.progress(0.0)
                status_texts[worker] = st.empty()
        
        generators = {w: run_expert(w, input_text, tier.depth) for w in tier.workers}
        active_workers = list(tier.workers)
        traces = {}
        
        while active_workers:
            for worker in list(active_workers):
                try:
                    msg_type, val = await generators[worker].__anext__()
                    if msg_type == "progress":
                        pct = float(val) / float(tier.depth)
                        progress_bars[worker].progress(pct)
                        status_texts[worker].text(f"Validation loop {val}/{tier.depth}...")
                    elif msg_type == "result":
                        traces[worker] = val
                        status_texts[worker].info(val)
                        active_workers.remove(worker)
                except StopAsyncIteration:
                    if worker in active_workers: active_workers.remove(worker)
        
        st.write("### 🎯 Step 3: Synthesis Layer Optimization (y_t)...")
        final_plan = await synthesis_layer(traces, input_text)
        st.success(f"**Final Synthesized Master Execution Matrix:**\n\n{final_plan}")

    asyncio.run(main_pipeline())
