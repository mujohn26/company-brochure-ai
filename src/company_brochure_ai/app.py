"""Gradio web interface. Run with:  uv run python -m brochure_forge.app"""

import gradio as gr

from .brochure import stream_brochure
from .clients import MODELS


def build_app():
    return gr.Interface(
        fn=stream_brochure,
        title="🏭 Brochure Forge",
        description="Enter a company name and website, pick a model, and get a brochure in seconds.",
        inputs=[
            gr.Textbox(label="Company Name", info="Enter the company name"),
            gr.Textbox(label="Company Website", info="Must start with http:// or https://"),
            gr.Dropdown(list(MODELS), label="Select model", value="GPT"),
        ],
        outputs=[gr.Markdown(label="Brochure")],
        examples=[
            ["Andela", "https://www.andela.com", "GPT"],
            ["Hugging Face", "https://huggingface.co", "OLLAMA"],
        ],
        flagging_mode="never",
    )


def main():
    build_app().launch()


if __name__ == "__main__":
    main()