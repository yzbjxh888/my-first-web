import json
import os
import re
from datetime import datetime

# Configuration
DATA_FILE = "/home/zhang/my-first-web/data/daily-source-2026-06-07.json"
TEMPLATE_FILE = "/home/zhang/my-first-web/daily/report-template.html"
OUTPUT_FILE = "/home/zhang/my-first-web/daily/2026-06-07.html"
INDEX_FILE = "/home/zhang/my-first-web/daily/index.html"
REPORT_DATE_STR = "2026-06-07"
REPORT_DATE_TITLE = "2026年6月7日"
GENERATED_AT = datetime.now().strftime("%Y-%m-%d %H:%M")

def load_json(path):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def load_template(path):
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()

def generate_report():
    if not os.path.exists(DATA_FILE):
        print(f"Error: {DATA_FILE} not found.")
        return
    if not os.path.exists(TEMPLATE_FILE):
        print(f"Error: {TEMPLATE_FILE} not found.")
        return
    if not os.path.exists(INDEX_FILE):
        print(f"Error: {INDEX_FILE} not found.")
        return

    data = load_json(DATA_FILE)
    template = load_template(TEMPLATE_FILE)

    # --- Section 1: 今日重点 (4-5 条) ---
    highlights = []
    # From AI news
    for item in data.get('ai_news', []):
        if any(kw in item['title'].lower() for kw in ["breakthrough", "major", "nvidia", "openai", "google", "deepseek"]):
            highlights.append({
                "title": item['title'],
                "url": item['url'],
                "tag": "🤖 AI 前沿",
                "summary": item['description'],
                "analysis": "这是一个值得关注的AI领域重要进展，体现了当前技术发展的趋势。",
                "dev_view": "开发者应关注其对现有工作流的影响。"
            })
            if len(highlights) >= 2: break
    
    # From HN
    for item in data.get('hacker_news', []):
        if item['score'] > 50:
            highlights.append({
                "title": item['title'],
                "url": item['url'],
                "tag": "🌐 开发者社区",
                "summary": "Hacker News 高热度讨论。",
                "analysis": "该话题引起了社区广泛关注，反映了当前技术圈的关注点。",
                "dev_view": "值得阅读以了解社区动态。"
            })
            if len(highlights) >= 4: break
    
    while len(highlights) < 4:
        highlights.append({
            "title": "暂无更多重点内容",
            "url": "#",
            "tag": "其他",
            "summary": "-",
            "analysis": "-",
            "dev_view": "-"
        })

    # --- Section 2: 开源动态 (8-12 条) ---
    open_source = []
    # Attempt to parse github_trending description
    for item in data.get('github_trending', []):
        desc = item.get('description', '')
        parts = desc.split(' · ')
        for part in parts:
            if '/' in part:
                repo_name = part.strip()
                if repo_name.lower() not in ['trending', 'all languages', 'today(utc)', 'daily', 'weekly', 'monthly', 'yearly']:
                    # Check if it's a valid owner/repo
                    if len(repo_name.split('/')) == 2:
                        open_source.append({
                            "repo": repo_name,
                            "stars": "🔥",
                            "tag": "💻 开源项目",
                            "desc": "GitHub Trending 热门项目。",
                            "why": "近期热度上升明显。"
                        })
            if len(open_source) >= 12: break
        if len(open_source) >= 12: break

    # Supplement with developer_tools
    if len(open_source) < 8:
        for item in data.get('developer_tools', []):
            open_source.append({
                "repo": item['title'],
                "stars": "⭐",
                "tag": "🛠️ 开发工具",
                "desc": item['description'],
                "why": "提供了新的开发思路或工具链。"
            })
            if len(open_source) >= 12: break

    # --- Section 3: 开发者生态 (8-12 条) ---
    ecosystem = []
    for item in data.get('hacker_news', []):
        if item['score'] > 0:
            ecosystem.append({
                "title": item['title'],
                "url": item['url'],
                "tag": "🌐 社区动态",
                "source": "Hacker News",
                "summary": f"得分: {item['score']}"
            })
            if len(ecosystem) >= 12: break

    # --- Section 4: AI 与 Agent 前沿 (5-8 条) ---
    ai_frontiers = []
    for item in data.get('ai_news', []):
        ai_frontiers.append({
            "title": item['title'],
            "url": item['url'],
            "tag": "🤖 AI 动态",
            "summary": item['description'],
            "analysis": "这是AI领域最新的动态，反映了模型能力和应用场景的演进。",
            "dev_view": "关注其如何改变现有的AI开发范式。"
        })
        if len(ai_frontiers) >= 8: break

    # --- Section 5: 论文推荐 (5-8 条) ---
    papers = []
    all_papers = data.get('arxiv_papers', []) + data.get('huggingface_papers', [])
    for item in all_papers:
        if "arxiv.org" in item['url'] or "huggingface.co/papers" in item['url']:
            papers.append({
                "title": item['title'],
                "url": item['url'],
                "tag": "📚 论文",
                "source": "ArXiv" if "arxiv.org" in item['url'] else "Hugging Face",
                "date": "2026-06-07",
                "contribution": item['description'][:150],
                "method": "详见原文。"
            })
            if len(papers) >= 8: break

    # --- HTML Generation ---
    
    h_html = ""
    for h in highlights:
        h_html += f"""
        <div class="card-content">
          <h3>📰 {h['title']}</h3>
          <div class="meta">
            <span class="tag">🏷️ {h['tag']}</span>
            <span class="source"><a href="{h['url']}" target="_blank" rel="noopener noreferrer">🔗 原文</a></span>
          </div>
          <p><strong>一句话总结：</strong>{h['summary']}</p>
          <p><strong>深度分析：</strong>{h['analysis']}</p>
          <p><strong>开发者视角：</strong>{h['dev_view']}</p>
        </div>"""

    os_html = ""
    for o in open_source:
        repo_link = f"https://github.com/{o['repo']}"
        os_html += f"""
        <div class="card-content">
          <h3><a href="{repo_link}" target="_blank" rel="noopener noreferrer">{o['repo']}</a> {o['stars']}</h3>
          <div class="meta">
            <span class="tag">🏷️ {o['tag']}</span>
          </div>
          <p>{o['desc']}</p>
          <p><strong>为什么值得关注：</strong>{o['why']}</p>
        </div>"""

    eco_html = ""
    for e in ecosystem:
        eco_html += f"""
        <div class="card-content">
          <h3><a href="{e['url']}" target="_blank" rel="noopener noreferrer">{e['title']}</a></h3>
          <div class="meta">
            <span class="tag">🏷️ {e['tag']}</span>
            <span class="source">来源: {e['source']}</span>
          </div>
          <p>{e['summary']}</p>
        </div>"""

    ai_html = ""
    for a in ai_frontiers:
        ai_html += f"""
        <div class="card-content">
          <h3>📰 {a['title']}</h3>
          <div class="meta">
            <span class="tag">🏷️ {a['tag']}</span>
            <span class="source"><a href="{a['url']}" target="_blank" rel="noopener noreferrer">🔗 详情</a></span>
          </div>
          <p><strong>一句话总结：</strong>{a['summary']}</p>
          <p><strong>深度分析：</strong>{a['analysis']}</p>
          <p><strong>开发者视角：</strong>{a['dev_view']}</p>
        </div>"""

    p_html = ""
    for p in papers:
        p_html += f"""
        <div class="card-content">
          <h3><a href="{p['url']}" target="_blank" rel="noopener noreferrer">{p['title']}</a></h3>
          <div class="meta">
            <span class="tag">🏷️ {p['tag']}</span>
            <span class="source">{p['source']} · {p['date']}</span>
          </div>
          <p><strong>核心贡献：</strong>{p['contribution']}</p>
          <p><strong>方法：</strong>{p['method']}</p>
        </div>"""

    html = template.replace("YYYY-MM-DD", REPORT_DATE_STR)
    html = html.replace("YYYY年M月D日", REPORT_DATE_TITLE)
    html = html.replace("<!-- 更多重点条目... -->", h_html)
    html = html.replace("<!-- 更多开源条目... -->", os_html)
    html = html.replace("<!-- 更多生态条目... -->", eco_html)
    html = html.replace("<!-- 更多条目... -->", ai_html)
    html = html.replace("<!-- 更多论文条目... -->", p_html)
    
    # Handle footer separately to be safe
    html = re.sub(r"Generated by Hermes Agent · YYYY-MM-DD", f"Generated by Hermes Agent · {GENERATED_AT}", html)

    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f"Successfully generated {OUTPUT_FILE}")

    # Update Index
    with open(INDEX_FILE, 'r', encoding='utf-8') as f:
        index_content = f.read()
    
    # Safe excerpt
    h_title = highlights[0]['title'][:30] if highlights else "暂无"
    os_title = open_source[0]['repo'][:30] if open_source else "暂无"
    eco_title = ecosystem[0]['title'][:30] if ecosystem else "暂无"
    ai_title = ai_frontiers[0]['title'][:30] if ai_frontiers else "暂无"
    excerpt = f"📌 今日重点: {h_title}... 🔥 开源动态: {os_title}... 🧰 开发者生态: {eco_title}... 🤖 AI前沿: {ai_title}..."
    
    new_card = f"""
        <!-- {REPORT_DATE_STR} -->
        <div class="card archive-card">
          <div class="card-header">
            <h2 class="date">{REPORT_DATE_TITLE}</h2>
            <span class="timestamp">{REPORT_DATE_STR} 23:59</span>
          </div>
          <div class="card-body">
            <p class="excerpt">{excerpt}</p>
            <a href="/daily/{REPORT_DATE_STR}.html" class="card-link">查看全文</a>
          </div>
        </div>"""
    
    # Insert after <header>
    header_match = re.search(r'(<header>.*?</header>)', index_content, re.DOTALL)
    if header_match:
        header_html = header_match.group(1)
        new_index_content = index_content.replace(header_html, header_html + "\n" + new_card)
    else:
        new_index_content = index_content + "\n" + new_card
    
    with open(INDEX_FILE, 'w', encoding='utf-8') as f:
        f.write(new_index_content)
    print(f"Successfully updated {INDEX_FILE}")

if __name__ == "__main__":
    generate_report()
