# Copyright 2026 YOUAI Cloud Video Factory
# Pure-HTTP Kernel RPC Bridge for Google Colab CLI in WebSocket-restricted environments.

import base64
import json
import logging
import time
import uuid
from typing import Any, Callable, Dict, List, Optional
from urllib.parse import quote

import requests

logger = logging.getLogger(__name__)

DAEMON_SCRIPT = r'''
import os
import sys
import json
import time
import fcntl
import threading
import traceback
import io

def _try_start_youai_daemon():
    if getattr(sys, "_youai_rpc_daemon_started", False):
        return
    try:
        lock_fd = open("/tmp/_youai_rpc.lock", "w")
        fcntl.flock(lock_fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except Exception:
        return

    sys._youai_rpc_daemon_started = True
    sys._youai_rpc_lock_fd = lock_fd
    _GLOBAL_NS = {"__name__": "__main__", "__builtins__": __builtins__}

    class _TeeIO(io.TextIOBase):
        def __init__(self, orig, log_path, buf_list):
            self.orig = orig
            self.log_path = log_path
            self.buf_list = buf_list
        def write(self, s):
            if not s:
                return 0
            self.buf_list.append(s)
            try:
                with open(self.log_path, "a", encoding="utf-8") as f:
                    f.write(s)
                    f.flush()
            except Exception:
                pass
            return len(s)
        def flush(self):
            try:
                self.orig.flush()
            except Exception:
                pass

    def _rpc_loop():
        try:
            os.makedirs("/content", exist_ok=True)
            os.chdir("/content")
        except Exception:
            pass
        with open("/tmp/_youai_rpc_ready", "w") as f:
            f.write(str(os.getpid()))

        while True:
            try:
                req_path = "/tmp/_youai_rpc_req.json"
                if os.path.exists(req_path):
                    try:
                        with open(req_path, "r", encoding="utf-8") as f:
                            req = json.load(f)
                        os.remove(req_path)
                    except Exception:
                        time.sleep(0.1)
                        continue

                    req_id = req.get("id", "default")
                    code = req.get("code", "")
                    stream_path = f"/tmp/_youai_rpc_stream_{req_id}.log"
                    resp_path = f"/tmp/_youai_rpc_resp_{req_id}.json"

                    stdout_buf = []
                    stderr_buf = []
                    old_out, old_err = sys.stdout, sys.stderr
                    sys.stdout = _TeeIO(old_out, stream_path, stdout_buf)
                    sys.stderr = _TeeIO(old_err, stream_path, stderr_buf)

                    outputs = []
                    try:
                        compiled = compile(code, "<colab-exec>", "exec")
                        exec(compiled, _GLOBAL_NS, _GLOBAL_NS)
                    except SystemExit as se:
                        if stdout_buf:
                            outputs.append({"output_type": "stream", "name": "stdout", "text": "".join(stdout_buf)})
                            stdout_buf.clear()
                        if stderr_buf:
                            outputs.append({"output_type": "stream", "name": "stderr", "text": "".join(stderr_buf)})
                            stderr_buf.clear()
                        outputs.append({
                            "output_type": "error",
                            "ename": "SystemExit",
                            "evalue": str(se.code),
                            "traceback": [],
                        })
                    except BaseException as e:
                        if stdout_buf:
                            outputs.append({"output_type": "stream", "name": "stdout", "text": "".join(stdout_buf)})
                            stdout_buf.clear()
                        if stderr_buf:
                            outputs.append({"output_type": "stream", "name": "stderr", "text": "".join(stderr_buf)})
                            stderr_buf.clear()
                        tb_lines = traceback.format_exception(type(e), e, e.__traceback__)
                        outputs.append({
                            "output_type": "error",
                            "ename": type(e).__name__,
                            "evalue": str(e),
                            "traceback": tb_lines,
                        })
                    finally:
                        sys.stdout = old_out
                        sys.stderr = old_err

                    if stdout_buf:
                        outputs.insert(0, {"output_type": "stream", "name": "stdout", "text": "".join(stdout_buf)})
                    if stderr_buf:
                        outputs.append({"output_type": "stream", "name": "stderr", "text": "".join(stderr_buf)})

                    tmp_resp = resp_path + ".tmp"
                    with open(tmp_resp, "w", encoding="utf-8") as f:
                        json.dump({"outputs": outputs}, f)
                    os.replace(tmp_resp, resp_path)
            except Exception:
                pass
            time.sleep(0.15)

    t = threading.Thread(target=_rpc_loop, name="youai-http-rpc", daemon=True)
    t.start()

_try_start_youai_daemon()
'''

PTH_LINE = "import os; exec(open('/tmp/_youai_rpc_daemon.py').read()) if os.path.exists('/tmp/_youai_rpc_daemon.py') else None\n"


class ColabHttpRpcClient:
    """Executes Python code on a Colab runtime using pure HTTPS (/api/contents + /api/kernels)."""

    def __init__(self, base_url: str, token: str):
        self.base_url = base_url.rstrip("/")
        self.token = token
        self.headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "X-Colab-Client-Agent": "colab-cli",
            "X-Colab-Runtime-Proxy-Token": self.token,
        }
        self.params = {
            "authuser": "0",
            "colab-runtime-proxy-token": self.token,
        }
        self._bootstrapped = False

    def _contents_req(
        self,
        method: str,
        path: str,
        params: Optional[dict] = None,
        json_data: Optional[dict] = None,
        timeout: float = 30.0,
    ) -> Optional[dict]:
        quoted = quote(path.strip("/"), safe="/")
        url = f"{self.base_url}/api/contents/{quoted}"
        req_params = dict(self.params)
        if params:
            req_params.update(params)
        resp = requests.request(
            method,
            url,
            headers=self.headers,
            params=req_params,
            json=json_data,
            timeout=timeout,
        )
        if resp.status_code == 404:
            return None
        resp.raise_for_status()
        if method == "DELETE" or not resp.text:
            return {}
        return resp.json()

    def _put_text(self, remote_path: str, text: str) -> None:
        b64 = base64.b64encode(text.encode("utf-8")).decode("ascii")
        name = remote_path.strip("/").split("/")[-1]
        payload = {
            "name": name,
            "path": remote_path.strip("/"),
            "type": "file",
            "format": "base64",
            "content": b64,
        }
        self._contents_req("PUT", remote_path, json_data=payload)

    def _get_text(self, remote_path: str) -> Optional[str]:
        data = self._contents_req("GET", remote_path, params={"content": "1"})
        if not data:
            return None
        content = data.get("content", "")
        if data.get("format") == "base64":
            return base64.b64decode(content).decode("utf-8", errors="replace")
        return str(content)

    def ensure_daemon(self) -> None:
        if self._bootstrapped:
            ready = self._get_text("tmp/_youai_rpc_ready")
            if ready:
                return

        ready = self._get_text("tmp/_youai_rpc_ready")
        if ready:
            self._bootstrapped = True
            return

        # 1. Upload daemon script to /tmp/_youai_rpc_daemon.py
        self._put_text("tmp/_youai_rpc_daemon.py", DAEMON_SCRIPT)

        # 2. Discover python3.X dist-packages directories and /etc/python3.X/sitecustomize.py
        target_pths = ["usr/lib/python3/dist-packages/youai_colab_rpc.pth"]
        for base_lib in ["usr/local/lib", "usr/lib"]:
            lib_dir = self._contents_req("GET", base_lib)
            if lib_dir and lib_dir.get("type") == "directory":
                for item in lib_dir.get("content", []):
                    name = item.get("name", "")
                    if name.startswith("python3."):
                        target_pths.append(f"{base_lib}/{name}/dist-packages/youai_colab_rpc.pth")

        for pth_path in target_pths:
            try:
                self._put_text(pth_path, PTH_LINE)
            except Exception as e:
                logger.debug(f"Could not write .pth to {pth_path}: {e}")

        for py_etc in ["etc/python3.12/sitecustomize.py", "etc/python3.13/sitecustomize.py", "etc/python3.11/sitecustomize.py"]:
            try:
                existing = self._get_text(py_etc)
                if existing is not None and "_youai_rpc_daemon" not in existing:
                    self._put_text(py_etc, existing + "\n" + PTH_LINE)
            except Exception:
                pass

        # 3. Spawn a fresh kernel via POST /api/kernels so Python loads youai_colab_rpc.pth
        resp = requests.post(
            f"{self.base_url}/api/kernels",
            headers=self.headers,
            params=self.params,
            json={"name": "python3", "path": "content"},
            timeout=30.0,
        )
        resp.raise_for_status()

        # 4. Wait for /tmp/_youai_rpc_ready
        deadline = time.time() + 25.0
        while time.time() < deadline:
            if self._get_text("tmp/_youai_rpc_ready"):
                self._bootstrapped = True
                return
            time.sleep(0.3)

        raise RuntimeError("Timed out waiting for Colab HTTP RPC daemon to start.")

    def execute_code(
        self,
        code: str,
        output_hook: Optional[Callable[[Dict[str, Any]], None]] = None,
        timeout: Optional[float] = None,
    ) -> List[Dict[str, Any]]:
        self.ensure_daemon()

        req_id = uuid.uuid4().hex[:12]
        stream_path = f"tmp/_youai_rpc_stream_{req_id}.log"
        resp_path = f"tmp/_youai_rpc_resp_{req_id}.json"

        self._put_text(
            "tmp/_youai_rpc_req.json",
            json.dumps({"id": req_id, "code": code}),
        )

        eff_timeout = timeout if (timeout and timeout > 30.0) else 3600.0
        deadline = time.time() + eff_timeout
        stream_offset = 0

        while time.time() < deadline:
            if output_hook:
                stream_text = self._get_text(stream_path)
                if stream_text and len(stream_text) > stream_offset:
                    delta = stream_text[stream_offset:]
                    stream_offset = len(stream_text)
                    output_hook(
                        {"output_type": "stream", "name": "stdout", "text": delta}
                    )

            resp_text = self._get_text(resp_path)
            if resp_text:
                if output_hook:
                    stream_text = self._get_text(stream_path)
                    if stream_text and len(stream_text) > stream_offset:
                        delta = stream_text[stream_offset:]
                        stream_offset = len(stream_text)
                        output_hook(
                            {"output_type": "stream", "name": "stdout", "text": delta}
                        )

                try:
                    self._contents_req("DELETE", resp_path)
                    self._contents_req("DELETE", stream_path)
                except Exception:
                    pass

                data = json.loads(resp_text)
                outputs = data.get("outputs", [])
                if output_hook:
                    for out in outputs:
                        if out.get("output_type") == "error":
                            output_hook(out)
                return outputs

            time.sleep(0.3)

        raise TimeoutError(f"Colab HTTP RPC execution timed out after {eff_timeout}s")
