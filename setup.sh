#!/bin/bash
#
# AI 安全靶场 - Linux/macOS 一键安装脚本
#

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color
BOLD='\033[1m'

print_step() {
    echo -e "\n${BLUE}${BOLD}[$1]${NC} $2"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

echo ""
echo "============================================================"
echo -e "${GREEN}${BOLD}  🛡️  AI 安全靶场 - Linux/macOS 一键安装${NC}"
echo "============================================================"
echo ""

# 检测系统
OS=$(uname -s)
echo -e "${BLUE}系统: $OS$(NC)"

# 检查 Python
print_step "1/5" "检查 Python 版本"
if command -v python3 &> /dev/null; then
    PYTHON=python3
elif command -v python &> /dev/null; then
    PYTHON=python
else
    print_error "未找到 Python，请先安装 Python 3.9+"
    exit 1
fi

PY_VERSION=$($PYTHON --version 2>&1)
print_success "$PY_VERSION"

# 检查虚拟环境
print_step "2/5" "检查虚拟环境"
if [ -n "$VIRTUAL_ENV" ]; then
    print_success "已在虚拟环境中: $VIRTUAL_ENV"
elif [ -d "venv" ]; then
    print_success "虚拟环境已存在"
else
    print_warning "未检测到虚拟环境，建议创建虚拟环境运行"
    read -p "是否创建虚拟环境? [y/N]: " choice
    if [[ "$choice" =~ ^[Yy]$ ]]; then
        echo "创建虚拟环境..."
        $PYTHON -m venv venv
        print_success "虚拟环境已创建"
        echo ""
        print_warning "请运行以下命令激活虚拟环境后重新运行此脚本:"
        echo "  source venv/bin/activate"
        exit 0
    fi
fi

# 安装依赖
print_step "3/5" "安装 Python 依赖"
echo "升级 pip..."
$PYTHON -m pip install --upgrade pip
echo "安装项目依赖..."
$PYTHON -m pip install -r requirements.txt
print_success "依赖安装完成"

# 初始化数据库
print_step "4/5" "初始化数据库"
$PYTHON manage.py migrate --noinput
print_success "数据库初始化完成"

# 创建管理员
print_step "5/5" "创建管理员账号"
$PYTHON create_superuser.py
print_success "管理员账号已创建 (admin/admin)"

echo ""
echo "============================================================"
echo -e "${GREEN}${BOLD}  🎉 安装完成！${NC}"
echo "============================================================"
echo ""
echo "  启动服务：$PYTHON manage.py runserver"
echo "  访问地址：http://127.0.0.1:8000"
echo "  登录账号：admin / admin"
echo ""
echo "============================================================"
echo ""
