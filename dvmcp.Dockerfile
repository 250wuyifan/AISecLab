# DVMCP (Damn Vulnerable MCP) 靶场服务
# 10 个 MCP 安全挑战，端口 9001-9010

FROM python:3.10-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    supervisor \
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
    /tmp/dvmcp_challenge10/config \
    /var/log/supervisor

# 初始化状态文件
RUN echo '{"weather_tool_calls": 0}' > /tmp/dvmcp_challenge4/state/state.json

# 创建挑战 3 的示例文件
RUN echo "Welcome to the public directory!" > /tmp/dvmcp_challenge3/public/welcome.txt && \
    echo "This is a public file." > /tmp/dvmcp_challenge3/public/public_file.txt && \
    printf "CONFIDENTIAL: Employee Salary Information\n-----------------------------------------\nCEO: \$1,200,000/year\nCTO: \$950,000/year\nCFO: \$900,000/year\nSenior Engineers: \$180,000-\$250,000/year\nMid-level Engineers: \$120,000-\$170,000/year\nJunior Engineers: \$80,000-\$110,000/year" > /tmp/dvmcp_challenge3/private/employee_salaries.txt

# 创建挑战 10 的示例文件
RUN printf "SYSTEM CONFIGURATION\n-------------------\nCloud Provider: AWS\nRegion: us-west-2\nAPI Keys:\n  - AWS_ACCESS_KEY_ID: AKIA5EXAMPLE12345678\n  - AWS_SECRET_ACCESS_KEY: abcdef1234567890EXAMPLE/abcdefghijklmnopqrst\nS3 Buckets:\n  - customer-data-prod\n  - financial-reports-2025\n  - employee-records-confidential" > /tmp/dvmcp_challenge10/config/system.conf && \
    printf '{\n  "admin_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsIm5hbWUiOiJBZG1pbiBVc2VyIiwicm9sZSI6ImFkbWluIiwiaWF0IjoxNjUxODg0ODAwfQ.8FhJ7Z5KFUEJFoQW2xeUL9_NOzlKB3j8fKvxU_5qB4Y",\n  "service_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJzZXJ2aWNlIiwibmFtZSI6IlNlcnZpY2UgQWNjb3VudCIsInJvbGUiOiJzZXJ2aWNlIiwiaWF0IjoxNjUxODg0ODAwfQ.7y6t5r4e3w2q1z0x9c8v7b6n5m4k3j2h1g0f"\n}' > /tmp/dvmcp_challenge10/config/tokens.json

# 创建 supervisord 配置
RUN printf '[supervisord]\n\
nodaemon=true\n\
user=root\n\
logfile=/var/log/supervisor/supervisord.log\n\
pidfile=/var/run/supervisord.pid\n\
\n\
[program:challenge1]\n\
command=python /app/challenges/easy/challenge1/server_sse.py\n\
stdout_logfile=/var/log/supervisor/challenge1.log\n\
stderr_logfile=/var/log/supervisor/challenge1.err\n\
autostart=true\n\
autorestart=true\n\
\n\
[program:challenge2]\n\
command=python /app/challenges/easy/challenge2/server_sse.py\n\
stdout_logfile=/var/log/supervisor/challenge2.log\n\
stderr_logfile=/var/log/supervisor/challenge2.err\n\
autostart=true\n\
autorestart=true\n\
\n\
[program:challenge3]\n\
command=python /app/challenges/easy/challenge3/server_sse.py\n\
stdout_logfile=/var/log/supervisor/challenge3.log\n\
stderr_logfile=/var/log/supervisor/challenge3.err\n\
autostart=true\n\
autorestart=true\n\
\n\
[program:challenge4]\n\
command=python /app/challenges/medium/challenge4/server_sse.py\n\
stdout_logfile=/var/log/supervisor/challenge4.log\n\
stderr_logfile=/var/log/supervisor/challenge4.err\n\
autostart=true\n\
autorestart=true\n\
\n\
[program:challenge5]\n\
command=python /app/challenges/medium/challenge5/server_sse.py\n\
stdout_logfile=/var/log/supervisor/challenge5.log\n\
stderr_logfile=/var/log/supervisor/challenge5.err\n\
autostart=true\n\
autorestart=true\n\
\n\
[program:challenge6]\n\
command=python /app/challenges/medium/challenge6/server_sse.py\n\
stdout_logfile=/var/log/supervisor/challenge6.log\n\
stderr_logfile=/var/log/supervisor/challenge6.err\n\
autostart=true\n\
autorestart=true\n\
\n\
[program:challenge7]\n\
command=python /app/challenges/medium/challenge7/server_sse.py\n\
stdout_logfile=/var/log/supervisor/challenge7.log\n\
stderr_logfile=/var/log/supervisor/challenge7.err\n\
autostart=true\n\
autorestart=true\n\
\n\
[program:challenge8]\n\
command=python /app/challenges/hard/challenge8/server_sse.py\n\
stdout_logfile=/var/log/supervisor/challenge8.log\n\
stderr_logfile=/var/log/supervisor/challenge8.err\n\
autostart=true\n\
autorestart=true\n\
\n\
[program:challenge9]\n\
command=python /app/challenges/hard/challenge9/server_sse.py\n\
stdout_logfile=/var/log/supervisor/challenge9.log\n\
stderr_logfile=/var/log/supervisor/challenge9.err\n\
autostart=true\n\
autorestart=true\n\
\n\
[program:challenge10]\n\
command=python /app/challenges/hard/challenge10/server_sse.py\n\
stdout_logfile=/var/log/supervisor/challenge10.log\n\
stderr_logfile=/var/log/supervisor/challenge10.err\n\
autostart=true\n\
autorestart=true\n\
' > /etc/supervisor/conf.d/dvmcp.conf

# 暴露端口
EXPOSE 9001 9002 9003 9004 9005 9006 9007 9008 9009 9010

# 使用 supervisord 启动所有服务（支持自动重启）
CMD ["/usr/bin/supervisord", "-c", "/etc/supervisor/conf.d/dvmcp.conf"]
