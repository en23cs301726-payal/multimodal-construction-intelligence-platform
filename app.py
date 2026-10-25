import json
import re
import requests
import streamlit as st
from PIL import Image
from io import BytesIO
from datetime import datetime

APP_NAME = "Multimodal Construction Intelligence Platform"
GEMINI_MODEL = "gemini-1.5-flash"
GEMINI_ENDPOINT = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"

st.set_page_config(page_title=APP_NAME, page_icon="🏗️", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
:root { --navy:#13233f; --blue:#2563eb; --red:#dc2626; --muted:#64748b; }
.block-container {padding-top:1.5rem; padding-bottom:2rem; max-width:1400px;}
.hero {padding:1.5rem 1.7rem;border-radius:18px;background:linear-gradient(120deg,#172554,#2563eb);color:white;margin-bottom:1rem}
.hero h1 {color:white;margin:0 0 .35rem 0;font-size:2rem}
.hero p {color:#e2e8f0;margin:0}
.small-muted {color:#64748b;font-size:.88rem}
.metric-card {padding:1rem;border:1px solid #e2e8f0;border-radius:14px;background:#fff}
.status {display:inline-block;padding:.25rem .65rem;border-radius:999px;font-weight:700;font-size:.8rem}
.status-good {background:#dcfce7;color:#166534}.status-warn {background:#fef3c7;color:#92400e}.status-bad {background:#fee2e2;color:#991b1b}
div[data-testid="stMetric"] {border:1px solid #e2e8f0;padding:14px;border-radius:12px;background:#fff}
</style>
""", unsafe_allow_html=True)

def parse_json_response(text):
    text = re.sub(r"^\s*```(?:json)?\s*|\s*```\s*$", "", text.strip(), flags=re.I)
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", text, flags=re.S)
        if match:
            return json.loads(match.group(0))
        raise ValueError("The AI response did not contain valid JSON.")

def gemini_generate(api_key, prompt, image=None, temperature=0.2):
    """Call Gemini REST API. Returns generated text or raises a useful error."""
    parts = [{"text": prompt}]
    if image is not None:
        image_bytes = image.getvalue()
        mime = image.type or "image/jpeg"
        import base64
        parts.insert(0, {"inline_data": {"mime_type": mime, "data": base64.b64encode(image_bytes).decode("utf-8")}})
    response = requests.post(
        GEMINI_ENDPOINT.format(model=GEMINI_MODEL),
        params={"key": api_key},
        json={"contents": [{"parts": parts}], "generationConfig": {"temperature": temperature, "responseMimeType": "application/json"}},
        timeout=90,
    )
    if response.status_code >= 400:
        try:
            detail = response.json().get("error", {}).get("message", response.text)
        except Exception:
            detail = response.text
        raise RuntimeError(f"Gemini API error ({response.status_code}): {detail}")
    payload = response.json()
    try:
        return payload["candidates"][0]["content"]["parts"][0]["text"]
    except (KeyError, IndexError, TypeError):
        raise RuntimeError("Gemini returned an empty or unexpected response.")

def analyze_or_demo(api_key, prompt, image, demo_result):
    if api_key:
        try:
            return parse_json_response(gemini_generate(api_key, prompt, image))
        except Exception as exc:
            st.warning(f"Live AI analysis failed; showing demonstration data instead. Details: {exc}")
    else:
        st.info("Demonstration mode is active. Add a Gemini API key in the sidebar for image-based AI analysis.")
    return demo_result

def download_json(data, filename):
    return st.download_button("⬇️ Download JSON report", json.dumps(data, indent=2, ensure_ascii=False), file_name=filename, mime="application/json")

def money_inr(value):
    if value >= 1e7:
        return f"₹{value/1e7:,.2f} Cr"
    if value >= 1e5:
        return f"₹{value/1e5:,.2f} L"
    return f"₹{value:,.0f}"

def show_json(data):
    st.json(data, expanded=True)

with st.sidebar:
    st.markdown("## 🏗️ Construction Intelligence")
    st.caption("Skill Wallet · Capstone Project 1")
    api_key = st.text_input("Google Gemini API key", type="password", help="Used only for requests made from this app session. Do not share your key or commit it to Git.")
    st.markdown("---")
    st.markdown("### Architecture")
    st.markdown("1. Photo / project inputs\n2. Gemini multimodal reasoning\n3. Validated JSON-style outputs\n4. Streamlit metrics & reports")
    st.markdown("---")
    st.markdown("### Modules")
    st.caption("• PPE safety audit\n• Crack diagnostics\n• Budget & valuation\n• Weather-aware assistant")
    st.markdown("---")
    st.caption("Prototype decision support only. Not a substitute for a qualified safety officer, structural engineer, quantity surveyor, or registered valuer.")

st.markdown(f"""<div class="hero"><h1>🏗️ {APP_NAME}</h1><p>AI-assisted site safety, crack triage, construction planning and real-estate decision support.</p></div>""", unsafe_allow_html=True)
st.warning("Safety and structural assessments are indicative. Never use a photo-only AI result to certify a site, diagnose structural safety, or authorize work. Follow applicable local codes and qualified professional advice.")

tab_safety, tab_cracks, tab_planning, tab_assistant = st.tabs([
    "🦺 Site Safety & PPE", "🧱 Crack Diagnostics", "📐 Planning & Valuation", "🌦️ Daily Site Assistant"
])

with tab_safety:
    st.subheader("Site Safety & PPE Audit")
    st.write("Upload a clear site image. The model should identify visible PPE and observable hazards; obscured items are marked unknown rather than assumed compliant.")
    safety_image = st.file_uploader("Construction site photo", type=["jpg", "jpeg", "png"], key="safety_image")
    if safety_image:
        st.image(safety_image, caption="Uploaded site image", use_container_width=True)
    if st.button("Run PPE safety audit", type="primary", key="run_safety"):
        demo = {
            "safety_score": 72,
            "overall_status": "Needs Improvement",
            "ppe_detection": {
                "helmets": {"status": "Partially visible", "compliant": False, "notes": "Verify every worker has a correctly fitted helmet."},
                "high_visibility_vests": {"status": "Partially visible", "compliant": False, "notes": "Ensure high-visibility clothing is worn in active work zones."},
                "steel_toe_boots": {"status": "Not verifiable from image", "compliant": None, "notes": "Inspect footwear at site level."},
                "safety_harnesses": {"status": "Not verifiable from image", "compliant": None, "notes": "Check harness use where fall protection is required."}
            },
            "hazards": [
                {"hazard": "Potential missing PPE", "severity": "High", "evidence": "Demonstration placeholder; verify against uploaded image.", "corrective_remedy": "Pause affected work and complete a supervisor-led PPE check."},
                {"hazard": "Unprotected edge / trip risk", "severity": "Medium", "evidence": "Demonstration placeholder; verify on site.", "corrective_remedy": "Inspect access routes and edges; install guarding and housekeeping controls as required."}
            ],
            "limitations": "Demonstration data only; no image inference was performed."
        }
        prompt = """You are an occupational construction safety assistant. Inspect the attached image only for visible evidence. Return JSON only with keys: safety_score (integer 0-100), overall_status (Compliant / Needs Improvement / Unsafe / Insufficient Visual Evidence), ppe_detection (object with helmets, high_visibility_vests, steel_toe_boots, safety_harnesses; each has status, compliant (true/false/null), notes), hazards (array of objects with hazard, severity (Low/Medium/High/Critical), evidence, corrective_remedy), limitations (string). Do not claim OSHA or Indian code compliance can be certified from a photo. Distinguish not visible from absent. Mention relevant OSHA principles and applicable Indian site rules cautiously; IS 456 is a concrete code, not a PPE standard. Prioritize imminent danger. Be conservative and factual."""
        if not safety_image:
            st.error("Upload a JPG or PNG image first.")
        else:
            result = analyze_or_demo(api_key, prompt, safety_image, demo)
            st.session_state["safety_result"] = result
    result = st.session_state.get("safety_result")
    if result:
        score = max(0, min(100, int(result.get("safety_score", 0))))
        c1, c2, c3 = st.columns(3)
        c1.metric("Safety score", f"{score}/100")
        c2.metric("Overall status", str(result.get("overall_status", "Unknown")))
        c3.metric("Hazards identified", len(result.get("hazards", [])))
        st.progress(score / 100)
        st.markdown("#### PPE checklist")
        ppe = result.get("ppe_detection", {})
        if isinstance(ppe, dict):
            for item, detail in ppe.items():
                with st.expander(item.replace("_", " ").title()):
                    st.write(detail if isinstance(detail, str) else detail.get("status", "Unknown"))
                    if isinstance(detail, dict):
                        st.caption(detail.get("notes", ""))
                        st.write("Compliant:", detail.get("compliant", "Unknown"))
        st.markdown("#### Site hazards & corrective actions")
        for hazard in result.get("hazards", []):
            sev = hazard.get("severity", "Unknown")
            st.markdown(f"**{hazard.get('hazard','Hazard')}** · `{sev}`")
            st.write(hazard.get("evidence", ""))
            st.write("**Corrective action:** " + hazard.get("corrective_remedy", ""))
        download_json(result, "site_safety_audit.json")
        with st.expander("Raw structured output"):
            show_json(result)

with tab_cracks:
    st.subheader("Crack Diagnostics & Structural Integrity")
    st.write("Upload a close-up image with a scale reference where possible. Image-only crack-width estimates are uncertain.")
    crack_image = st.file_uploader("Concrete or wall surface photo", type=["jpg", "jpeg", "png"], key="crack_image")
    if crack_image:
        st.image(crack_image, caption="Uploaded surface image", use_container_width=True)
    if st.button("Analyze crack / defect", type="primary", key="run_crack"):
        demo = {
            "defect_type": "Hairline",
            "estimated_crack_width_mm": None,
            "width_confidence": "Low without a scale reference",
            "severity": "Needs professional review",
            "possible_root_causes": ["Shrinkage or temperature movement (not confirmed)"],
            "recommended_actions": ["Photograph with a crack-width gauge and record location/date.", "Ask a qualified engineer to inspect if the crack is growing, leaking, diagonal, or accompanied by deformation."],
            "repair_options_for_engineer_review": ["Do not select epoxy injection or grouting until the cause and activity are established."],
            "urgency": "Routine inspection unless active movement or distress is present",
            "limitations": "Demonstration data only; no image inference was performed."
        }
        prompt = """Act as a cautious construction defect triage assistant, not a structural certifier. Inspect the attached concrete/wall image. Return JSON only with keys: defect_type (one of Hairline, Settlement, Structural Shear, Thermal Expansion, Spalling, Other/Unclear), estimated_crack_width_mm (number or null; do not invent precision without scale), width_confidence, severity, possible_root_causes (array), recommended_actions (array), repair_options_for_engineer_review (array; options may include epoxy injection or structural re-grouting only where appropriate and explicitly conditional), urgency, limitations. Distinguish observations from hypotheses. State that photo-only classification cannot establish structural safety. If there are signs of major movement, exposed reinforcement, falling concrete, or rapidly widening cracks, recommend restricting access and urgent qualified engineer inspection."""
        if not crack_image:
            st.error("Upload a JPG or PNG image first.")
        else:
            st.session_state["crack_result"] = analyze_or_demo(api_key, prompt, crack_image, demo)
    crack_result = st.session_state.get("crack_result")
    if crack_result:
        a, b = st.columns(2)
        a.metric("Defect classification", crack_result.get("defect_type", "Unclear"))
        b.metric("Estimated width", (str(crack_result.get("estimated_crack_width_mm")) + " mm") if crack_result.get("estimated_crack_width_mm") is not None else "Not estimated")
        st.markdown(f"**Urgency:** {crack_result.get('urgency', 'Not specified')}")
        st.markdown("#### Possible causes")
        for cause in crack_result.get("possible_root_causes", []):
            st.write("• " + str(cause))
        st.markdown("#### Recommended actions")
        for action in crack_result.get("recommended_actions", []):
            st.write("• " + str(action))
        st.markdown("#### Repair options for engineer review")
        for action in crack_result.get("repair_options_for_engineer_review", []):
            st.write("• " + str(action))
        st.caption(crack_result.get("limitations", ""))
        download_json(crack_result, "crack_diagnostics.json")
        with st.expander("Raw structured output"):
            show_json(crack_result)

with tab_planning:
    st.subheader("Project Planning & Real Estate Valuation")
    left, right = st.columns(2)
    with left:
        structure = st.selectbox("Structure type", ["Residential apartment", "Independent house", "Commercial building", "Warehouse / industrial", "Institutional"])
        sqft = st.number_input("Built-up area (sq ft)", min_value=100, max_value=2_000_000, value=2500, step=100)
        tier = st.selectbox("Location tier", ["Tier 1", "Tier 2", "Tier 3"])
        completion = st.slider("Physical completion", 0, 100, 35, 5)
    with right:
        city = st.text_input("City / locality (optional)", placeholder="e.g., Indore, Madhya Pradesh")
        finish = st.selectbox("Finish / specification", ["Economy", "Standard", "Premium"], index=1)
        include_render = st.checkbox("Generate conceptual 3D render prompt", value=True)
    rates = {
        "Residential apartment": {"Tier 1": 2600, "Tier 2": 2100, "Tier 3": 1750},
        "Independent house": {"Tier 1": 2900, "Tier 2": 2300, "Tier 3": 1850},
        "Commercial building": {"Tier 1": 3400, "Tier 2": 2700, "Tier 3": 2200},
        "Warehouse / industrial": {"Tier 1": 1900, "Tier 2": 1550, "Tier 3": 1300},
        "Institutional": {"Tier 1": 3100, "Tier 2": 2500, "Tier 3": 2050}
    }
    multiplier = {"Economy": 0.85, "Standard": 1.0, "Premium": 1.35}[finish]
    base_rate = rates[structure][tier] * multiplier
    budget = sqft * base_rate
    # Broad thumb rules only; actual quantity requires drawings, specs and BOQ.
    steel_kg = sqft * (3.5 if structure == "Warehouse / industrial" else 4.0 if structure == "Independent house" else 4.5)
    cement_bags = sqft * (0.35 if structure == "Warehouse / industrial" else 0.40 if structure == "Independent house" else 0.45)
    valuation_rate = {"Tier 1": 8500, "Tier 2": 6000, "Tier 3": 4200}[tier]
    if structure == "Warehouse / industrial":
        valuation_rate *= 0.78
    elif structure == "Commercial building":
        valuation_rate *= 1.25
    asset_value = sqft * valuation_rate
    incurred = budget * completion / 100
    c1, c2, c3 = st.columns(3)
    c1.metric("Indicative project budget", money_inr(budget))
    c2.metric("CapEx incurred at completion", money_inr(incurred))
    c3.metric("Indicative market value", money_inr(asset_value))
    c4, c5, c6 = st.columns(3)
    c4.metric("Steel thumb-rule", f"{steel_kg/1000:,.1f} tonnes")
    c5.metric("Cement thumb-rule", f"{cement_bags:,.0f} bags")
    c6.metric("Completion milestone", f"{completion}%")
    st.progress(completion / 100)
    st.caption(f"Modelled location: {city.strip() or tier}. Construction rate used: ₹{base_rate:,.0f}/sq ft. Market rate used: ₹{valuation_rate:,.0f}/sq ft.")
    st.warning("All figures are rough planning assumptions, not a BOQ, contractor quote, bank valuation, or registered valuation. Rates vary substantially by city, soil, design, floor count, materials, taxes, approvals and date. Validate with local professionals.")
    estimate = {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "structure_type": structure, "built_up_sqft": sqft, "location_tier": tier, "city_or_locality": city,
        "finish": finish, "completion_percent": completion, "assumed_construction_rate_inr_per_sqft": round(base_rate),
        "indicative_project_budget_inr": round(budget), "estimated_capex_incurred_inr": round(incurred),
        "assumed_market_rate_inr_per_sqft": round(valuation_rate), "indicative_market_asset_value_inr": round(asset_value),
        "steel_estimate_kg": round(steel_kg), "cement_estimate_bags": round(cement_bags),
        "methodology_note": "Illustrative thumb rules only; confirm with local BOQ, drawings, quotations and a qualified valuer."
    }
    download_json(estimate, "project_planning_estimate.json")
    if include_render:
        render_prompt = f"Photorealistic conceptual architectural visualization of a {finish.lower()} {structure.lower()}, approximately {sqft:,} square feet, in {city.strip() or tier + ' Indian city'}, climate-appropriate design, realistic Indian construction context, professional architectural visualization, daylight, human-scale landscaping, no text, no logos. Concept only; not a construction drawing."
        st.markdown("#### Conceptual 3D render prompt")
        st.text_area("Copy this prompt into your preferred image-generation service", value=render_prompt, height=120)
        st.caption("This app generates a prompt only; it does not call Pollinations or produce a render automatically.")

with tab_assistant:
    st.subheader("Daily Site Assistant & Weather-Aware Advisory")
    weather = st.selectbox("Current / forecast weather", ["Normal", "High Wind", "Heavy Rain", "Extreme Heat"])
    advisory = {
        "Normal": ("Routine controls", "Continue only after the competent person confirms site controls, equipment checks, access routes and weather conditions are suitable."),
        "High Wind": ("Wind / lifting risk", "Pause crane and hoisting work when manufacturer limits or site lift plans require it. Secure loose materials, scaffolds and temporary works; reassess before restart."),
        "Heavy Rain": ("Rain / electrical / ground risk", "Inspect drainage, excavations, access and ground stability. Protect electrical equipment from water; isolate unsafe circuits through authorized personnel. Reassess concrete placement and curing with the engineer."),
        "Extreme Heat": ("Heat stress", "Provide drinking water, shade, rest breaks and acclimatization; schedule heavy work for cooler periods. Monitor workers for heat illness and follow the site's emergency response procedure.")
    }
    title, message = advisory[weather]
    st.markdown(f"### {title}")
    st.info(message)
    st.caption("Use site-specific method statements, equipment manuals and local weather warnings. The selector is a checklist aid, not a live weather feed.")
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    for item in st.session_state.chat_history:
        with st.chat_message(item["role"]):
            st.markdown(item["content"])
    user_question = st.chat_input("Ask about site planning, safety controls, materials, or construction processes…")
    if user_question:
        st.session_state.chat_history.append({"role": "user", "content": user_question})
        with st.chat_message("user"):
            st.markdown(user_question)
        context = "\n".join([f'{m["role"]}: {m["content"]}' for m in st.session_state.chat_history[-10:]])
        assistant_prompt = f"""You are a cautious construction project assistant. Provide concise, practical guidance and clearly flag when a qualified engineer, safety officer, licensed electrician, or registered valuer is needed. Never certify structural safety or legal compliance. Current selected weather: {weather}. Weather advisory: {message}. Conversation so far:\n{context}\nRespond with helpful plain text. Mention assumptions and safety-critical limitations."""
        if api_key:
            try:
                answer = gemini_generate(api_key, assistant_prompt, None)
                answer = parse_json_response(answer) if answer.strip().startswith("{") else answer
                if isinstance(answer, dict):
                    answer = answer.get("answer") or answer.get("response") or json.dumps(answer, indent=2)
            except Exception as exc:
                answer = f"Demo assistant (AI request failed: {exc}). For this {weather.lower()} condition, follow the site safety plan and consult the responsible professional. Please clarify the structure, activity, location and applicable constraints for more specific general guidance."
        else:
            answer = f"Demonstration assistant: For your question — “{user_question}” — first follow the approved method statement, site risk assessment and applicable local requirements. Current weather note: {message} For structural, lifting, electrical or emergency decisions, consult the responsible qualified professional. Add a Gemini API key for AI-generated responses."
        st.session_state.chat_history.append({"role": "assistant", "content": answer})
        with st.chat_message("assistant"):
            st.markdown(answer)
    if st.button("Clear conversation"):
        st.session_state.chat_history = []
        st.rerun()

st.markdown("---")
st.markdown('<p class="small-muted">Prototype build · No external database · Reports are generated in-session · Always validate AI output before operational use.</p>', unsafe_allow_html=True)
