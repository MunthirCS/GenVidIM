import os

# Base directory of the project
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# --- Model Configurations ---
# Default model paths
MODEL_DIR = os.path.join(BASE_DIR, 'models')
T2V_A14B_CKPT_DIR = os.path.join(MODEL_DIR, 'Wan2.2-T2V-A14B')
I2V_A14B_CKPT_DIR = os.path.join(MODEL_DIR, 'Wan2.2-I2V-A14B')
TI2V_5B_CKPT_DIR = os.path.join(MODEL_DIR, 'Wan2.2-TI2V-5B')
S2V_14B_CKPT_DIR = os.path.join(MODEL_DIR, 'Wan2.2-S2V-14B')
ANIMATE_14B_CKPT_DIR = os.path.join(MODEL_DIR, 'Wan2.2-Animate-14B')

# --- Generation Settings ---
DEFAULT_VIDEO_SIZE = '1280*720'
DEFAULT_OFFLOAD_MODEL = True
DEFAULT_CONVERT_MODEL_DTYPE = True
DEFAULT_T5_CPU = True

# --- Prompt Extension Settings ---
# Dashscope API
DASH_API_KEY = os.environ.get('DASH_API_KEY')
DASH_API_URL = os.environ.get('DASH_API_URL', 'https://dashscope.aliyuncs.com/api/v1')
DEFAULT_PROMPT_EXTEND_METHOD = 'dashscope'
DEFAULT_PROMPT_EXTEND_MODEL_T2V = 'qwen-plus'
DEFAULT_PROMPT_EXTEND_MODEL_I2V = 'qwen-vl-max'

# Local Qwen model
DEFAULT_LOCAL_QWEN_MODEL_T2V = 'Qwen/Qwen2.5-14B-Instruct'
DEFAULT_LOCAL_QWEN_MODEL_I2V = 'Qwen/Qwen2.5-VL-7B-Instruct'

# --- Multi-GPU Settings ---
DEFAULT_ULYSSES_SIZE = 8
DEFAULT_DIT_FSDP = True
DEFAULT_T5_FSDP = True

# --- Serverless Deployment ---
# RunPod settings
RUNPOD_API_KEY = os.environ.get('RUNPOD_API_KEY')
DOCKER_IMAGE_NAME = 'genvidim-serverless'

# Add any other configurations you might need
# For example, paths to other assets, logs, etc.
ASSETS_DIR = os.path.join(BASE_DIR, 'assets')
EXAMPLES_DIR = os.path.join(BASE_DIR, 'examples')
LOGS_DIR = os.path.join(BASE_DIR, 'logs')

# Create logs directory if it doesn't exist
os.makedirs(LOGS_DIR, exist_ok=True)
