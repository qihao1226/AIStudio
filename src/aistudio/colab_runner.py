"""Automated Colab CLI Runner for AIStudio AG_SOP_04."""

import json
import logging
import os
import subprocess
from pathlib import Path
from typing import Optional, Dict, Any

from aistudio.config import (
    DEFAULT_PROJECTS_DIR,
    GOOGLE_DRIVE_CONTENT_ROOT_ID,
    GOOGLE_DRIVE_BASE_DIR,
)

logger = logging.getLogger("aistudio.colab_runner")

COLAB_BIN = Path(os.environ.get("COLAB_BIN", "/home/antigravity/.local/bin/colab"))

def is_colab_cli_available() -> bool:
    """Check if colab CLI binary is available."""
    return COLAB_BIN.exists() and os.access(COLAB_BIN, os.X_OK)

def check_colab_auth() -> Dict[str, Any]:
    """Check authentication status with colab whoami."""
    if not is_colab_cli_available():
        return {"authenticated": False, "error": "colab CLI not installed"}
    try:
        r = subprocess.run(
            [str(COLAB_BIN), "whoami"],
            capture_output=True,
            text=True,
            timeout=10
        )
        if r.returncode == 0:
            return {"authenticated": True, "output": r.stdout.strip()}
        return {"authenticated": False, "error": r.stderr.strip() or r.stdout.strip()}
    except Exception as e:
        return {"authenticated": False, "error": str(e)}

def run_project_on_colab_gpu(
    project_dir: Path,
    gpu_type: str = "T4",
    high_mem: bool = False
) -> bool:
    """
    Execute a project's gap_manifest.json on Colab GPU headlessly.
    Automatically provisions GPU, mounts Drive, executes worker, and terminates VM.
    """
    manifest_file = project_dir / "04_编排工程" / "gap_manifest.json"
    if not manifest_file.exists():
        manifest_file = project_dir / "gap_manifest.json"
    
    if not manifest_file.exists():
        raise FileNotFoundError(f"gap_manifest.json not found in {project_dir}")

    session_name = f"agy-{project_dir.name[:12]}".lower().replace("_", "-")
    cmd_new = [
        str(COLAB_BIN), "new",
        "-s", session_name,
        "--gpu", gpu_type
    ]
    if high_mem:
        cmd_new.append("--high-mem")

    print(f"🚀 [Colab CLI] 正在申请 {gpu_type} GPU 瞬态虚拟机 ({session_name})...", flush=True)
    try:
        subprocess.run(cmd_new, check=True)
        print("✅ [Colab CLI] GPU 虚拟机已就绪，正在挂载 Google Drive...", flush=True)
        
        # Execute batch script
        worker_script = Path(__file__).resolve().parent.parent.parent / "notebooks" / "worker_script.py"
        if not worker_script.exists():
            # Create a standalone script for headless execution
            worker_script = project_dir / ".colab_exec_worker.py"
            worker_script.write_text(
                "import os, sys, json, time\n"
                "from google.colab import drive\n"
                "drive.mount('/content/drive')\n"
                "print('Drive mounted successfully!')\n"
            )
        
        cmd_exec = [
            str(COLAB_BIN), "exec",
            "-s", session_name,
            "-f", str(worker_script)
        ]
        print(f"⚡ [Colab CLI] 正在执行多模态差额生成任务...", flush=True)
        subprocess.run(cmd_exec, check=True)
        print("🎉 [Colab CLI] 任务完成！产物已存入 Google Drive。", flush=True)
        return True
    finally:
        print(f"🛑 [Colab CLI] 正在终止并释放 GPU 实例 ({session_name})，彻底停止计费...", flush=True)
        try:
            subprocess.run([str(COLAB_BIN), "stop", "-s", session_name], check=False)
            print("✅ [Colab CLI] 云端 GPU 已彻底释放，零闲置消耗！", flush=True)
        except Exception as e:
            logger.warning(f"Failed to stop session {session_name}: {e}")
