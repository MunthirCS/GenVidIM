import gradio as gr
import subprocess
import os
from pathlib import Path

# --- Configuration ---
MODEL_BASE_PATH = Path('/workspace/models')
OUTPUT_BASE_PATH = Path('/workspace/GenVidIM/outputs')
MODEL_CHOICES = [
    't2v-A14B',
    'i2v-A14B',
    'ti2v-5B',
    's2v-14B',
    'animate-14B'
]
DEFAULT_TASK = 'ti2v-5B'

# --- Gradio Interface ---
def generate_video(prompt, task, size, steps, use_prompt_extend, prompt_extend_method, prompt_extend_model, prompt_extend_target_lang):
    """
    Function to be called by the Gradio interface.
    """
    cmd = [
        'python', 'generate.py',
        '--task', task,
        '--size', size,
        '--sample_steps', str(steps),
        '--prompt', prompt,
        '--ckpt_dir', str(MODEL_BASE_PATH / f"Wan2.2-{task}"),
        '--offload_model', 'True',
        '--convert_model_dtype',
        '--t5_cpu'
    ]

    if use_prompt_extend:
        cmd.append('--use_prompt_extend')
        if prompt_extend_method:
            cmd.extend(['--prompt_extend_method', prompt_extend_method])
        if prompt_extend_model:
            cmd.extend(['--prompt_extend_model', prompt_extend_model])
        if prompt_extend_target_lang:
            cmd.extend(['--prompt_extend_target_lang', prompt_extend_target_lang])

    try:
        result = subprocess.run(
            cmd,
            cwd='/workspace/GenVidIM',
            capture_output=True,
            text=True,
            timeout=1200
        )

        if result.returncode != 0:
            return None, f"Error: {result.stderr}"

        video_files = sorted(OUTPUT_BASE_PATH.glob('*.mp4'), key=lambda p: p.stat().st_mtime, reverse=True)
        if not video_files:
            return None, "Error: No video file was generated."

        return str(video_files[0]), None

    except Exception as e:
        return None, f"Error: {e}"

with gr.Blocks() as demo:
    gr.Markdown("# Wan 2.2 Video Generation")
    
    with gr.Row():
        with gr.Column():
            prompt = gr.Textbox(label="Prompt")
            task = gr.Dropdown(choices=MODEL_CHOICES, value=DEFAULT_TASK, label="Model")
            size = gr.Textbox(label="Size", value="1280*704")
            steps = gr.Slider(minimum=1, maximum=100, value=35, label="Steps")
            
            with gr.Accordion("Prompt Extension", open=False):
                use_prompt_extend = gr.Checkbox(label="Use Prompt Extension")
                prompt_extend_method = gr.Dropdown(choices=["dashscope", "local_qwen"], label="Method")
                prompt_extend_model = gr.Textbox(label="Model")
                prompt_extend_target_lang = gr.Dropdown(choices=["zh", "en"], label="Target Language")

            generate_btn = gr.Button("Generate Video")

        with gr.Column():
            video_output = gr.Video(label="Generated Video")
            error_output = gr.Textbox(label="Error")

    generate_btn.click(
        fn=generate_video,
        inputs=[prompt, task, size, steps, use_prompt_extend, prompt_extend_method, prompt_extend_model, prompt_extend_target_lang],
        outputs=[video_output, error_output]
    )

if __name__ == "__main__":
    demo.launch()
