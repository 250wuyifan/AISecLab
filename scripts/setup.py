#!/usr/bin/env python3
"""
跨平台一键安装脚本
支持 Windows / macOS / Linux
"""
import os
import sys
import subprocess
import platform
from pathlib import Path

# 颜色输出
class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def print_color(msg, color=Colors.GREEN):
    # Windows 需要启用 ANSI
    if platform.system() == 'Windows':
        os.system('')
    print(f"{color}{msg}{Colors.RESET}")

def print_step(step, msg):
    print_color(f"\n[{step}] {msg}", Colors.BLUE + Colors.BOLD)

def print_success(msg):
    print_color(f"✓ {msg}", Colors.GREEN)

def print_warning(msg):
    print_color(f"⚠ {msg}", Colors.YELLOW)

def print_error(msg):
    print_color(f"✗ {msg}", Colors.RED)

def run_command(cmd, check=True, capture=False):
    """执行命令，跨平台兼容"""
    if platform.system() == 'Windows':
        # Windows 使用 shell=True
        result = subprocess.run(cmd, shell=True, check=check, 
                              capture_output=capture, text=True)
    else:
        result = subprocess.run(cmd, shell=True, check=check,
                              capture_output=capture, text=True)
    return result

def check_python_version():
    """检查 Python 版本"""
    print_step("1/5", "检查 Python 版本")
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 9):
        print_error(f"需要 Python 3.9+，当前版本: {version.major}.{version.minor}")
        sys.exit(1)
    print_success(f"Python {version.major}.{version.minor}.{version.micro}")

def check_pip():
    """检查 pip 是否可用"""
    try:
        run_command(f"{sys.executable} -m pip --version", capture=True)
        return True
    except:
        return False

def create_venv():
    """创建虚拟环境（可选）"""
    print_step("2/5", "检查虚拟环境")
    
    # 检查是否已在虚拟环境中
    if sys.prefix != sys.base_prefix:
        print_success(f"已在虚拟环境中: {sys.prefix}")
        return
    
    venv_path = Path("venv")
    if venv_path.exists():
        print_success("虚拟环境已存在")
        return
    
    print_warning("未检测到虚拟环境，建议创建虚拟环境运行（可跳过）")
    
    choice = input("是否创建虚拟环境? [y/N]: ").strip().lower()
    if choice == 'y':
        print("创建虚拟环境...")
        run_command(f"{sys.executable} -m venv venv")
        print_success("虚拟环境已创建")
        
        # 提示激活方式
        if platform.system() == 'Windows':
            print_warning("请运行以下命令激活虚拟环境后重新运行此脚本:")
            print("  .\\venv\\Scripts\\activate")
        else:
            print_warning("请运行以下命令激活虚拟环境后重新运行此脚本:")
            print("  source venv/bin/activate")
        sys.exit(0)

def install_dependencies():
    """安装依赖"""
    print_step("3/5", "安装 Python 依赖")
    
    # 升级 pip
    print("升级 pip...")
    run_command(f"{sys.executable} -m pip install --upgrade pip", check=False)
    
    # 安装依赖
    print("安装项目依赖...")
    result = run_command(f"{sys.executable} -m pip install -r requirements.txt", check=False)
    
    if result.returncode != 0:
        print_warning("部分依赖安装可能失败，尝试继续...")
    else:
        print_success("依赖安装完成")

def init_database():
    """初始化数据库"""
    print_step("4/5", "初始化数据库")
    
    print("执行数据库迁移...")
    run_command(f"{sys.executable} manage.py migrate --noinput")
    print_success("数据库初始化完成")

def create_superuser():
    """创建管理员账号"""
    print_step("5/5", "创建管理员账号")
    
    # 检查是否已存在 admin 用户
    check_cmd = f'{sys.executable} -c "import django; django.setup(); from django.contrib.auth.models import User; print(User.objects.filter(username=\'admin\').exists())"'
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'aisec_playground.settings')
    
    try:
        result = run_command(check_cmd, capture=True)
        if 'True' in result.stdout:
            print_success("管理员账号已存在 (admin/admin)")
            return
    except:
        pass
    
    print("创建管理员账号...")
    run_command(f"{sys.executable} create_superuser.py")
    print_success("管理员账号已创建 (admin/admin)")

def print_summary():
    """打印安装完成信息"""
    print("\n" + "=" * 60)
    print_color("🎉 安装完成！", Colors.GREEN + Colors.BOLD)
    print("=" * 60)
    
    print("\n启动服务：")
    if platform.system() == 'Windows':
        print_color("  python manage.py runserver", Colors.YELLOW)
    else:
        print_color("  python manage.py runserver", Colors.YELLOW)
    
    print("\n访问地址：")
    print_color("  http://127.0.0.1:8000", Colors.BLUE)
    
    print("\n登录账号：")
    print_color("  用户名: admin  密码: admin", Colors.YELLOW)
    
    print("\n" + "=" * 60)
    print_color("📖 更多信息请查看 README.md", Colors.GREEN)
    print("=" * 60 + "\n")

def main():
    print("\n" + "=" * 60)
    print_color("🛡️  AI 安全靶场 - 跨平台安装脚本", Colors.GREEN + Colors.BOLD)
    print_color(f"   系统: {platform.system()} {platform.release()}", Colors.BLUE)
    print("=" * 60)
    
    # 切换到项目根目录
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    os.chdir(project_root)
    print_color(f"项目目录: {project_root}", Colors.BLUE)
    
    try:
        check_python_version()
        create_venv()
        install_dependencies()
        init_database()
        create_superuser()
        print_summary()
    except subprocess.CalledProcessError as e:
        print_error(f"命令执行失败: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n安装已取消")
        sys.exit(1)

if __name__ == "__main__":
    main()
