# DVMCP (Damn Vulnerable MCP) 靶场服务
# 10 个 MCP 安全挑战，端口 9001-9010

FROM python:3.10-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    && rm -rf /var/lib/apt/lists/*

# 克隆 DVMCP 项目（中文版）
RUN git clone --depth 1 https://github.com/250wuyifan/damn-vulnerable-MCP-server-CN.git .

# 安装 Python 依赖
RUN pip install --no-cache-dir -r requirements.txt

# 创建挑战所需的目录和文件
RUN mkdir -p /tmp/dvmcp_challenge3/public /tmp/dvmcp_challenge3/private \
    /tmp/dvmcp_challenge4/state \
    /tmp/dvmcp_challenge6/user_uploads \
    /tmp/dvmcp_challenge8/sensitive \
    /tmp/dvmcp_challenge10/config

# 初始化状态文件
RUN echo '{"weather_tool_calls": 0}' > /tmp/dvmcp_challenge4/state/state.json

# 创建挑战 3 的示例文件
RUN echo "Welcome to the public directory!" > /tmp/dvmcp_challenge3/public/welcome.txt && \
    echo "This is a public file." > /tmp/dvmcp_challenge3/public/public_file.txt && \
    echo "CONFIDENTIAL: Employee Salary Information\n-----------------------------------------\nCEO: \$1,200,000/year\nCTO: \$950,000/year\nCFO: \$900,000/year" > /tmp/dvmcp_challenge3/private/employee_salaries.txt

# 创建挑战 10 的示例文件
RUN echo "SYSTEM CONFIGURATION\n-------------------\nCloud Provider: AWS\nRegion: us-west-2\nAPI Keys:\n  - AWS_ACCESS_KEY_ID: AKIA5EXAMPLE12345678" > /tmp/dvmcp_challenge10/config/system.conf && \
    echo '{"admin_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."}' > /tmp/dvmcp_challenge10/config/tokens.json

# 暴露端口
EXPOSE 9001 9002 9003 9004 9005 9006 9007 9008 9009 9010

# 创建启动脚本
RUN echo '#!/bin/bash\n\
python challenges/easy/challenge1/server_sse.py &\n\
python challenges/easy/challenge2/server_sse.py &\n\
python challenges/easy/challenge3/server_sse.py &\n\
python challenges/medium/challenge4/server_sse.py &\n\
python challenges/medium/challenge5/server_sse.py &\n\
python challenges/medium/challenge6/server_sse.py &\n\
python challenges/medium/challenge7/server_sse.py &\n\
python challenges/hard/challenge8/server_sse.py &\n\
python challenges/hard/challenge9/server_sse.py &\n\
python challenges/hard/challenge10/server_sse.py &\n\
wait' > /app/start.sh && chmod +x /app/start.sh

CMD ["/app/start.sh"]
