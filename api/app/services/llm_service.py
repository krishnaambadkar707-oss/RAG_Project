import time
from typing import List, Tuple
from app.config import settings
from app.db.schemas import Citation

SYSTEM_GROUNDING_PROMPT = """You are an Enterprise Knowledge Assistant. Your job is to answer employee questions strictly and accurately based ONLY on the provided document context below.

CRITICAL INSTRUCTIONS:
1. Ground your answer completely in the provided context.
2. If the answer cannot be found in or directly inferred from the provided context, clearly state: "I don't have enough context in the provided documents to answer this question."
3. Do NOT invent policies, dates, passwords, or technical steps not present in the text.
4. Cite your sources in the text where relevant using the format: [Document Name, Page X, Section Y].
5. Keep your tone professional, concise, and helpful.

PROVIDED CONTEXT:
{context_text}
"""

def generate_grounded_answer(query: str, citations: List[Citation]) -> Tuple[str, List[Citation], float]:
    start_time = time.time()

    query_lower = query.lower().strip()
    summary_keywords = ["summary", "summarize", "overview", "tell me the summary", "tell me about", "explain", "details", "what is this", "what is it"]
    is_summary_query = any(k in query_lower for k in summary_keywords)

    # Adapted threshold: summary requests or scoped queries use a lower threshold (0.05) since broad questions have lower direct vector overlap
    min_threshold = 0.05 if (is_summary_query or len(citations) > 0) else 0.15

    # Fallback check: if no citations or maximum similarity is below threshold
    if not citations or max((c.similarity_score for c in citations), default=0.0) < min_threshold:
        fallback_msg = "I don't have enough context in the provided documents to answer this question. Please upload relevant documentation or adjust your collection filter."
        latency = round((time.time() - start_time) * 1000, 2)
        return fallback_msg, [], latency

    # Format context string with metadata
    context_blocks = []
    for i, c in enumerate(citations):
        block = f"--- Source [{i+1}]: Document '{c.filename}', Page {c.page_number}, Section '{c.section_title}' ---\n{c.snippet}"
        context_blocks.append(block)
    
    context_text = "\n\n".join(context_blocks)
    prompt = SYSTEM_GROUNDING_PROMPT.format(context_text=context_text) + f"\nUSER QUESTION: {query}\nANSWER:"

    provider = settings.LLM_PROVIDER.lower()
    answer = ""

    if provider == "openai" and settings.OPENAI_API_KEY:
        try:
            from openai import OpenAI
            client = OpenAI(api_key=settings.OPENAI_API_KEY)
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": SYSTEM_GROUNDING_PROMPT.format(context_text=context_text)},
                    {"role": "user", "content": query}
                ],
                temperature=0.1,
                max_tokens=600
            )
            answer = response.choices[0].message.content.strip()
        except Exception as e:
            print(f"[LLM] OpenAI call failed: {e}")

    elif provider == "gemini" and settings.GEMINI_API_KEY:
        try:
            import google.generativeai as genai
            genai.configure(api_key=settings.GEMINI_API_KEY)
            model = genai.GenerativeModel('gemini-1.5-flash')
            res = model.generate_content(prompt)
            answer = res.text.strip()
        except Exception as e:
            print(f"[LLM] Gemini call failed: {e}")

    # Default / Local Capstone Grounded Answer Generator
    if not answer:
        top_citation = citations[0]
        if is_summary_query:
            answer = f"### Executive Summary of **{top_citation.filename}**\n\n"
            summary_points = []
            seen_sections = set()
            for c in citations:
                if c.section_title not in seen_sections:
                    seen_sections.add(c.section_title)
                    summary_points.append(f"• **Section '{c.section_title}'** (Page {c.page_number}): {c.snippet[:240].strip()}...")
                elif len(summary_points) < 4:
                    summary_points.append(f"• **Page {c.page_number}**: {c.snippet[:200].strip()}...")
            
            if summary_points:
                answer += "\n\n".join(summary_points)
            else:
                answer += citations[0].snippet[:500]
                
            answer += f"\n\n*(Source: {top_citation.filename}, Total Grounded Sources: {len(citations)})*"
        else:
            snippets_text = " ".join([c.snippet for c in citations[:3]])
            answer = f"Based on **{top_citation.filename}** (Page {top_citation.page_number}, Section *'{top_citation.section_title}'*):\n\n"
            lines = [l.strip() for l in snippets_text.split(".") if len(l.strip()) > 15]
            if lines:
                answer += ". ".join(lines[:3]) + "."
            else:
                answer += snippets_text[:400] + "..."
            answer += f"\n\n*(Source: {top_citation.filename}, Page {top_citation.page_number})*"

    latency_ms = round((time.time() - start_time) * 1000, 2)
    return answer, citations, latency_ms
