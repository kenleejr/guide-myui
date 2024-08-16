from fasthtml import FastHTML
from fasthtml.fastapp import *
from fasthtml.common import *
from fasthtml.components import Zero_md
from starlette.requests import Request
from vertexai.generative_models import GenerativeModel, GenerationConfig
from vertexai.generative_models import HarmCategory, HarmBlockThreshold
import asyncio


import logging
logging.basicConfig(encoding='utf-8', level=logging.INFO)  # Set the desired logging level
logger = logging.getLogger(__name__)

# Setting up FastHTML
tlink = Script(src="https://cdn.tailwindcss.com")
plotlylink = Script(src="https://cdn.plot.ly/plotly-2.34.0.min.js")
dlink = Link(rel="stylesheet", href="https://cdn.jsdelivr.net/npm/daisyui@4.11.1/dist/full.min.css")
zeromd_header = Script(type="module", src="https://cdn.jsdelivr.net/npm/zero-md@3?register")


model = GenerativeModel(model_name="gemini-1.5-pro",
                                 system_instruction="You are an expert UI designer with experience in HTML and CSS.",
                                 generation_config=GenerationConfig(temperature=0.2,
                                                                    max_output_tokens=8192),
                                 safety_settings={
                                    HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
                                    HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
                                    HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
                                    HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
                                 }
)


app = FastHTML(hdrs=(tlink, plotlylink, dlink, zeromd_header), 
               ftrs=(),
               ws_hdr=True)


@app.get("/")
def home(request: Request):
    return Div(
                Div(Span(id="loading",
                         cls='loading loading-bars loading-lg htmx-indicator'),
                    id="generated_html",
                    cls='flex-grow justify-center'
                ),
                Form(
                    Group(
                        Button('Send', cls='btn btn-primary'),
                        Textarea(id="prompt", placeholder='Type your message...', cls='textarea textarea-bordered flex-grow mr-2'),
                        cls='flex flex-row gap-2'
                    ),
                    hx_post="/generate_ui",
                    hx_include="this",
                    hx_target="#generated_html",
                    hx_swap="outerHTML",
                    hx_indicator="#loading",
                    cls='bg-base-300 p-4'
                ),
                cls="h-screen flex flex-col"
            )

@app.post("/generate_ui")
async def generate_ui(request: Request):
    form_data = await request.form()
    logger.info(form_data)
    prompt = form_data.get("prompt")
    user_prompt = f"""Your task is to generate raw HTML and CSS according to the specifications given in this prompt: {prompt}. 
    Do not generate a fully body of HTML, only a partial that can be swapped into an existing HTML document.
    You have at your disposal tailwind utility classes, daisyui classes, and vanilla css and javascript to be included inline in the HTML you return.
    Do NOT respond with separate css and js files, just respond with the HTML only."""
    generated_ui = await model.generate_content_async(contents=user_prompt)
    generated_ui_text = generated_ui.text[7:-3]
    return Div(
            NotStr(generated_ui_text),
            id="generated_html"
    )


if __name__ == '__main__': uvicorn.run("main:app", host='0.0.0.0', port=8000, reload=False)

