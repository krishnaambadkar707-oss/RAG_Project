import time
from typing import List, Tuple
from app.config import settings
from app.db.schemas import Citation

SYSTEM_GROUNDING_PROMPT = """You are a helpful Enterprise Knowledge Assistant. Your job is to answer employee questions in a simple, easy-to-understand way using ONLY the provided document context.

🎯 KEY INSTRUCTIONS:
1. Use SIMPLE, EVERYDAY LANGUAGE - avoid jargon and technical terms
2. Keep answers SHORT and CLEAR - use bullet points for lists
3. Answer ONLY from the provided documents - do NOT make up information
4. Format nicely:
   - Use bullet points (•) for lists
   - Use clear sections with headers
   - Make it easy to scan and read
5. If you can't find the answer in documents, say: "I couldn't find this answer in our documents"
6. Always mention which document and page you got the info from

✅ EXAMPLE GOOD ANSWER:
"According to HR Policy (Page 2):
• Full-time employees get 20 days of annual leave
• You can carry over 5 unused days to next year
• Request leave on our intranet"

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
        fallback_msg = "I couldn't find an answer to your question in the available documents. Try asking in a different way or upload the relevant documents first."
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

    # Default / Local Grounded Answer Generator - Simple & User-Friendly
    if not answer:
        top_citation = citations[0]
        
        def clean_snippet(text, max_length=300):
            """Clean snippet to make it readable and user-friendly"""
            text = text.strip()
            # Remove extra whitespace
            text = ' '.join(text.split())
            # Keep first sentences only
            sentences = text.split('.')
            clean_sentences = [s.strip() for s in sentences if len(s.strip()) > 5]
            result = '. '.join(clean_sentences[:2])
            if len(result) > max_length:
                result = result[:max_length] + "..."
            return result
        
        if is_summary_query:
            # Summary format: Clean bullet points
            answer = f"📋 **Overview of {top_citation.filename}**\n\n"
            summary_points = []
            seen_sections = set()
            
            for c in citations:
                if c.section_title not in seen_sections and len(summary_points) < 5:
                    seen_sections.add(c.section_title)
                    clean_text = clean_snippet(c.snippet, 180)
                    summary_points.append(f"• **{c.section_title}:** {clean_text}")
            
            if summary_points:
                answer += "\n".join(summary_points)
            else:
                answer += clean_snippet(citations[0].snippet)
                
            answer += f"\n\n📄 Source: **{top_citation.filename}** (Page {top_citation.page_number})"
        else:
            # Q&A format: Direct, simple answer
            clean_text = clean_snippet(top_citation.snippet, 350)
            answer = f"{clean_text}"
            
            # Add more context if available from other sources
            additional_info = []
            for c in citations[1:3]:
                if c.section_title != top_citation.section_title:
                    snippet = clean_snippet(c.snippet, 150)
                    additional_info.append(f"• Also in **{c.section_title}** (Page {c.page_number}): {snippet}")
            
            if additional_info:
                answer += "\n\n**More Information:**\n" + "\n".join(additional_info)
            
            answer += f"\n\n📄 From **{top_citation.filename}** • Page {top_citation.page_number} • Section: *{top_citation.section_title}*"

    latency_ms = round((time.time() - start_time) * 1000, 2)
    return answer, citations, latency_ms
