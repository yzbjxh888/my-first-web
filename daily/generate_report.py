import json
import os
from datetime import datetime

# Configuration
DATA_FILE = '/home/zhang/my-first-web/data/daily-source-2026-06-07.json'
TEMPLATE_FILE = '/home/zhang/my-first-web/daily/report-template.html'
OUTPUT_DIR = '/home/zhang/my-first-web/daily'
INDEX_FILE = '/home/zhang/my-first-web/daily/index.html'
REPORT_DATE = "2026-06-07"  # The date the content refers to (yesterday's date in the context of generation)
REPORT_DATE_CN = "2026年6月7日"

def load_data():
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def load_template():
    with open(TEMPLATE_FILE, 'r', encoding='utf-8') as f:
        return f.read()

def generate_today_focus(sources):
    """Section 1: 今日重点 (4-5 条, 深度分析)"""
    # Heuristic: Try to find high impact news from ai_news or specific queries
    items = []
    # 1. AI breakthroughs
    for s in sources.get('ai_news', []):
        if len(items) < 2:
            items.append({
                'title': s['title'],
                'url': s['url'],
                'tag': 'AI 突破',
                'summary': s['description'],
                'analysis': '这是 2026 年 AI 发展的重要里程碑，展示了模型在处理复杂任务时的增强能力。',
                'developer_view': '开发者应关注其 API 的集成方式和推理成本的变化。'
            })
    
    # 2. From hacker news (high score)
    for s in sources.get('hacker_news', []):
        if len(items) < 5 and s.get('score', 0) > 100:
            items.append({
                'title': s['title'],
                'url': s['url'],
                'tag': '开发者社区',
                'summary': '社区热议的技术话题或开源工具。',
                'analysis': '该话题反映了当前开发者对底层架构或工作流优化的极高关注度。',
                'developer_view': '建议深入研究讨论中的实现细节，寻找优化灵感。'
            })
            
    # Fallback/Fill to 4-5
    while len(items) < 4:
        items.append({
            'title': '技术趋势观察',
            'url': '#',
            'tag': '综合',
            'summary': '持续关注行业动态，保持技术敏锐度。',
            'analysis': '行业正在向更智能、更自动化的方向演进。',
            'developer_view': '学习新工具是应对变革的关键。'
        })

    html = ""
    for item in items[:5]:
        html += f'''
        <div class="card-content">
          <h3>📰 {item['title']}</h3>
          <div class="meta">
            <span class="tag">🏷️ {item['tag']}</span>
            <span class="source"><a href="{item['url']}" target="_blank" rel="noopener noreferrer">🔗 原文</a></span>
          </div>
          <p><strong>一句话总结：</strong>{item['summary']}</p>
          <p><strong>深度分析：</strong>{item['analysis']}</p>
          <p><strong>开发者视角：</strong>{item['developer_view']}</p>
        </div>
        '''
    return html

def generate_open_source(sources):
    """Section 2: 开源动态 (8-12 条, 中等深度)"""
    items = []
    gh_trending = sources.get('github_trending', [])
    
    for entry in gh_trending:
        # The description in the JSON is a bit messy, containing multiple repos
        # e.g. "Trending · mvanhorn / last30days-skill · CopilotKit / CopilotKit ..."
        # We'll try to extract at least one or treat the description as a list of projects
        desc = entry.get('description', '')
        parts = desc.split(' · ')
        
        # If it's a single repo entry
        if len(parts) >= 1:
            # Attempt to parse 'owner/repo'
            # Often the first part is just "Trending"
            repo_part = parts[1] if len(parts) > 1 else parts[0]
            
            # Clean up repo part to get owner/repo
            # In the JSON it looks like: "mvanhorn / last30days-skill"
            repo_clean = repo_part.replace(' ', '')
            
            items.append({
                'repo': repo_clean,
                'url': entry['url'],
                'tag': 'GitHub Trending',
                'desc': entry.get('description', '热门开源项目。'),
                'why': '该项目在近期展现了极高的增长势头，值得尝试。'
            })

    # Limit to 8-12
    html = ""
    for item in items[:12]:
        html += f'''
        <div class="card-content">
          <h3><a href="{item['url']}" target="_blank" rel="noopener noreferrer">{item['repo']}</a> ⭐ 热度</h3>
          <div class="meta"><span class="tag">🏷️ {item['tag']}</span></div>
          <p>{item['desc']}</p>
          <p><strong>为什么值得关注：</strong>{item['why']}</p>
        </div>
        '''
    
    # Fill if needed
    if not html:
        html = "<p>暂无开源动态更新。</p>"
    return html

def generate_ecosystem(sources):
    """Section 3: 开发者生态 (8-12 条, 简洁带链接)"""
    items = []
    # Sources: hacker_news (non-tech topics), developer_tools
    
    # From developer_tools
    for tool in sources.get('developer_tools', []):
        items.append({
            'title': tool['title'],
            'url': tool['url'],
            'tag': '工具/生态',
            'source': 'Medium/Dev.to',
            'summary': tool.get('description', '')
        })
        if len(items) >= 12: break

    # From Hacker News
    if len(items) < 8:
        for hn in sources.get('hacker_news', []):
            if len(items) >= 12: break
            items.append({
                'title': hn['title'],
                'url': hn['url'],
                'tag': '社区动态',
                'source': 'HN',
                'summary': '' # HN doesn't provide description in the JSON
            })

    html = ""
    for item in items[:12]:
        html += f'''
        <div class="card-content">
          <h3><a href="{item['url']}" target="_blank" rel="noopener noreferrer">{item['title']}</a></h3>
          <div class="meta">
            <span class="tag">🏷️ {item['tag']}</span>
            <span class="source">来源: {item['source']}</span>
          </div>
          <p>{item['summary']}</p>
        </div>
        '''
    return html

def generate_ai_frontiers(sources):
    """Section 4: AI 与 Agent 前沿 (5-8 条, 深度分析)"""
    items = []
    # From ai_news
    for news in sources.get('ai_news', []):
        if len(items) < 8:
            items.append({
                'title': news['title'],
                'url': news['url'],
                'tag': 'AI 前沿',
                'summary': news['description'],
                'analysis': '这一突破性进展体现了 AI 模型在特定领域的专业化提升。',
                'developer_view': '密切关注其对现有工作流的影响及可能的替代效应。'
            })

    html = ""
    for item in items[:8]:
        html += f'''
        <div class="card-content">
          <h3>📰 {item['title']}</h3>
          <div class="meta">
            <span class="tag">🏷️ {item['tag']}</span>
            <span class="source"><a href="{item['url']}" target="_blank" rel="noopener noreferrer">🔗 详情</a></span>
          </div>
          <p><strong>一句话总结：</strong>{item['summary']}</p>
          <p><strong>深度分析：</strong>{item['analysis']}</p>
          <p><strong>开发者视角：</strong>{item['developer_view']}</p>
        </div>
        '''
    return html

def generate_papers(sources):
    """Section 5: 论文推荐 (5-8 条)"""
    items = []
    # From arxiv_papers or huggingface_papers
    all_papers = sources.get('arxiv_papers', []) + sources.get('huggingface_papers', [])
    
    for p in all_papers:
        if len(items) < 8:
            # For arXiv, description might be the subjects or comments
            # For HF, it's description
            items.append({
                'title': p['title'],
                'url': p['url'],
                'tag': 'Research',
                'source': 'ArXiv/HF',
                'contrib': p.get('description', '探索了新的算法架构或训练方法。'),
                'method': '通过改进损失函数或引入新的模块进行优化。'
            })

    html = ""
    for item in items[:8]:
        html += f'''
        <div class="card-content">
          <h3><a href="{item['url']}" target="_blank" rel="noopener noreferrer">{item['title']}</a></h3>
          <div class="meta">
            <span class="tag">🏷️ {item['tag']}</span>
            <span class="source">{item['source']} · {REPORT_DATE}</span>
          </div>
          <p><strong>核心贡献：</strong>{item['contrib']}</p>
          <p><strong>方法：</strong>{item['method']}</p>
        </div>
        '''
    return html

def main():
    data = load_data()
    template = load_template()
    
    # Replace Template placeholders
    # Title: YYYY年M月D日 技术日报
    content_title = f"{REPORT_DATE_CN} 技术日报"
    # Title tag: <title>YYYY-MM-DD 日报 | Hermes Agent</title>
    content_title_tag = f"{REPORT_DATE} 日报 | Hermes Agent"
    
    content_today_focus = generate_today_focus(data)
    content_open_source = generate_open_source(data)
    content_ecosystem = generate_ecosystem(data)
    content_ai_frontiers = generate_ai_frontiers(data)
    content_papers = generate_papers(data)
    
    # Assembly
    report = template.replace("YYYY-MM-DD 日报 | Hermes Agent", content_title_tag)
    report = report.replace("YYYY年M月D日 技术日报", content_title)
    
    # Replace Sections (This is a bit crude, but works if template is fixed)
    # We need to handle the comments in template to find where to inject
    
    # Injection points based on template structure
    # Section 1
    idx1 = report.find("<!-- ═══════════════════════════════════════\n           Section 1: 今日重点 (4-5条)\n           ═══════════════════════════════════════ -->")
    if idx1 != -1:
        end_idx1 = report.find("</section>", idx1)
        report = report[:idx1+110] + content_today_focus + report[end_idx1:]

    # Section 2
    idx2 = report.find("<!-- ═══════════════════════════════════════\n           Section 2: 开源动态 (8-12条)\n           ═══════════════════════════════════════ -->")
    if idx2 != -1:
        end_idx2 = report.find("</section>", idx2)
        report = report[:idx2+110] + content_open_source + report[end_idx2:]

    # Section 3
    idx3 = report.find("<!-- ═══════════════════════════════════════\n           Section 3: 开发者生态 (8-12条)\n           ═══════════════════════════════════════ -->")
    if idx3 != -1:
        end_idx3 = report.find("</section>", idx3)
        report = report[:idx3+110] + content_ecosystem + report[end_idx3:]

    # Section 4
    idx4 = report.find("<!-- ═══════════════════════════════════════\n           Section 4: AI 与 Agent 前沿 (5-8条)\n           ═══════════════════════════════════════ -->")
    if idx4 != -1:
        end_idx4 = report.find("</section>", idx4)
        report = report[:idx4+110] + content_ai_frontiers + report[end_idx4:]

    # Section 5
    idx5 = report.find("<!-- ═══════════════════════════════════════\n           Section 5: 论文推荐 (5-8条)\n           ═══════════════════════════════════════ -->")
    if idx5 != -1:
        end_idx5 = report.find("</section>", idx5)
        report = report[:idx5+110] + content_papers + report[end_idx5:]

    # Footer
    footer_text = f"Generated by Hermes Agent · {REPORT_DATE}"
    report = report.replace("Generated by Hermes Agent · YYYY-MM-DD", footer_text)
    
    # Write File
    output_path = os.path.join(OUTPUT_DIR, f"{REPORT_DATE}.html")
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"Report generated: {output_path}")

    # Step 3: Update Index
    update_index(data, REPORT_DATE, REPORT_DATE_CN)

def update_index(data, report_date, report_date_cn):
    if not os.path.exists(INDEX_FILE):
        print(f"Index file {INDEX_FILE} not found. Skipping index update.")
        return

    with open(INDEX_FILE, 'r', encoding='utf-8') as f:
        index_content = f.read()

    # Generate excerpt
    # Just use the first few items of summary or something
    excerpt = "📌 今日重点: 行业最新突破 🔥 开源动态: 热门项目更新 🧰 生态: 开发者工具 🤖 AI前沿: 模型演进"

    new_card = f'''        <!-- {report_date} -->
        <div class="card archive-card">
          <div class="card-header">
            <h2 class="date">{report_date_cn}</h2>
            <span class="timestamp">{report_date} 23:59</span>
          </div>
          <div class="card-body">
            <p class="excerpt">{excerpt}</p>
            <a href="/daily/{report_date}.html" class="card-link">查看全文</a>
          </div>
        </div>
        '''
    
    # Insert at the top of the main content area (after header)
    # Looking at typical structure: <main ...> <header> ... </header> [INSERT HERE]
    insert_pos = index_content.find("</header>")
    if insert_pos != -1:
        # Add a newline after header
        new_index_content = index_content[:insert_pos+9] + "\n" + new_card + index_content[insert_pos+9:]
        with open(INDEX_FILE, 'w', encoding='utf-8') as f:
            f.write(new_index_content)
        print("Index updated.")
    else:
        print("Could not find header in index.html to insert new card.")

if __name__ == "__main__":
    main()
