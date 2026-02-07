from pathlib import Path
from typing import Optional
import typer
from rich.console import Console
from rich.panel import Panel

from mcpscan import __version__, BANNER
from mcpscan.core.runner import run_scan

app = typer.Typer(add_completion=False, rich_markup_mode="rich")
console = Console()


@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    version: bool = typer.Option(False, "--version", "-V", help="Show version and exit"),
):
    """
    🛰️  MCPScan — MCP 多阶段安全扫描器 (多 LLM 支持版)
    """
    if version:
        console.print(f"[bold cyan]mcpscan[/] {__version__}")
        raise typer.Exit()

    if ctx.invoked_subcommand is None:
        console.print(Panel.fit(BANNER, style="bold magenta"))
        console.print(
            "[bold]支持的 LLM Provider:[/] deepseek, siliconflow, ollama, openai, custom\n"
            "[bold]Try:[/] mcpscan scan --help"
        )
        raise typer.Exit()


@app.command()
def scan(
    code: str = typer.Argument(..., help="本地路径或 GitHub URL"),
    out: Path = typer.Option(
        "triage_report.json", "--out", "-o", help="输出结果文件（JSON）"
    ),
    save: bool = typer.Option(
        False,
        "--save/--no-save",
        help="是否将扫描结果保存到文件（默认不保存）",
    ),
    monitor_desc: bool = typer.Option(
        True,
        "--monitor-desc/--no-monitor-desc",
        help="是否执行 metadata 描述字段的安全监测（默认开启）",
    ),
    monitor_code: bool = typer.Option(
        True,
        "--monitor-code/--no-monitor-code",
        help="是否执行代码层面风险扫描与跨文件流提取（默认开启）",
    ),
    # ── LLM 配置参数 ──
    llm_provider: Optional[str] = typer.Option(
        None,
        "--llm-provider",
        help="LLM Provider: deepseek, siliconflow, ollama, openai, custom (默认自动检测)",
    ),
    llm_model: Optional[str] = typer.Option(
        None,
        "--llm-model",
        help="LLM 模型名称 (如: deepseek-chat, Qwen/Qwen2.5-7B-Instruct, qwen2.5:7b)",
    ),
    llm_api_key: Optional[str] = typer.Option(
        None,
        "--llm-api-key",
        help="LLM API Key (也可通过环境变量设置)",
    ),
    llm_base_url: Optional[str] = typer.Option(
        None,
        "--llm-base-url",
        help="LLM API Base URL (如: http://localhost:11434/v1)",
    ),
):
    """
    🚀 对目标仓库执行 Semgrep + LLM 两阶段安全扫描

    支持多种 LLM 后端:
    - deepseek: DeepSeek API (需 DEEPSEEK_API_KEY)
    - siliconflow: 硅基流动 API (需 SILICONFLOW_API_KEY)
    - ollama: 本地 Ollama (无需 API Key)
    - openai: OpenAI API (需 OPENAI_API_KEY)
    - custom: 任意 OpenAI 兼容 API (需 LLM_API_KEY + LLM_BASE_URL)
    """
    output_path = out if save else None
    run_scan(
        code,
        output_path,
        monitor_desc=monitor_desc,
        monitor_code=monitor_code,
        llm_provider=llm_provider,
        llm_model=llm_model,
        llm_api_key=llm_api_key,
        llm_base_url=llm_base_url,
    )


@app.command()
def rules():
    """打印内置 Semgrep 规则集所在目录（可复制后自定义）"""
    from importlib.resources import files

    console.print(str(files("mcpscan") / "rules"), style="green")


@app.command()
def providers():
    """列出支持的 LLM Provider 及其配置"""
    from mcpscan.core.llm_bridge import PROVIDER_PRESETS
    from rich.table import Table
    import os

    table = Table(title="支持的 LLM Provider", show_header=True, header_style="bold blue")
    table.add_column("Provider", style="cyan")
    table.add_column("Base URL")
    table.add_column("Default Model")
    table.add_column("Env Key")
    table.add_column("Status")

    for name, preset in PROVIDER_PRESETS.items():
        env_key = preset.get("env_key")
        has_key = "✅" if (env_key and os.getenv(env_key)) or name == "ollama" else "❌"
        table.add_row(
            name,
            preset.get("base_url") or "(需手动设置)",
            preset.get("default_model") or "(需手动设置)",
            env_key or "(无需)",
            has_key,
        )

    console.print(table)
    console.print("\n[bold]示例:[/]")
    console.print("  # 使用硅基流动")
    console.print('  export SILICONFLOW_API_KEY="sk-xxx"')
    console.print("  mcpscan scan ./repo --llm-provider siliconflow")
    console.print("")
    console.print("  # 使用本地 Ollama")
    console.print("  mcpscan scan ./repo --llm-provider ollama --llm-model qwen2.5:7b")
    console.print("")
    console.print("  # 使用自定义 API")
    console.print('  export LLM_API_KEY="sk-xxx"')
    console.print("  mcpscan scan ./repo --llm-provider custom --llm-base-url http://my-api/v1 --llm-model my-model")


if __name__ == "__main__":
    app()
