from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.utils.html import escape
import re
import markdown as mdlib
from django.utils.safestring import mark_safe
import json
from .models import Category, Topic
from .forms import TopicForm, CategoryForm


def _preprocess_markdown(text: str) -> str:
    """
    轻量预处理：
    - 将裸 URL 包一层 <...>，让 Markdown 自动生成可点击链接。
      例如：链接：https://example.com -> 链接：<https://example.com>
    - 排除已经在 Markdown 链接/图片语法中的 URL：[text](url) 或 ![alt](url)
    """
    if not text:
        return ""
    # 排除：已有 <、在 ]( 后面的（链接/图片）、在 )后面的
    # 只处理独立的裸 URL
    return re.sub(r"(?<![<\(])(https?://[^\s>\)\]]+)(?![^\[]*\])", r"<\1>", text)

def index(request):
    categories = Category.objects.prefetch_related('topics').all()
    latest_topics = (
        Topic.objects.select_related('category')
        .order_by('-updated_at')[:8]
    )
    
    # 获取靶场统计数据
    lab_stats = {
        'total_labs': 0,
        'total_categories': 0,
        'completed_count': 0,
        'favorites_count': 0,
        'completion_rate': 0,
        'completed_slugs': [],
        'favorite_slugs': [],
    }
    
    try:
        from playground.views import _build_sidebar_context
        from playground.models import LabProgress, LabFavorite
        
        ctx = _build_sidebar_context(active_item_id="")
        lab_groups = ctx.get("lab_groups", [])
        
        # 统计总数（对所有用户可见）
        lab_stats['total_labs'] = sum(len(g.items) for g in lab_groups)
        lab_stats['total_categories'] = len(lab_groups)
        
        # 用户进度（仅登录用户）
        if request.user.is_authenticated:
            lab_stats['completed_count'] = LabProgress.objects.filter(
                user=request.user, completed=True
            ).count()
            lab_stats['favorites_count'] = LabFavorite.objects.filter(
                user=request.user
            ).count()
            lab_stats['completed_slugs'] = list(
                LabProgress.objects.filter(user=request.user, completed=True)
                .values_list("lab_slug", flat=True)
            )
            lab_stats['favorite_slugs'] = list(
                LabFavorite.objects.filter(user=request.user)
                .values_list("lab_slug", flat=True)
            )
            if lab_stats['total_labs'] > 0:
                lab_stats['completion_rate'] = round(
                    lab_stats['completed_count'] / lab_stats['total_labs'] * 100, 1
                )
    except Exception:
        pass
    
    context = {
        'categories': categories,
        'current_topic': None,
        'latest_topics': latest_topics,
        'lab_stats': lab_stats,
    }
    return render(request, 'learning/index.html', context)

@login_required
def topic_create(request):
    if request.method == 'POST':
        form = TopicForm(request.POST, request.FILES)
        if form.is_valid():
            topic = form.save(commit=False)
            topic.author = request.user
            # 优先使用自填作者名，否则默认当前用户
            if form.cleaned_data.get('author_name'):
                topic.author_name = form.cleaned_data['author_name']
            else:
                topic.author_name = request.user.username if request.user.is_authenticated else ''
            
            # 处理 Markdown 文件上传
            uploaded_file = request.FILES.get('markdown_file')
            if uploaded_file:
                try:
                    content = uploaded_file.read().decode('utf-8')
                    topic.content = content
                    
                    # 如果标题为空，尝试从文件内容第一行提取
                    if not topic.title:
                        lines = content.split('\n')
                        for line in lines:
                            if line.startswith('# '):
                                topic.title = line[2:].strip()
                                break
                        # 如果还是没标题，用文件名
                        if not topic.title:
                            topic.title = uploaded_file.name.replace('.md', '')
                except Exception as e:
                    form.add_error('markdown_file', f'文件读取失败: {str(e)}')
                    return render(request, 'learning/topic_form.html', {'form': form})
            
            topic.save()
            messages.success(request, '文章已成功创建！')
            return redirect('learning:topic_detail', topic.id)
    else:
        form = TopicForm()
    
    return render(request, 'learning/topic_form.html', {'form': form})

def topic_detail(request, topic_id):
    categories = Category.objects.prefetch_related('topics').all()
    topic = get_object_or_404(Topic, id=topic_id)
    latest_topics = (
        Topic.objects.select_related('category')
        .order_by('-updated_at')[:8]
    )

    # 渲染 Markdown + 生成 TOC（标题目录 & 自动锚点）
    # 额外启用 sane_lists，让“有缩进/混合段落”的列表更稳定。
    md = mdlib.Markdown(
        extensions=['fenced_code', 'codehilite', 'tables', 'toc', 'sane_lists', 'smarty'],
        extension_configs={
            'toc': {
                'permalink': True,
                'permalink_title': '复制链接',
            }
        }
    )
    rendered_content = md.convert(_preprocess_markdown(topic.content or ""))
    toc_html = md.toc or ""

    # 上一篇/下一篇（同一分类内，按 id 顺序）
    prev_topic = (
        Topic.objects.filter(category_id=topic.category_id, id__lt=topic.id)
        .order_by('-id')
        .first()
    )
    next_topic = (
        Topic.objects.filter(category_id=topic.category_id, id__gt=topic.id)
        .order_by('id')
        .first()
    )
    context = {
        'categories': categories,
        'current_topic': topic,
        'prev_topic': prev_topic,
        'next_topic': next_topic,
        'rendered_content': mark_safe(rendered_content),
        'toc_html': mark_safe(toc_html),
        'latest_topics': latest_topics,
    }
    return render(request, 'learning/index.html', context)

@login_required
def topic_update(request, topic_id):
    topic = get_object_or_404(Topic, id=topic_id)
    
    # 权限检查：只有作者或管理员可以编辑
    if topic.author != request.user and not request.user.is_staff:
        messages.error(request, '您没有权限编辑此文章。')
        return redirect('learning:topic_detail', topic_id=topic.id)
    
    if request.method == 'POST':
        form = TopicForm(request.POST, request.FILES, instance=topic)
        if form.is_valid():
            updated_topic = form.save(commit=False)
            if form.cleaned_data.get('author_name'):
                updated_topic.author_name = form.cleaned_data['author_name']
            else:
                updated_topic.author_name = request.user.username if request.user.is_authenticated else ''
            
            # 处理 Markdown 文件上传
            uploaded_file = request.FILES.get('markdown_file')
            if uploaded_file:
                try:
                    content = uploaded_file.read().decode('utf-8')
                    updated_topic.content = content
                    
                    # 如果标题为空，尝试从文件内容第一行提取
                    if not updated_topic.title:
                        lines = content.split('\n')
                        for line in lines:
                            if line.startswith('# '):
                                updated_topic.title = line[2:].strip()
                                break
                        # 如果还是没标题，用文件名
                        if not updated_topic.title:
                            updated_topic.title = uploaded_file.name.replace('.md', '')
                except Exception as e:
                    form.add_error('markdown_file', f'文件读取失败: {str(e)}')
                    return render(request, 'learning/topic_form.html', {
                        'form': form,
                        'topic': topic,
                        'is_edit': True
                    })
            
            # 保存到数据库
            updated_topic.save()
            messages.success(request, '文章已成功更新！')
            return redirect('learning:topic_detail', topic_id=updated_topic.id)
    else:
        form = TopicForm(instance=topic)
    
    return render(request, 'learning/topic_form.html', {
        'form': form,
        'topic': topic,
        'is_edit': True
    })

@login_required
def topic_delete(request, topic_id):
    topic = get_object_or_404(Topic, id=topic_id)
    
    # 权限检查：只有作者或管理员可以删除
    if topic.author != request.user and not request.user.is_staff:
        messages.error(request, '您没有权限删除此文章。')
        return redirect('learning:topic_detail', topic_id=topic.id)
    
    if request.method == 'POST':
        topic.delete()
        messages.success(request, '文章已成功删除！')
        return redirect('learning:index')
    
    # GET 请求时显示确认页面
    categories = Category.objects.prefetch_related('topics').all()
    context = {
        'categories': categories,
        'current_topic': topic,
        'show_delete_confirm': True
    }
    return render(request, 'learning/index.html', context)


def search(request):
    q = (request.GET.get('q') or '').strip()
    categories = Category.objects.prefetch_related('topics').all()

    results = Topic.objects.none()
    if q:
        results = (
            Topic.objects.select_related('category')
            .filter(
                Q(title__icontains=q)
                | Q(content__icontains=q)
                | Q(category__name__icontains=q)
            )
            .order_by('-updated_at')[:50]
        )

    def _strip_markdown(text: str) -> str:
        """非常轻量的 Markdown 清理，用于搜索摘要展示（不追求完全准确）。"""
        if not text:
            return ""
        # 去掉代码块/行内代码的反引号
        text = re.sub(r"```[\s\S]*?```", " ", text)
        text = re.sub(r"`([^`]+)`", r"\1", text)
        # 链接/图片: ![alt](url) / [text](url)
        text = re.sub(r"!\[([^\]]*)\]\([^)]+\)", r"\1", text)
        text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
        # 标题/加粗/斜体等符号
        text = re.sub(r"[*_~#>]+", " ", text)
        # 多空白压缩
        text = re.sub(r"\s+", " ", text).strip()
        return text

    def _make_snippet(title: str, category_name: str, content: str, query: str, radius: int = 60) -> str:
        """生成高亮摘要 HTML（已 escape），优先从 content 命中处截取。"""
        if not query:
            return ""
        hay = _strip_markdown(content)
        q_re = re.compile(re.escape(query), re.IGNORECASE)
        m = q_re.search(hay)
        if not m:
            # 如果内容没命中，就给个开头摘要
            base = hay[:140]
            return escape(base) + ("…" if len(hay) > 140 else "")

        start = max(0, m.start() - radius)
        end = min(len(hay), m.end() + radius)
        prefix = "…" if start > 0 else ""
        suffix = "…" if end < len(hay) else ""
        piece = hay[start:end]
        # 高亮：先 escape，再替换匹配为 <mark>
        escaped_piece = escape(piece)
        highlighted = q_re.sub(lambda mm: f"<mark>{escape(mm.group(0))}</mark>", escaped_piece)
        return prefix + highlighted + suffix

    results_with_snippet = []
    for t in results:
        results_with_snippet.append({
            "obj": t,
            "snippet": _make_snippet(t.title, t.category.name if t.category else "", t.content, q),
        })

    return render(request, 'learning/search_results.html', {
        'categories': categories,
        'q': q,
        'results': results_with_snippet,
    })


@login_required
def knowledge_panel(request):
    """
    类“幕布”的知识结构面板：
    AI安全靶场 -> 分类 -> 文章
    支持在面板内创建分类/文章节点，编辑跳转到现有编辑页。
    """
    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'create_category':
            c_form = CategoryForm(request.POST)
            if c_form.is_valid():
                c_form.save()
                messages.success(request, '分类已创建')
                return redirect('learning:knowledge_panel')
            else:
                messages.error(request, '分类创建失败，请检查填写')

        elif action == 'create_topic':
            t_form = TopicForm(request.POST, request.FILES)
            if t_form.is_valid():
                topic = t_form.save(commit=False)
                topic.author = request.user
                topic.author_name = (t_form.cleaned_data.get('author_name') or request.user.username)

                uploaded_file = request.FILES.get('markdown_file')
                if uploaded_file:
                    try:
                        content = uploaded_file.read().decode('utf-8')
                        topic.content = content
                        if not topic.title:
                            # 尝试从 H1 提取
                            for line in content.split('\n'):
                                if line.startswith('# '):
                                    topic.title = line[2:].strip()
                                    break
                            if not topic.title:
                                topic.title = uploaded_file.name.replace('.md', '')
                    except Exception as e:
                        messages.error(request, f'Markdown 文件读取失败: {str(e)}')
                        return redirect('learning:knowledge_panel')

                topic.save()
                messages.success(request, '文章节点已创建')
                # 大纲视图：创建后留在面板，不自动跳到编辑页
                return redirect('learning:knowledge_panel')
            else:
                messages.error(request, '文章创建失败：请填写内容或上传 Markdown 文件')

        elif action == 'delete_topic':
            topic_id = request.POST.get('topic_id')
            try:
                t = Topic.objects.get(id=topic_id)
                t.delete()
                messages.success(request, '文章已删除')
            except Topic.DoesNotExist:
                messages.error(request, '文章不存在或已删除')
            return redirect('learning:knowledge_panel')

        elif action == 'edit_category':
            cat_id = request.POST.get('category_id')
            try:
                cat = Category.objects.get(id=cat_id)
                cat.name = request.POST.get('name', cat.name)
                cat.description = request.POST.get('description', cat.description)
                cat.save()
                messages.success(request, '分类已更新')
            except Category.DoesNotExist:
                messages.error(request, '分类不存在')
            return redirect('learning:knowledge_panel')

        elif action == 'delete_category':
            cat_id = request.POST.get('category_id')
            try:
                cat = Category.objects.get(id=cat_id)
                cat.delete()
                messages.success(request, '分类已删除')
            except Category.DoesNotExist:
                messages.error(request, '分类不存在或已删除')
            return redirect('learning:knowledge_panel')

        else:
            messages.error(request, '未知操作')

    categories = Category.objects.prefetch_related('topics').all().order_by('id')
    embed = (request.GET.get('embed') == '1')
    return render(request, 'learning/panel.html', {
        'categories': categories,
        'category_form': CategoryForm(),
        'topic_form': TopicForm(),
        'embed': embed,
    })


@login_required
def knowledge_panel_mindmap(request):
    """
    思维导图式知识面板（带连线，左->右展开）。
    """
    # 复用与 /panel/ 一致的创建逻辑（简化：仍用同样的 action）
    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'create_category':
            c_form = CategoryForm(request.POST)
            if c_form.is_valid():
                c_form.save()
                messages.success(request, '分类已创建')
                return redirect('learning:knowledge_panel_mindmap')
            messages.error(request, '分类创建失败，请检查填写')

        elif action == 'create_topic':
            t_form = TopicForm(request.POST, request.FILES)
            if t_form.is_valid():
                topic = t_form.save(commit=False)
                topic.author = request.user
                topic.author_name = (t_form.cleaned_data.get('author_name') or request.user.username)

                uploaded_file = request.FILES.get('markdown_file')
                if uploaded_file:
                    try:
                        content = uploaded_file.read().decode('utf-8')
                        topic.content = content
                        if not topic.title:
                            for line in content.split('\n'):
                                if line.startswith('# '):
                                    topic.title = line[2:].strip()
                                    break
                            if not topic.title:
                                topic.title = uploaded_file.name.replace('.md', '')
                    except Exception as e:
                        messages.error(request, f'Markdown 文件读取失败: {str(e)}')
                        return redirect('learning:knowledge_panel_mindmap')

                topic.save()
                messages.success(request, '文章节点已创建')
                return redirect('learning:topic_update', topic_id=topic.id)

            messages.error(request, '文章创建失败：请填写内容或上传 Markdown 文件')

        else:
            messages.error(request, '未知操作')

    categories = Category.objects.prefetch_related('topics').all().order_by('id')

    # jsMind 数据结构（node_tree），强制全部向右展开
    root = {
        "id": "root",
        "topic": "AI安全靶场",
        "expanded": True,
        "direction": "right",
        "children": [],
    }
    for c in categories:
        cat_node = {
            "id": f"cat-{c.id}",
            "topic": c.name,
            "direction": "right",
            "expanded": True,
            "kind": "category",
            "category_id": c.id,
            "children": [],
        }
        for t in c.topics.all():
            cat_node["children"].append({
                "id": f"topic-{t.id}",
                "topic": t.title,
                "direction": "right",
                "expanded": True,
                "kind": "topic",
                "topic_id": t.id,
                "url": f"/topic/{t.id}/",
                "edit_url": f"/topic/{t.id}/edit/",
            })
        root["children"].append(cat_node)

    mind = {
        "meta": {"name": "aisec", "author": "aisec", "version": "1.0"},
        "format": "node_tree",
        "data": root,
    }

    return render(request, 'learning/panel_mindmap.html', {
        "categories": categories,
        "category_form": CategoryForm(),
        "topic_form": TopicForm(),
        "mind_json": json.dumps(mind, ensure_ascii=False),
    })
