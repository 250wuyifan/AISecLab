/**
 * AI安全靶场 - 赛博朋克背景动画
 * 创建流动的粒子网络效果
 */

(function() {
    'use strict';

    // 检查是否为暗色主题
    function isDarkTheme() {
        return document.documentElement.getAttribute('data-theme') === 'dark';
    }

    // 只在暗色主题下启用动画
    if (!isDarkTheme()) {
        // 监听主题变化
        const observer = new MutationObserver(function(mutations) {
            mutations.forEach(function(mutation) {
                if (mutation.attributeName === 'data-theme') {
                    if (isDarkTheme()) {
                        initCanvas();
                    } else {
                        destroyCanvas();
                    }
                }
            });
        });
        observer.observe(document.documentElement, { attributes: true });
        return;
    }

    let canvas, ctx, particles, animationId;
    let width, height;
    
    // 配置参数
    const config = {
        particleCount: 50,
        particleSize: 2,
        lineDistance: 150,
        particleSpeed: 0.3,
        colors: {
            particle: 'rgba(0, 245, 255, 0.6)',
            line: 'rgba(99, 102, 241, 0.15)',
            glow: 'rgba(0, 245, 255, 0.3)'
        }
    };

    class Particle {
        constructor() {
            this.reset();
        }

        reset() {
            this.x = Math.random() * width;
            this.y = Math.random() * height;
            this.vx = (Math.random() - 0.5) * config.particleSpeed;
            this.vy = (Math.random() - 0.5) * config.particleSpeed;
            this.size = Math.random() * config.particleSize + 1;
            this.alpha = Math.random() * 0.5 + 0.3;
        }

        update() {
            this.x += this.vx;
            this.y += this.vy;

            // 边界检测
            if (this.x < 0 || this.x > width) this.vx *= -1;
            if (this.y < 0 || this.y > height) this.vy *= -1;

            // 保持在边界内
            this.x = Math.max(0, Math.min(width, this.x));
            this.y = Math.max(0, Math.min(height, this.y));
        }

        draw() {
            ctx.beginPath();
            ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
            ctx.fillStyle = config.colors.particle;
            ctx.globalAlpha = this.alpha;
            ctx.fill();
            
            // 添加发光效果
            ctx.shadowBlur = 10;
            ctx.shadowColor = config.colors.glow;
            ctx.fill();
            ctx.shadowBlur = 0;
            ctx.globalAlpha = 1;
        }
    }

    function initCanvas() {
        // 如果已存在则先销毁
        destroyCanvas();

        canvas = document.createElement('canvas');
        canvas.id = 'bg-canvas';
        canvas.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            pointer-events: none;
            z-index: -1;
            opacity: 0;
            transition: opacity 0.5s ease;
        `;
        document.body.appendChild(canvas);

        ctx = canvas.getContext('2d');
        
        resize();
        initParticles();
        
        // 淡入效果
        setTimeout(() => {
            canvas.style.opacity = '1';
        }, 100);

        animate();
        
        window.addEventListener('resize', resize);
    }

    function destroyCanvas() {
        if (animationId) {
            cancelAnimationFrame(animationId);
            animationId = null;
        }
        if (canvas) {
            canvas.remove();
            canvas = null;
            ctx = null;
        }
        particles = null;
        window.removeEventListener('resize', resize);
    }

    function resize() {
        if (!canvas) return;
        width = window.innerWidth;
        height = window.innerHeight;
        canvas.width = width;
        canvas.height = height;
    }

    function initParticles() {
        particles = [];
        for (let i = 0; i < config.particleCount; i++) {
            particles.push(new Particle());
        }
    }

    function drawLines() {
        for (let i = 0; i < particles.length; i++) {
            for (let j = i + 1; j < particles.length; j++) {
                const dx = particles[i].x - particles[j].x;
                const dy = particles[i].y - particles[j].y;
                const distance = Math.sqrt(dx * dx + dy * dy);

                if (distance < config.lineDistance) {
                    const alpha = (1 - distance / config.lineDistance) * 0.3;
                    ctx.beginPath();
                    ctx.moveTo(particles[i].x, particles[i].y);
                    ctx.lineTo(particles[j].x, particles[j].y);
                    ctx.strokeStyle = config.colors.line;
                    ctx.globalAlpha = alpha;
                    ctx.lineWidth = 1;
                    ctx.stroke();
                    ctx.globalAlpha = 1;
                }
            }
        }
    }

    function animate() {
        if (!ctx || !particles) return;
        
        ctx.clearRect(0, 0, width, height);

        // 绘制连接线
        drawLines();

        // 更新和绘制粒子
        particles.forEach(particle => {
            particle.update();
            particle.draw();
        });

        animationId = requestAnimationFrame(animate);
    }

    // 监听主题变化
    const observer = new MutationObserver(function(mutations) {
        mutations.forEach(function(mutation) {
            if (mutation.attributeName === 'data-theme') {
                if (isDarkTheme()) {
                    initCanvas();
                } else {
                    destroyCanvas();
                }
            }
        });
    });
    observer.observe(document.documentElement, { attributes: true });

    // 初始化
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initCanvas);
    } else {
        initCanvas();
    }

    // 页面可见性变化时暂停/恢复动画
    document.addEventListener('visibilitychange', function() {
        if (document.hidden) {
            if (animationId) {
                cancelAnimationFrame(animationId);
                animationId = null;
            }
        } else if (isDarkTheme() && canvas && !animationId) {
            animate();
        }
    });
})();
