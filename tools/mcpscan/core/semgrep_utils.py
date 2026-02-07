import json, subprocess, tempfile, logging, shutil, sys
from pathlib import Path
from typing import Dict, List, Any

def find_semgrep() -> str:
    """
    查找 semgrep 可执行文件路径
    跨平台兼容：Windows / macOS / Linux
    """
    # 优先使用 shutil.which 查找 PATH 中的 semgrep
    semgrep_path = shutil.which("semgrep")
    if semgrep_path:
        return semgrep_path
    
    # Windows 上可能需要查找 semgrep.exe 或 semgrep.cmd
    if sys.platform == "win32":
        for suffix in [".exe", ".cmd", ".bat"]:
            path = shutil.which(f"semgrep{suffix}")
            if path:
                return path
    
    # 如果找不到，返回 "semgrep" 并让系统报错
    return "semgrep"

def run_semgrep(code_root: Path, config: Path, results_file: Path) -> List[Dict[str, Any]]:
    """
    运行 Semgrep 扫描
    跨平台兼容
    """
    semgrep_bin = find_semgrep()
    cmd = [semgrep_bin, "--config", str(config), "--json", "--output", str(results_file), str(code_root)]
    logging.info("▶️  Running: %s", " ".join(cmd))
    
    try:
        completed = subprocess.run(
            cmd, 
            text=True, 
            capture_output=True,
            # Windows 上需要设置 shell=False 并正确处理路径
            shell=False,
            # 设置编码避免 Windows 上的编码问题
            encoding='utf-8',
            errors='replace'
        )
    except FileNotFoundError:
        raise RuntimeError(
            "Semgrep 未安装或不在 PATH 中。\n"
            "安装方式：pip install semgrep\n"
            "或访问：https://semgrep.dev/docs/getting-started/"
        )
    
    if completed.returncode not in (0, 1):
        logging.error(completed.stderr)
        raise RuntimeError(f"Semgrep failed: {completed.stderr}")
    
    return json.loads(results_file.read_text(encoding='utf-8')).get("results", [])
