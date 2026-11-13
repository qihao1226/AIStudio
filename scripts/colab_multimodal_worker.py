#!/usr/bin/env python3
"""
YOUAI Cloud Video Factory - Headless Colab Multimodal Worker (v3.5)
===================================================================
Upgraded Top-Tier Open-Source Multimodal Stack for Google Colab (L4 / A100 / T4):
  1. Image Generation (T2I & Bilingual Typography):
     - Default Flagship (`z-image-turbo`): `Tongyi-MAI/Z-Image-Turbo` (6B S3-DiT + Qwen3 Text Encoder,
       Apache 2.0). #1 Open-Source model on AI Arena; generates 1080p photorealistic images AND
       accurate Chinese/English typography in 8 steps (~2.5s on L4/A100).
     - Secondary Engine (`flux-schnell`): `unsloth/FLUX.1-schnell` (12B MMDiT, Apache 2.0, ungated)
       for 4-step Western commercial photography & cinematic lighting.
     - Lightweight Fallback (`sdxl-turbo`): `stabilityai/sdxl-turbo` (`guidance_scale=0.0`).
  2. Voice, Speech Cloning & Audio Mastering (The "Golden 4-Tier" Audio Fleet):
     - Tier 1 Studio Documentary & Podcast Narrator (`kokoro`): `hexgrad/Kokoro-82M` (StyleTTS2 + ISTFTNet,
       Apache 2.0). #1 Open-Weight TTS Arena model with 8 native Mandarin studio voices
       (`zm_yunjian`, `zm_yunxi`, `zm_yunyang`, `zm_yunxia`, `zf_xiaoxiao`, `zf_xiaobei`,
       `zf_xiaoni`, `zf_xiaoyi`) and 20+ English studio voices (`af_heart`, `am_fenrir`, `am_michael`).
     - Tier 2 Chinese Pinyin & Emotion-Controllable Explainer (`index-tts`): `IndexTeam/IndexTTS-2.5`
       (Bilibili, 0.8B GPT + CFM + BigVGAN). Solves polyphone errors with Pinyin syntax (`{重|chong2}构`),
       supports pause control `[pause:0.5s]`, and timbre-emotion disentanglement (`--emo-audio`, `--emo-text`).
     - Tier 3 48kHz Broadcast Master & Prompt Voice Design (`voxcpm`): `openbmb/VoxCPM2` (OpenBMB,
       2B Tokenizer-Free MiniCPM-4 base). Generates native 48kHz studio audio; creates new voices purely
       via natural language description (`--voice-design`) or high-fidelity cloning.
     - Tier 4 Zero-Shot Flow Matching Voice Cloning (`f5-tts`): `SWivid/F5-TTS` (`F5TTS_v1_Base`, Flow
       Matching). Clones any 3-10s reference WAV file (`--ref-audio`) in Mandarin, English, or mixed speech.
     - Mandatory Broadcast Audio Mastering: 30ms Anti-Pop fade (`afade`) + EBU R128 `-14.0 LUFS`
       loudness normalization (`loudnorm=I=-14:TP=-1.5:LRA=11`) + `48kHz` (VoxCPM) / `44.1kHz` 16-bit PCM WAV.
  3. Millisecond Word-Level Timestamp ASR (`faster-whisper-turbo`):
     - `mobiuslabsgmbh/faster-whisper-large-v3-turbo` (6x faster than large-v3, float16 on CUDA)
       for driving OpenFilm dynamic subtitles and kinetic flash typography.
  4. 5TB Google Drive Model Vault Caching:
     - Automatically caches weights under `/content/drive/MyDrive/AIStudio_Models/hf_cache` when
       Google Drive is mounted (`--use-drive-cache`), eliminating repeated downloads across sessions.
"""

import os
import re
import sys
import json
import time
import shutil
import subprocess
from pathlib import Path

os.environ.setdefault("HF_XET_HIGH_PERFORMANCE", "1")

# Map legacy edge-tts voice names to Kokoro-82M studio voice IDs
VOICE_ALIAS_MAP = {
    "zh-cn-yunjianneural": "zm_yunjian",
    "zh-cn-yunxineural": "zm_yunxi",
    "zh-cn-yunyangneural": "zm_yunyang",
    "zh-cn-yunxianeural": "zm_yunxia",
    "zh-cn-xiaoxiaoneural": "zf_xiaoxiao",
    "zh-cn-xiaobeineural": "zf_xiaobei",
    "zh-cn-xiaonineural": "zf_xiaoni",
    "zh-cn-xiaoyineural": "zf_xiaoyi",
    "en-us-andrewneural": "am_michael",
    "en-us-brianneural": "am_fenrir",
    "en-us-avasneural": "af_heart",
    "en-us-jennyneural": "af_bella",
    "en-gb-ryanneural": "bm_george",
}


def write_status(status_path: str, state: str, message: str, extra: dict = None):
    if not status_path:
        return
    payload = {
        "state": state,
        "message": message,
        "timestamp": time.time(),
    }
    if extra:
        payload.update(extra)
    p = Path(status_path)
    p.parent.mkdir(parents=True, exist_ok=True)
    tmp = p.with_suffix(".tmp")
    tmp.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    tmp.replace(p)


def setup_model_vault(use_drive_cache: bool = True):
    """Configure HuggingFace cache in 5TB Google Drive Model Vault when mounted."""
    if not use_drive_cache:
        return
    drive_root = Path("/content/drive/MyDrive")
    if drive_root.exists():
        vault_cache = drive_root / "AIStudio_Models" / "hf_cache"
        vault_cache.mkdir(parents=True, exist_ok=True)
        os.environ["HF_HOME"] = str(vault_cache)
        print(f"🏦 [Model Vault] Mounted 5TB Google Drive Model Vault: {vault_cache}", flush=True)


def ensure_dependencies(need_f5: bool = False, need_voxcpm: bool = False, need_indextts: bool = False):
    """Install required top-tier multimodal packages on the remote Colab VM (Python 3.10-3.13 safe)."""
    missing_core = False
    try:
        import kokoro  # noqa: F401
        import misaki  # noqa: F401
        import faster_whisper  # noqa: F401
        import diffusers  # noqa: F401
        import edge_tts  # noqa: F401
    except ImportError:
        missing_core = True

    if missing_core:
        print("⏳ [Colab Worker] Installing top-tier multimodal dependencies (Kokoro-82M, Faster-Whisper-Turbo, Diffusers)...", flush=True)
        subprocess.run(["apt-get", "-qq", "-y", "install", "espeak-ng"], check=False)
        subprocess.run(
            [
                sys.executable, "-m", "pip", "install", "-q",
                "loguru", "addict", "cn2an", "jieba", "ordered-set",
                "pypinyin", "pypinyin-dict", "num2words", "espeakng-loader",
                "phonemizer-fork", "faster-whisper>=1.1.0", "edge-tts",
                "soundfile", "opencv-python-headless",
            ],
            check=True,
        )
        subprocess.run(
            [
                sys.executable, "-m", "pip", "install", "-q",
                "--ignore-requires-python", "--no-deps",
                "kokoro>=0.9.4", "misaki>=0.9.4",
            ],
            check=True,
        )

    if need_f5:
        try:
            import f5_tts  # noqa: F401
        except ImportError:
            print("⏳ [Colab Worker] Installing F5-TTS zero-shot voice cloning runtime...", flush=True)
            subprocess.run(
                [
                    sys.executable, "-m", "pip", "install", "-q",
                    "cached_path", "ema_pytorch>=0.5.2", "hydra-core>=1.3.0",
                    "pydub", "pypinyin", "rjieba", "tomli", "torchdiffeq",
                    "transformers_stream_generator", "unidecode", "vocos",
                    "x_transformers>=1.31.14",
                ],
                check=True,
            )
            subprocess.run(
                [
                    sys.executable, "-m", "pip", "install", "-q",
                    "--ignore-requires-python", "--no-deps", "f5-tts",
                ],
                check=True,
            )

    if need_voxcpm:
        try:
            import voxcpm  # noqa: F401
        except ImportError:
            print("⏳ [Colab Worker] Installing VoxCPM2 runtime (OpenBMB 2B 48kHz)...", flush=True)
            subprocess.run(
                [sys.executable, "-m", "pip", "install", "-q", "voxcpm", "soundfile"],
                check=False,
            )

    if need_indextts:
        try:
            import indextts  # noqa: F401
        except ImportError:
            print("⏳ [Colab Worker] Installing IndexTTS-2.5 runtime (Bilibili 0.8B GPT+CFM)...", flush=True)
            subprocess.run(
                [
                    sys.executable, "-m", "pip", "install", "-q",
                    "huggingface_hub", "soundfile", "bigvgan", "torchaudio",
                ],
                check=False,
            )
            res = subprocess.run([sys.executable, "-m", "pip", "install", "-q", "indextts"], check=False)
            if res.returncode != 0:
                subprocess.run(
                    [sys.executable, "-m", "pip", "install", "-q", "git+https://github.com/index-tts/index-tts.git"],
                    check=False,
                )



def locate_content_root() -> Path:
    """Locate the mounted Google Drive `内容生产` root or fallback to `/content/youai_work`."""
    candidates = [
        Path("/content/drive/MyDrive/YOUAI/内容生产"),
        Path("/content/drive/MyDrive/内容生产"),
    ]
    for c in candidates:
        if c.exists():
            return c
    drive_root = Path("/content/drive/MyDrive")
    if drive_root.exists():
        for p in drive_root.rglob("内容生产"):
            if p.is_dir():
                return p
        fallback = drive_root / "内容生产"
        fallback.mkdir(parents=True, exist_ok=True)
        return fallback
    local_root = Path("/content/youai_work")
    local_root.mkdir(parents=True, exist_ok=True)
    return local_root


def contains_chinese(text: str) -> bool:
    return bool(re.search(r"[\u4e00-\u9fff]", text))


class MultimodalEngine:
    def __init__(self):
        import torch
        self.torch = torch
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.vram_gb = (
            torch.cuda.get_device_properties(0).total_memory / (1024**3)
            if self.device == "cuda"
            else 0.0
        )
        self.gpu_name = (
            torch.cuda.get_device_name(0) if self.device == "cuda" else "CPU"
        )
        self.whisper_model = None
        self.image_pipe = None
        self.image_model_type = None
        self.kokoro_pipes = {}
        self.f5_tts_model = None
        self.voxcpm_model = None
        self.indextts_model = None
        print(
            f"🖥️ [Engine] Device: {self.gpu_name} ({self.device}, VRAM: {self.vram_gb:.2f} GiB)",
            flush=True,
        )

    def load_whisper(self, model_size="mobiuslabsgmbh/faster-whisper-large-v3-turbo", force_cpu: bool = False):
        if self.whisper_model is None or force_cpu:
            from faster_whisper import WhisperModel
            # On Colab CUDA 13, ctranslate2 looks for libcublas.so.12; symlink to .13 if present
            for lib in ("libcublas.so", "libcublasLt.so"):
                p13 = Path(f"/usr/local/cuda/lib64/{lib}.13")
                p12 = Path(f"/usr/lib/x86_64-linux-gnu/{lib}.12")
                if p13.exists() and not p12.exists():
                    try:
                        p12.symlink_to(p13)
                    except OSError:
                        pass
            dev = "cpu" if force_cpu else self.device
            compute_type = "float16" if dev == "cuda" else "int8"
            print(f"🎙️ [ASR] Loading Faster-Whisper ({model_size}, {dev}, {compute_type})...", flush=True)
            try:
                self.whisper_model = WhisperModel(model_size, device=dev, compute_type=compute_type)
            except Exception as e:
                print(f"⚠️ [ASR] Turbo repo fallback to large-v3 ({e})", flush=True)
                self.whisper_model = WhisperModel("large-v3", device=dev, compute_type=compute_type)
        return self.whisper_model

    def transcribe(self, audio_path: str, output_json_path: str) -> dict:
        import numpy as np
        model = self.load_whisper()
        print(f"🎙️ [ASR] Transcribing with millisecond word timestamps: {audio_path}", flush=True)
        # Decode via FFmpeg to 16kHz mono float32 to bypass PyAV 14+ metadata_errors bug on Python 3.13
        proc = subprocess.run(
            [
                "ffmpeg", "-nostdin", "-threads", "0", "-i", str(audio_path),
                "-f", "f32le", "-ac", "1", "-acodec", "pcm_f32le", "-ar", "16000", "-",
            ],
            capture_output=True,
            check=True,
        )
        audio_np = np.frombuffer(proc.stdout, np.float32).flatten()
        try:
            segments, info = model.transcribe(audio_np, beam_size=5, word_timestamps=True)
            segments = list(segments)
        except RuntimeError as e:
            print(f"⚠️ [ASR] CUDA library mismatch ({e}), switching to fast INT8 CPU inference...", flush=True)
            model = self.load_whisper(force_cpu=True)
            segments, info = model.transcribe(audio_np, beam_size=5, word_timestamps=True)
            segments = list(segments)
        result = {"language": info.language, "duration": round(info.duration, 3), "segments": [], "words": []}
        for s in segments:
            seg_words = []
            for w in (s.words or []):
                w_item = {
                    "word": w.word.strip(),
                    "start": round(w.start, 3),
                    "end": round(w.end, 3),
                    "prob": round(w.probability, 3),
                }
                if w_item["word"]:
                    seg_words.append(w_item)
                    result["words"].append(w_item)
            result["segments"].append({
                "id": s.id,
                "start": round(s.start, 3),
                "end": round(s.end, 3),
                "text": s.text.strip(),
                "words": seg_words,
            })
        Path(output_json_path).parent.mkdir(parents=True, exist_ok=True)
        with open(output_json_path, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        print(f"✅ [ASR] Saved {len(result['words'])} word timestamps -> {output_json_path}", flush=True)
        return result

    def generate_image(
        self,
        prompt: str,
        output_path: str,
        aspect_ratio: str = "16:9",
        steps: int = None,
        seed: int = 42,
        model: str = "z-image-turbo",
    ) -> str:
        from PIL import Image

        # Auto-select best model based on VRAM if not explicitly forced
        if model == "auto":
            model = "z-image-turbo" if self.vram_gb >= 14.0 else "sdxl-turbo"

        if self.image_pipe is None or self.image_model_type != model:
            if self.image_pipe is not None:
                del self.image_pipe
                if self.device == "cuda":
                    self.torch.cuda.empty_cache()

            if model == "z-image-turbo":
                from diffusers import ZImagePipeline
                print("🎨 [T2I] Loading Tongyi-MAI/Z-Image-Turbo (6B S3-DiT + Qwen3, bfloat16, low_cpu_mem_usage=True)...", flush=True)
                self.image_pipe = ZImagePipeline.from_pretrained(
                    "Tongyi-MAI/Z-Image-Turbo",
                    torch_dtype=self.torch.bfloat16,
                    low_cpu_mem_usage=True,
                )
                if self.vram_gb >= 28.0:
                    self.image_pipe.to(self.device)
                else:
                    self.image_pipe.enable_model_cpu_offload()
                self.image_model_type = "z-image-turbo"

            elif model == "flux-schnell":
                from diffusers import FluxPipeline
                print("🎨 [T2I] Loading unsloth/FLUX.1-schnell (12B MMDiT, bfloat16)...", flush=True)
                self.image_pipe = FluxPipeline.from_pretrained(
                    "unsloth/FLUX.1-schnell",
                    torch_dtype=self.torch.bfloat16,
                )
                if self.vram_gb >= 28.0:
                    self.image_pipe.to(self.device)
                else:
                    self.image_pipe.enable_model_cpu_offload()
                self.image_model_type = "flux-schnell"

            else:
                from diffusers import AutoPipelineForText2Image
                print("🎨 [T2I] Loading stabilityai/sdxl-turbo (fp16, guidance_scale=0.0)...", flush=True)
                self.image_pipe = AutoPipelineForText2Image.from_pretrained(
                    "stabilityai/sdxl-turbo",
                    torch_dtype=self.torch.float16 if self.device == "cuda" else self.torch.float32,
                    variant="fp16" if self.device == "cuda" else None,
                ).to(self.device)
                self.image_model_type = "sdxl-turbo"

        if aspect_ratio == "16:9":
            gen_w, gen_h = (1344, 768) if self.image_model_type in ("z-image-turbo", "flux-schnell") else (1024, 576)
            target_w, target_h = 1920, 1080
        elif aspect_ratio == "9:16":
            gen_w, gen_h = (768, 1344) if self.image_model_type in ("z-image-turbo", "flux-schnell") else (576, 1024)
            target_w, target_h = 1080, 1920
        else:
            gen_w, gen_h = 1024, 1024
            target_w, target_h = 1080, 1080

        if self.image_model_type == "z-image-turbo":
            infer_steps = steps if (steps and steps >= 8) else 9  # 9 results in 8 DiT forwards
        elif self.image_model_type == "flux-schnell":
            infer_steps = steps if (steps and 1 <= steps <= 8) else 4
        else:
            infer_steps = max(1, min(steps or 4, 4))

        generator = (
            self.torch.Generator(device="cuda" if self.device == "cuda" else "cpu").manual_seed(int(seed))
            if seed is not None
            else None
        )

        t0 = time.time()
        call_kwargs = dict(
            prompt=prompt,
            width=gen_w,
            height=gen_h,
            num_inference_steps=infer_steps,
            guidance_scale=0.0,
            generator=generator,
        )
        if self.image_model_type == "flux-schnell":
            call_kwargs["max_sequence_length"] = 256

        image = self.image_pipe(**call_kwargs).images[0]
        dt = time.time() - t0

        image = image.resize((target_w, target_h), Image.Resampling.LANCZOS)
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        image.save(output_path)
        print(
            f"✅ [T2I:{self.image_model_type}] Generated {target_w}x{target_h} in {dt:.2f}s -> {output_path}",
            flush=True,
        )
        return output_path

    def _get_kokoro_pipe(self, lang_code: str):
        if lang_code not in self.kokoro_pipes:
            from kokoro import KPipeline
            print(f"🗣️ [Kokoro-82M] Loading studio TTS pipeline (lang='{lang_code}')...", flush=True)
            self.kokoro_pipes[lang_code] = KPipeline(
                lang_code=lang_code,
                repo_id="hexgrad/Kokoro-82M",
                device=self.device,
            )
        return self.kokoro_pipes[lang_code]

    def generate_tts(
        self,
        text: str,
        output_path: str,
        ref_audio: str = None,
        ref_text: str = "",
        speed: float = 1.0,
        voice: str = "zm_yunjian",
        engine: str = "auto",
        voice_design: str = "",
        emo_audio: str = None,
        emo_text: str = "",
        with_timestamps: bool = False,
    ) -> str:
        import numpy as np
        import soundfile as sf

        out_p = Path(output_path)
        out_p.parent.mkdir(parents=True, exist_ok=True)
        raw_wav = str(out_p.with_suffix(".raw.wav"))
        used_engine = None
        target_sample_rate = 44100

        # Normalize legacy edge-tts voice names to Kokoro studio voice IDs
        norm_voice = VOICE_ALIAS_MAP.get(voice.lower(), voice)
        if norm_voice not in (
            "zm_yunjian", "zm_yunxi", "zm_yunyang", "zm_yunxia",
            "zf_xiaoxiao", "zf_xiaobei", "zf_xiaoni", "zf_xiaoyi",
            "af_heart", "af_bella", "af_nova", "af_sarah",
            "am_fenrir", "am_michael", "am_adam", "am_onyx",
            "bf_emma", "bm_george", "bm_lewis",
        ):
            norm_voice = "zm_yunjian" if contains_chinese(text) else "af_heart"

        def get_studio_ref_anchor():
            prompt_wav = str(out_p.with_suffix(".prompt_ref.wav"))
            if not os.path.exists(prompt_wav):
                pipe = self._get_kokoro_pipe("z")
                prompt_text = "欢迎来到云端视频生产工厂，算力即生产力，每一帧都是工业级母带。"
                chunks = [audio for _, _, audio in pipe(prompt_text, voice=norm_voice, speed=1.0) if audio is not None]
                sf.write(prompt_wav, np.concatenate(chunks), 24000)
            return prompt_wav

        # 1. Bilibili IndexTTS-2.5 (Pinyin pronunciation control & Disentangled Emotion)
        if engine in ("index-tts", "indextts", "index-tts-2.5") or (
            engine == "auto" and (emo_audio or emo_text or (ref_audio and re.search(r'[{|}]|[A-Z]{2,}\d|\[pause:', text)))
        ):
            try:
                ensure_dependencies(need_indextts=True)
                drive_vault = Path("/content/drive/MyDrive/AIStudio_Models/IndexTTS-2.5")
                local_model_dir = Path("/content/IndexTTS-2.5")
                model_dir = None
                for candidate in [drive_vault, local_model_dir]:
                    if (candidate / "config.yaml").exists():
                        model_dir = candidate
                        break
                if model_dir is None:
                    print("📥 [IndexTTS-2.5] Downloading model weights from IndexTeam/IndexTTS-2.5...", flush=True)
                    target_dir = drive_vault if Path("/content/drive/MyDrive").exists() else local_model_dir
                    from huggingface_hub import snapshot_download
                    snapshot_download(repo_id="IndexTeam/IndexTTS-2.5", local_dir=str(target_dir))
                    model_dir = target_dir

                if self.indextts_model is None:
                    print(f"🗣️ [IndexTTS-2.5] Initializing Bilibili 0.8B GPT+CFM engine from {model_dir}...", flush=True)
                    try:
                        from indextts.infer_v2 import IndexTTS2
                    except ImportError:
                        from indextts.infer_v2_5 import IndexTTS2
                    self.indextts_model = IndexTTS2(
                        cfg_path=str(model_dir / "config.yaml"),
                        model_dir=str(model_dir),
                        use_fp16=True if self.device == "cuda" else False,
                    )

                actual_ref = ref_audio if (ref_audio and Path(ref_audio).exists()) else get_studio_ref_anchor()
                t0 = time.time()
                infer_kwargs = {
                    "spk_audio_prompt": str(actual_ref),
                    "text": text,
                    "output_path": raw_wav,
                    "speed": float(speed),
                    "verbose": True,
                }
                if emo_audio and Path(emo_audio).exists():
                    infer_kwargs["emo_audio_prompt"] = str(emo_audio)
                if emo_text:
                    infer_kwargs["emo_text"] = emo_text
                    infer_kwargs["use_emo_text"] = True

                self.indextts_model.infer(**infer_kwargs)
                print(f"✅ [IndexTTS-2.5] Synthesized emotion/pinyin controlled speech in {time.time()-t0:.2f}s", flush=True)
                used_engine = "index-tts-2.5"
            except Exception as e:
                print(f"⚠️ [IndexTTS-2.5] Fallback due to error ({e})", flush=True)

        # 2. OpenBMB VoxCPM2 (2B Tokenizer-Free 48kHz & Prompt Voice Design)
        if not used_engine and (
            engine in ("voxcpm", "voxcpm2") or (
                engine == "auto" and (voice_design or (text.startswith("(") and ")" in text[:120]))
            )
        ):
            try:
                ensure_dependencies(need_voxcpm=True)
                from voxcpm import VoxCPM
                if self.voxcpm_model is None:
                    print("🗣️ [VoxCPM2] Loading OpenBMB/VoxCPM2 (2B Tokenizer-Free 48kHz)...", flush=True)
                    self.voxcpm_model = VoxCPM.from_pretrained("openbmb/VoxCPM2", load_denoiser=False)

                synth_text = text
                if voice_design and not text.startswith("("):
                    synth_text = f"({voice_design}){text}"

                t0 = time.time()
                gen_kwargs = {
                    "text": synth_text,
                    "cfg_value": 2.0,
                    "inference_timesteps": 10,
                }
                if ref_audio and Path(ref_audio).exists():
                    gen_kwargs["reference_wav_path"] = str(ref_audio)
                    if ref_text:
                        gen_kwargs["prompt_text"] = ref_text

                wav = self.voxcpm_model.generate(**gen_kwargs)
                out_sr = getattr(self.voxcpm_model, "sample_rate", 48000)
                sf.write(raw_wav, wav, out_sr)
                target_sample_rate = 48000
                print(f"✅ [VoxCPM2] Synthesized 48kHz studio audio in {time.time()-t0:.2f}s", flush=True)
                used_engine = "voxcpm2"
            except Exception as e:
                print(f"⚠️ [VoxCPM2] Fallback due to error ({e})", flush=True)

        # 3. Zero-Shot Voice Cloning via F5-TTS (when ref_audio exists or engine == "f5-tts")
        if not used_engine and ((ref_audio and Path(ref_audio).exists()) or engine == "f5-tts"):
            try:
                ensure_dependencies(need_f5=True)
                from f5_tts.api import F5TTS
                if self.f5_tts_model is None:
                    print("🗣️ [F5-TTS] Loading SWivid/F5-TTS zero-shot voice cloning engine...", flush=True)
                    self.f5_tts_model = F5TTS(device=self.device)

                actual_ref = ref_audio if (ref_audio and Path(ref_audio).exists()) else get_studio_ref_anchor()
                actual_ref_text = ref_text or "欢迎来到云端视频生产工厂，算力即生产力，每一帧都是工业级母带。"

                t0 = time.time()
                self.f5_tts_model.infer(
                    ref_file=str(actual_ref),
                    ref_text=actual_ref_text,
                    gen_text=text,
                    speed=speed,
                    file_wave=raw_wav,
                )
                print(f"✅ [F5-TTS] Zero-shot cloned speech in {time.time()-t0:.2f}s", flush=True)
                used_engine = "f5-tts"
            except Exception as e:
                print(f"⚠️ [F5-TTS] Fallback to Kokoro-82M studio TTS ({e})", flush=True)

        # 4. Studio Documentary & Podcast Narrator via Kokoro-82M (Apache 2.0)
        if not used_engine and engine in ("auto", "kokoro", "kokoro-82m"):
            try:
                lang_code = "z" if (contains_chinese(text) or norm_voice.startswith("z")) else (
                    "b" if norm_voice.startswith("b") else "a"
                )
                pipe = self._get_kokoro_pipe(lang_code)
                t0 = time.time()
                audio_chunks = []
                # Split text into sentence clauses to prevent 510-token truncation in misaki/kokoro
                parts = [p.strip() for p in re.split(r'([。！？\n]+)', text) if p.strip()]
                sentences = []
                curr = ""
                for part in parts:
                    curr += part
                    if re.search(r'[。！？\n]$', part):
                        sentences.append(curr)
                        curr = ""
                if curr:
                    sentences.append(curr)
                if not sentences:
                    sentences = [text]

                for s in sentences:
                    for _, _, audio in pipe(s, voice=norm_voice, speed=speed):
                        if audio is not None:
                            audio_chunks.append(
                                audio.cpu().numpy() if hasattr(audio, "cpu") else np.asarray(audio)
                            )
                if not audio_chunks:
                    raise RuntimeError("Kokoro returned empty audio chunks")
                full_audio = np.concatenate(audio_chunks)
                sf.write(raw_wav, full_audio, 24000)
                print(
                    f"✅ [Kokoro-82M] Synthesized studio voice '{norm_voice}' in {time.time()-t0:.2f}s",
                    flush=True,
                )
                used_engine = f"kokoro-82m:{norm_voice}"
            except Exception as e:
                print(f"⚠️ [Kokoro-82M] Fallback to neural edge-tts ({e})", flush=True)

        # 5. Emergency fallback to edge-tts
        if not used_engine:
            raw_mp3 = str(out_p.with_suffix(".raw.mp3"))
            edge_voice = voice if "Neural" in voice else (
                "zh-CN-YunjianNeural" if contains_chinese(text) else "en-US-AndrewNeural"
            )
            rate_pct = int(round((speed - 1.0) * 100))
            rate_str = f"{rate_pct:+d}%"
            subprocess.run(
                [
                    "edge-tts",
                    "--text", text,
                    "--voice", edge_voice,
                    f"--rate={rate_str}",
                    "--write-media", raw_mp3,
                ],
                check=True,
            )
            raw_wav = raw_mp3
            used_engine = f"edge-tts:{edge_voice}"

        # Mandatory Broadcast Audio Mastering:
        # 30ms Anti-Pop fade-in/out + EBU R128 -14.0 LUFS normalization + 48kHz (VoxCPM) / 44.1kHz 16-bit PCM WAV
        af_chain = (
            "afade=t=in:st=0:d=0.03,"
            "areverse,afade=t=in:st=0:d=0.03,areverse,"
            "loudnorm=I=-14:TP=-1.5:LRA=11"
        )
        subprocess.run(
            [
                "ffmpeg", "-y", "-i", raw_wav,
                "-af", af_chain,
                "-ar", str(target_sample_rate), "-ac", "1", "-c:a", "pcm_s16le",
                str(out_p),
            ],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        for tmp_f in [raw_wav, str(out_p.with_suffix(".prompt_ref.wav"))]:
            try:
                if os.path.exists(tmp_f):
                    os.remove(tmp_f)
            except OSError:
                pass

        print(f"✅ [TTS:{used_engine}] Mastered -14 LUFS anti-pop PCM WAV ({target_sample_rate}Hz) -> {out_p}", flush=True)

        if with_timestamps:
            ts_path = str(out_p.with_suffix(".words.json"))
            self.transcribe(str(out_p), ts_path)

        return str(out_p)


def execute_manifest(engine: MultimodalEngine, manifest_path: Path, drive_project_root: Path = None, status_path: str = None):
    if not manifest_path.exists():
        raise FileNotFoundError(f"Manifest not found: {manifest_path}")
    with open(manifest_path, "r", encoding="utf-8") as f:
        manifest = json.load(f)

    project_id = manifest.get("project_id", "default_project")
    tasks = manifest.get("tasks", [])
    base_dir = (
        manifest_path.parent
        if (manifest_path.parent / "02_generated").exists()
        else manifest_path.parent.parent
    )
    if drive_project_root:
        candidate = Path(drive_project_root) / project_id
        if candidate.exists():
            base_dir = candidate

    print(f"\n📋 [Manifest] Executing project: {project_id} ({len(tasks)} tasks) in {base_dir}", flush=True)
    results = []
    for idx, task in enumerate(tasks, 1):
        t_type = task["type"]
        t_id = task.get("task_id", f"task_{idx}")
        out_abs = str(base_dir / task["output_path"]) if not Path(task["output_path"]).is_absolute() else task["output_path"]
        params = task.get("params", {})
        msg = f"[{idx}/{len(tasks)}] Running {t_id} ({t_type})"
        print(f"  {msg}", flush=True)
        write_status(status_path, "running", msg, {"current_task": idx, "total_tasks": len(tasks)})

        if t_type == "tts_narration":
            ref = params.get("ref_audio")
            if ref and not Path(ref).is_absolute():
                ref = str(base_dir / ref)
            emo_ref = params.get("emo_audio")
            if emo_ref and not Path(emo_ref).is_absolute():
                emo_ref = str(base_dir / emo_ref)
            engine.generate_tts(
                params["text"],
                out_abs,
                ref_audio=ref,
                ref_text=params.get("ref_text", ""),
                speed=params.get("speed", 1.0),
                voice=params.get("voice", "zm_yunjian"),
                engine=params.get("engine", "auto"),
                voice_design=params.get("voice_design", ""),
                emo_audio=emo_ref,
                emo_text=params.get("emo_text", ""),
                with_timestamps=params.get("with_timestamps", True),
            )
        elif t_type == "text_to_image":
            engine.generate_image(
                params["prompt"],
                out_abs,
                aspect_ratio=params.get("aspect_ratio", "16:9"),
                steps=params.get("steps", None),
                seed=params.get("seed", 42),
                model=params.get("model", "z-image-turbo"),
            )
        elif t_type == "asr_transcribe":
            src = params["audio_file"]
            if not Path(src).is_absolute():
                src = str(base_dir / src)
            engine.transcribe(src, out_abs)
        results.append({"task_id": t_id, "type": t_type, "output_path": out_abs})

    lock_file = base_dir / "02_generated" / "manifest_completed.lock"
    lock_file.parent.mkdir(parents=True, exist_ok=True)
    with open(lock_file, "w", encoding="utf-8") as f:
        json.dump({"status": "completed", "project_id": project_id, "time": time.time(), "results": results}, f, indent=2)
    write_status(status_path, "completed", f"Completed {len(tasks)} tasks for {project_id}", {"results": results})
    print(f"🎉 [Manifest] Completed all tasks for {project_id}!", flush=True)


def main():
    import argparse
    parser = argparse.ArgumentParser(description="YOUAI Headless Colab Multimodal Worker (v3.5)")
    parser.add_argument("--manifest", help="Explicit path to gap_manifest.json or batch manifest")
    parser.add_argument("--project-id", help="Project ID under 内容生产/04_全源素材重构")
    parser.add_argument("--task", choices=["image", "tts", "asr"], help="Single standalone task type")
    parser.add_argument("--prompt", help="Image prompt or TTS text")
    parser.add_argument("--output", help="Output file path on remote Colab VM")
    parser.add_argument("--model", default="z-image-turbo", help="Image model: z-image-turbo | flux-schnell | sdxl-turbo")
    parser.add_argument("--aspect", default="16:9", help="Image aspect ratio: 16:9 | 9:16 | 1:1")
    parser.add_argument("--steps", type=int, default=None, help="Inference steps override")
    parser.add_argument("--seed", type=int, default=42, help="Random seed")
    parser.add_argument("--voice", default="zm_yunjian", help="TTS voice ID (e.g., zm_yunjian, zm_yunxi, zf_xiaoxiao, af_heart)")
    parser.add_argument("--engine", default="auto", help="TTS engine: auto | kokoro | f5-tts | index-tts | voxcpm")
    parser.add_argument("--ref-audio", help="Reference WAV path for zero-shot voice cloning")
    parser.add_argument("--ref-text", default="", help="Optional transcript of reference WAV")
    parser.add_argument("--voice-design", default="", help="Natural language voice description for VoxCPM2")
    parser.add_argument("--emo-audio", help="Emotion reference WAV path for IndexTTS-2.5")
    parser.add_argument("--emo-text", default="", help="Emotion description text for IndexTTS-2.5")
    parser.add_argument("--speed", type=float, default=1.0, help="Speech speed multiplier")
    parser.add_argument("--with-timestamps", action="store_true", help="Also emit .words.json via Faster-Whisper-Turbo")
    parser.add_argument("--audio-input", help="Input audio file for standalone ASR task")
    parser.add_argument("--status-file", help="Path to status.json for non-blocking polling")
    parser.add_argument("--no-drive-cache", action="store_true", help="Disable 5TB Google Drive Model Vault caching")
    args, _ = parser.parse_known_args()

    try:
        write_status(args.status_file, "initializing", "Setting up Model Vault & dependencies...")
        setup_model_vault(use_drive_cache=not args.no_drive_cache)
        need_f5 = bool(args.ref_audio or args.engine == "f5-tts")
        need_voxcpm = bool(args.engine in ("voxcpm", "voxcpm2") or args.voice_design)
        need_indextts = bool(args.engine in ("index-tts", "indextts", "index-tts-2.5") or args.emo_audio or args.emo_text)
        ensure_dependencies(need_f5=need_f5, need_voxcpm=need_voxcpm, need_indextts=need_indextts)
        engine = MultimodalEngine()

        if args.task == "image":
            write_status(args.status_file, "running", f"Generating image with {args.model}...")
            out = engine.generate_image(
                prompt=args.prompt,
                output_path=args.output,
                aspect_ratio=args.aspect,
                steps=args.steps,
                seed=args.seed,
                model=args.model,
            )
            write_status(args.status_file, "completed", "Image generation complete", {"output": out})
            return

        if args.task == "tts":
            write_status(args.status_file, "running", f"Generating speech with {args.engine}/{args.voice}...")
            out = engine.generate_tts(
                text=args.prompt,
                output_path=args.output,
                ref_audio=args.ref_audio,
                ref_text=args.ref_text,
                speed=args.speed,
                voice=args.voice,
                engine=args.engine,
                voice_design=args.voice_design,
                emo_audio=args.emo_audio,
                emo_text=args.emo_text,
                with_timestamps=args.with_timestamps,
            )
            extra = {"output": out}
            if args.with_timestamps:
                extra["timestamps"] = str(Path(out).with_suffix(".words.json"))
            write_status(args.status_file, "completed", "TTS generation complete", extra)
            return

        if args.task == "asr":
            write_status(args.status_file, "running", "Transcribing audio with Faster-Whisper-Turbo...")
            res = engine.transcribe(args.audio_input, args.output)
            write_status(args.status_file, "completed", "ASR transcription complete", {"output": args.output, "word_count": len(res.get("words", []))})
            return

        if args.manifest:
            execute_manifest(engine, Path(args.manifest), status_path=args.status_file)
            return

        content_root = locate_content_root()
        search_dirs = [
            content_root / "04_全源素材重构",
            content_root / "01_真素材数字可视化",
            content_root,
        ]
        processed = 0
        for s_dir in search_dirs:
            if not s_dir.exists():
                continue
            for p in s_dir.iterdir():
                if not p.is_dir():
                    continue
                if args.project_id and p.name != args.project_id:
                    continue
                mf = p / "04_编排工程" / "gap_manifest.json"
                if not mf.exists():
                    mf = p / "gap_manifest.json"
                lock = p / "02_generated" / "manifest_completed.lock"
                if mf.exists() and (not lock.exists() or args.project_id):
                    execute_manifest(engine, mf, drive_project_root=p.parent, status_path=args.status_file)
                    processed += 1

        write_status(args.status_file, "completed", f"Processed {processed} project(s).")
        print(f"✅ [Colab Worker] Finished scanning. Processed {processed} project(s).", flush=True)
    except Exception as e:
        import traceback
        tb = traceback.format_exc()
        print(f"❌ [Colab Worker Error] {e}\n{tb}", flush=True)
        write_status(args.status_file, "failed", str(e), {"traceback": tb})
        sys.exit(1)


if __name__ == "__main__":
    main()
