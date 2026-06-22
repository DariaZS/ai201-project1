"""
app.py
Gradio web interface for The Unofficial Columbia Guide RAG system.
Run with: python app.py
Then open: http://localhost:7860
"""

import gradio as gr
from generator import ask

from retriever import embed_and_store

# Ensure vector store is populated on startup
embed_and_store()


def handle_query(question: str):
    """Takes a question, returns (answer, sources) for Gradio outputs."""
    if not question.strip():
        return "Please enter a question.", ""

    result = ask(question)
    sources = "\n".join(f"• {s}" for s in result["sources"])
    return result["answer"], sources


with gr.Blocks(title="The Unofficial Columbia Guide") as demo:
    gr.Markdown("# 🦁 The Unofficial Columbia Guide")
    gr.Markdown(
        "Ask questions about Columbia student life — CS requirements, "
        "housing lottery, dining halls, disability accommodations, and more. "
        "Answers are grounded in real student documents and official sources."
    )

    with gr.Row():
        inp = gr.Textbox(
            label="Your question",
            placeholder="e.g. How does the housing lottery work?",
            lines=2,
        )

    btn = gr.Button("Ask", variant="primary")

    with gr.Row():
        answer = gr.Textbox(label="Answer", lines=10)
        sources = gr.Textbox(label="Retrieved from", lines=4)

    btn.click(handle_query, inputs=inp, outputs=[answer, sources])
    inp.submit(handle_query, inputs=inp, outputs=[answer, sources])

    gr.Markdown(
        "_Answers are based only on collected documents. "
        "Always verify important information with official Columbia sources._"
    )

demo.launch()