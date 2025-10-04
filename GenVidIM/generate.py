# Copyright 2024-2025 The Alibaba Wan Team Authors. All rights reserved.
import argparse
import logging
import os
import sys
import warnings
from datetime import datetime
from functools import lru_cache

warnings.filterwarnings('ignore')

import random

import torch
import torch.distributed as dist
from PIL import Image

import wan
from wan.configs import MAX_AREA_CONFIGS, SIZE_CONFIGS, SUPPORTED_SIZES, WAN_CONFIGS
from wan.distributed.util import init_distributed_group
from wan.utils.prompt_extend import DashScopePromptExpander, QwenPromptExpander
from wan.utils.utils import merge_video_audio, save_video, str2bool
import config


EXAMPLE_PROMPT = {
    "t2v-A14B": {
        "prompt":
            "Two anthropomorphic cats in comfy boxing gear and bright gloves fight intensely on a spotlighted stage.",
    },
    "i2v-A14B": {
        "prompt":
            "Summer beach vacation style, a white cat wearing sunglasses sits on a surfboard. The fluffy-furred feline gazes directly at the camera with a relaxed expression. Blurred beach scenery forms the background featuring crystal-clear waters, distant green hills, and a blue sky dotted with white clouds. The cat assumes a naturally relaxed posture, as if savoring the sea breeze and warm sunlight. A close-up shot highlights the feline's intricate details and the refreshing atmosphere of the seaside.",
        "image":
            os.path.join(config.EXAMPLES_DIR, "i2v_input.JPG"),
    },
    "ti2v-5B": {
        "prompt":
            "Two anthropomorphic cats in comfy boxing gear and bright gloves fight intensely on a spotlighted stage.",
    },
    "animate-14B": {
        "prompt": "视频中的人在做动作",
        "video": "",
        "pose": "",
        "mask": "",
    },
    "s2v-14B": {
        "prompt":
            "Summer beach vacation style, a white cat wearing sunglasses sits on a surfboard. The fluffy-furred feline gazes directly at the camera with a relaxed expression. Blurred beach scenery forms the background featuring crystal-clear waters, distant green hills, and a blue sky dotted with white clouds. The cat assumes a naturally relaxed posture, as if savoring the sea breeze and warm sunlight. A close-up shot highlights the feline's intricate details and the refreshing atmosphere of the seaside.",
        "image":
            os.path.join(config.EXAMPLES_DIR, "i2v_input.JPG"),
        "audio":
            os.path.join(config.EXAMPLES_DIR, "talk.wav"),
        "tts_prompt_audio":
            os.path.join(config.EXAMPLES_DIR, "zero_shot_prompt.wav"),
        "tts_prompt_text":
            "希望你以后能够做的比我还好呦。",
        "tts_text":
            "收到好友从远方寄来的生日礼物，那份意外的惊喜与深深的祝福让我心中充满了甜蜜的快乐，笑容如花儿般绽放。"
    },
}


def _validate_args(args):
    # Basic check
    assert args.ckpt_dir is not None, "Please specify the checkpoint directory."
    assert args.task in WAN_CONFIGS, f"Unsupport task: {args.task}"
    assert args.task in EXAMPLE_PROMPT, f"Unsupport task: {args.task}"

    if args.prompt is None:
        args.prompt = EXAMPLE_PROMPT[args.task]["prompt"]
    if args.image is None and "image" in EXAMPLE_PROMPT[args.task]:
        args.image = EXAMPLE_PROMPT[args.task]["image"]
    if args.audio is None and args.enable_tts is False and "audio" in EXAMPLE_PROMPT[args.task]:
        args.audio = EXAMPLE_PROMPT[args.task]["audio"]
    if (args.tts_prompt_audio is None or args.tts_text is None) and args.enable_tts is True and "audio" in EXAMPLE_PROMPT[args.task]:
        args.tts_prompt_audio = EXAMPLE_PROMPT[args.task]["tts_prompt_audio"]
        args.tts_prompt_text = EXAMPLE_PROMPT[args.task]["tts_prompt_text"]
        args.tts_text = EXAMPLE_PROMPT[args.task]["tts_text"]

    if args.task == "i2v-A14B":
        assert args.image is not None, "Please specify the image path for i2v."

    cfg = WAN_CONFIGS[args.task]

    if args.sample_steps is None:
        args.sample_steps = cfg.sample_steps

    if args.sample_shift is None:
        args.sample_shift = cfg.sample_shift

    if args.sample_guide_scale is None:
        args.sample_guide_scale = cfg.sample_guide_scale

    if args.frame_num is None:
        args.frame_num = cfg.frame_num

    args.base_seed = args.base_seed if args.base_seed >= 0 else random.randint(
        0, sys.maxsize)
    # Size check
    if not 's2v' in args.task:
        assert args.size in SUPPORTED_SIZES[
            args.
            task], f"Unsupport size {args.size} for task {args.task}, supported sizes are: {', '.join(SUPPORTED_SIZES[args.task])}"


def _parse_args():
    parser = argparse.ArgumentParser(description="Generate a video from a text prompt or image using Wan.")
    
    # Task and model
    parser.add_argument("--task", type=str, default="t2v-A14B", choices=list(WAN_CONFIGS.keys()), help="The task to run.")
    parser.add_argument("--ckpt_dir", type=str, default=None, help="Path to the checkpoint directory.")
    
    # Generation parameters
    parser.add_argument("--prompt", type=str, default=None, help="The prompt for video generation.")
    parser.add_argument("--size", type=str, default=config.DEFAULT_VIDEO_SIZE, choices=list(SIZE_CONFIGS.keys()), help="Resolution of the generated video.")
    parser.add_argument("--frame_num", type=int, default=None, help="Number of frames to generate.")
    parser.add_argument("--sample_steps", type=int, default=None, help="Number of sampling steps.")
    parser.add_argument("--sample_guide_scale", type=float, default=None, help="Classifier-free guidance scale.")
    parser.add_argument("--base_seed", type=int, default=-1, help="Seed for random generation.")
    
    # Input files
    parser.add_argument("--image", type=str, default=None, help="Path to the input image.")
    parser.add_argument("--audio", type=str, default=None, help="Path to the input audio.")
    parser.add_argument("--pose_video", type=str, default=None, help="Path to the pose video.")
    
    # Performance and memory
    parser.add_argument("--offload_model", type=str2bool, default=None, help="Offload model to CPU to save GPU memory.")
    parser.add_argument("--convert_model_dtype", action="store_true", default=False, help="Convert model parameters to a different data type.")
    parser.add_argument("--t5_cpu", action="store_true", default=False, help="Place T5 model on CPU.")
    
    # Multi-GPU
    parser.add_argument("--ulysses_size", type=int, default=1, help="The size of the ulysses parallelism in DiT.")
    parser.add_argument("--t5_fsdp", action="store_true", default=False, help="Whether to use FSDP for T5.")
    parser.add_argument("--dit_fsdp", action="store_true", default=False, help="Whether to use FSDP for DiT.")

    # Prompt extension
    parser.add_argument("--use_prompt_extend", action="store_true", default=False, help="Enable prompt extension.")
    parser.add_argument("--prompt_extend_method", type=str, default=config.DEFAULT_PROMPT_EXTEND_METHOD, choices=["dashscope", "local_qwen"], help="Method for prompt extension.")
    parser.add_argument("--prompt_extend_model", type=str, default=None, help="The prompt extend model to use.")
    parser.add_argument("--prompt_extend_target_lang", type=str, default="zh", choices=["zh", "en"], help="The target language of prompt extend.")

    args = parser.parse_args()
    _validate_args(args)
    return args


def _init_logging(rank):
    # logging
    if rank == 0:
        # set format
        logging.basicConfig(
            level=logging.INFO,
            format="[%(asctime)s] %(levelname)s: %(message)s",
            handlers=[logging.StreamHandler(stream=sys.stdout)])
    else:
        logging.basicConfig(level=logging.ERROR)


def generate(args):
    rank = int(os.getenv("RANK", 0))
    world_size = int(os.getenv("WORLD_SIZE", 1))
    local_rank = int(os.getenv("LOCAL_RANK", 0))
    device = local_rank
    _init_logging(rank)

    if args.offload_model is None:
        args.offload_model = False if world_size > 1 else config.DEFAULT_OFFLOAD_MODEL
        logging.info(
            f"offload_model is not specified, set to {args.offload_model}.")
    if world_size > 1:
        torch.cuda.set_device(local_rank)
        dist.init_process_group(
            backend="nccl",
            init_method="env://",
            rank=rank,
            world_size=world_size)
    else:
        assert not (
            args.t5_fsdp or args.dit_fsdp
        ), f"t5_fsdp and dit_fsdp are not supported in non-distributed environments."
        assert not (
            args.ulysses_size > 1
        ), f"sequence parallel are not supported in non-distributed environments."

    if args.ulysses_size > 1:
        assert args.ulysses_size == world_size, f"The number of ulysses_size should be equal to the world size."
        init_distributed_group()

    if args.use_prompt_extend:
        if args.prompt_extend_method == "dashscope":
            prompt_expander = DashScopePromptExpander(
                model_name=args.prompt_extend_model,
                task=args.task,
                is_vl=args.image is not None)
        elif args.prompt_extend_method == "local_qwen":
            prompt_expander = QwenPromptExpander(
                model_name=args.prompt_extend_model,
                task=args.task,
                is_vl=args.image is not None,
                device=rank)
        else:
            raise NotImplementedError(
                f"Unsupport prompt_extend_method: {args.prompt_extend_method}")

    cfg = WAN_CONFIGS[args.task]
    if args.ulysses_size > 1:
        assert cfg.num_heads % args.ulysses_size == 0, f"`{cfg.num_heads=}` cannot be divided evenly by `{args.ulysses_size=}`."

    logging.info(f"Generation job args: {args}")
    logging.info(f"Generation model config: {cfg}")

    if dist.is_initialized():
        base_seed = [args.base_seed] if rank == 0 else [None]
        dist.broadcast_object_list(base_seed, src=0)
        args.base_seed = base_seed[0]

    logging.info(f"Input prompt: {args.prompt}")
    img = None
    if args.image is not None:
        img = Image.open(args.image).convert("RGB")
        logging.info(f"Input image: {args.image}")

    # prompt extend
    if args.use_prompt_extend:
        logging.info("Extending prompt ...")
        if rank == 0:
            prompt_output = prompt_expander(
                args.prompt,
                image=img,
                tar_lang=args.prompt_extend_target_lang,
                seed=args.base_seed)
            if prompt_output.status == False:
                logging.info(
                    f"Extending prompt failed: {prompt_output.message}")
                logging.info("Falling back to original prompt.")
                input_prompt = args.prompt
            else:
                input_prompt = prompt_output.prompt
            input_prompt = [input_prompt]
        else:
            input_prompt = [None]
        if dist.is_initialized():
            dist.broadcast_object_list(input_prompt, src=0)
        args.prompt = input_prompt[0]
        logging.info(f"Extended prompt: {args.prompt}")

    @lru_cache(maxsize=None)
    def get_pipeline(task, ckpt_dir, device, rank, t5_fsdp, dit_fsdp, ulysses_size, t5_cpu, convert_model_dtype, use_relighting_lora=False):
        if "t2v" in task:
            logging.info("Creating WanT2V pipeline.")
            return wan.WanT2V(
                config=cfg,
                checkpoint_dir=ckpt_dir,
                device_id=device,
                rank=rank,
                t5_fsdp=t5_fsdp,
                dit_fsdp=dit_fsdp,
                use_sp=(ulysses_size > 1),
                t5_cpu=t5_cpu,
                convert_model_dtype=convert_model_dtype,
            )
        elif "ti2v" in task:
            logging.info("Creating WanTI2V pipeline.")
            return wan.WanTI2V(
                config=cfg,
                checkpoint_dir=ckpt_dir,
                device_id=device,
                rank=rank,
                t5_fsdp=t5_fsdp,
                dit_fsdp=dit_fsdp,
                use_sp=(ulysses_size > 1),
                t5_cpu=t5_cpu,
                convert_model_dtype=convert_model_dtype,
            )
        elif "animate" in task:
            logging.info("Creating Wan-Animate pipeline.")
            return wan.WanAnimate(
                config=cfg,
                checkpoint_dir=ckpt_dir,
                device_id=device,
                rank=rank,
                t5_fsdp=t5_fsdp,
                dit_fsdp=dit_fsdp,
                use_sp=(ulysses_size > 1),
                t5_cpu=t5_cpu,
                convert_model_dtype=convert_model_dtype,
                use_relighting_lora=use_relighting_lora
            )
        elif "s2v" in task:
            logging.info("Creating WanS2V pipeline.")
            return wan.WanS2V(
                config=cfg,
                checkpoint_dir=ckpt_dir,
                device_id=device,
                rank=rank,
                t5_fsdp=t5_fsdp,
                dit_fsdp=dit_fsdp,
                use_sp=(ulysses_size > 1),
                t5_cpu=t5_cpu,
                convert_model_dtype=convert_model_dtype,
            )
        else:
            logging.info("Creating WanI2V pipeline.")
            return wan.WanI2V(
                config=cfg,
                checkpoint_dir=ckpt_dir,
                device_id=device,
                rank=rank,
                t5_fsdp=t5_fsdp,
                dit_fsdp=dit_fsdp,
                use_sp=(ulysses_size > 1),
                t5_cpu=t5_cpu,
                convert_model_dtype=convert_model_dtype,
            )

    pipeline = get_pipeline(
        args.task, args.ckpt_dir, device, rank, args.t5_fsdp, args.dit_fsdp,
        args.ulysses_size, args.t5_cpu, args.convert_model_dtype,
        getattr(args, 'use_relighting_lora', False)
    )

    if "t2v" in args.task:
        logging.info(f"Generating video ...")
        video = pipeline.generate(
            args.prompt,
            size=SIZE_CONFIGS[args.size],
            frame_num=args.frame_num,
            shift=args.sample_shift,
            sample_solver=args.sample_solver,
            sampling_steps=args.sample_steps,
            guide_scale=args.sample_guide_scale,
            seed=args.base_seed,
            offload_model=args.offload_model)
    elif "ti2v" in args.task:
        logging.info(f"Generating video ...")
        video = pipeline.generate(
            args.prompt,
            img=img,
            size=SIZE_CONFIGS[args.size],
            max_area=MAX_AREA_CONFIGS[args.size],
            frame_num=args.frame_num,
            shift=args.sample_shift,
            sample_solver=args.sample_solver,
            sampling_steps=args.sample_steps,
            guide_scale=args.sample_guide_scale,
            seed=args.base_seed,
            offload_model=args.offload_model)
    elif "animate" in args.task:
        logging.info(f"Generating video ...")
        video = pipeline.generate(
            src_root_path=args.src_root_path,
            replace_flag=args.replace_flag,
            refert_num = args.refert_num,
            clip_len=args.frame_num,
            shift=args.sample_shift,
            sample_solver=args.sample_solver,
            sampling_steps=args.sample_steps,
            guide_scale=args.sample_guide_scale,
            seed=args.base_seed,
            offload_model=args.offload_model)
    elif "s2v" in args.task:
        logging.info(f"Generating video ...")
        video = pipeline.generate(
            input_prompt=args.prompt,
            ref_image_path=args.image,
            audio_path=args.audio,
            enable_tts=args.enable_tts,
            tts_prompt_audio=args.tts_prompt_audio,
            tts_prompt_text=args.tts_prompt_text,
            tts_text=args.tts_text,
            num_repeat=args.num_clip,
            pose_video=args.pose_video,
            max_area=MAX_AREA_CONFIGS[args.size],
            infer_frames=args.infer_frames,
            shift=args.sample_shift,
            sample_solver=args.sample_solver,
            sampling_steps=args.sample_steps,
            guide_scale=args.sample_guide_scale,
            seed=args.base_seed,
            offload_model=args.offload_model,
            init_first_frame=args.start_from_ref,
        )
    else:
        logging.info("Generating video ...")
        video = pipeline.generate(
            args.prompt,
            img,
            max_area=MAX_AREA_CONFIGS[args.size],
            frame_num=args.frame_num,
            shift=args.sample_shift,
            sample_solver=args.sample_solver,
            sampling_steps=args.sample_steps,
            guide_scale=args.sample_guide_scale,
            seed=args.base_seed,
            offload_model=args.offload_model)

    if rank == 0:
        if args.save_file is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            sanitized_prompt = "".join(c if c.isalnum() else "_" for c in args.prompt)[:50]
            args.save_file = f"{args.task}_{args.size.replace('*','x')}_{timestamp}_{sanitized_prompt}.mp4"
        
        output_path = os.path.join(config.LOGS_DIR, args.save_file)
        
        logging.info(f"Saving generated video to {output_path}")
        save_video(
            tensor=video[None],
            save_file=output_path,
            fps=cfg.sample_fps,
            nrow=1,
            normalize=True,
            value_range=(-1, 1)
        )
        if "s2v" in args.task:
            audio_path = os.path.join(config.ASSETS_DIR, "tts.wav") if args.enable_tts else args.audio
            merge_video_audio(video_path=output_path, audio_path=audio_path)

    del video

    torch.cuda.synchronize()
    if dist.is_initialized():
        dist.barrier()
        dist.destroy_process_group()

    logging.info("Finished.")


if __name__ == "__main__":
    args = _parse_args()
    generate(args)
