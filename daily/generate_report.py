import json
import datetime
import os
import re
import sys

# Configuration
BASE_DIR = "/home/zhang/my-first-web"
DATA_DIR = os.path.join(BASE_DIR, "data")
DAILY_DIR = os.path.join(BASE_DIR, "daily")
TEMPLATE_PATH = os.path.join(DAILY_DIR, "report-template.html")
INDEX_PATH = os.path.join(DAILY_DIR, "index.html")

def get_date_from_filename(filename):
    match = re.search(r'(\d{4}-\d{2}-\d{2})', filename)
    return match.group(1) if match else None

def load_data(report_date):
    filename = f"daily-source-{report_date}.json"
    path = os.path.join(DATA_DIR, filename)
    if not os.path.exists(path):
        # Fallback: if the specific date is not found, find the most recent one
        files = sorted([f for f in os.listdir(DATA_DIR) if f.startswith("daily-source-") and f.endswith(".json")], reverse=True)
        if files:
            path = os.path.join(DATA_DIR, files[0])
            print(f"Warning: Specific data for {report_date} not found. Using {os.path.basename(path)}.")
        else:
            raise FileNotFoundError(f"No data files found in {DATA_DIR}")
    
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def parse_github_repos(text):
    pattern = r'([a-zA-Z0-9._-]+/[a-zA-Z0-9._-]+)'
    matches = re.findall(pattern, text)
    return [m for m in matches if '/' in m]

def generate_report(report_date):
    print(f"Generating report for {report_date}...")
    data = load_data(report_date)
    
    sections = {
        "today_focus": [],
        "open_source": [],
        "developer_ecosystem": [],
        "ai_agent_frontier": [],
        "paper_recommendation": []
    }

    # 1. AI & Agent Frontier (ai_news)
    for item in data.get("ai_news", []):
        title, desc, url = item["title"], item["description"], item["url"]
        is_major = any(k in title.lower() or k in desc.lower() for k in ["breakthrough", "major", "unveils", "announces", "revolution", "agentic", "star"])
        
        if is_major and len(sections["today_focus"]) < 5:
            sections["today_focus"].append({
                "title": title, "url": url, "tag": "⭐ 重大突破",
                "summary": desc,
                "analysis": "该进展显著提升了 AI 在实际场景中的应用能力，尤其是在自主决策和复杂任务编排方面。",
                "dev_view": "开发者应密切关注其 API 的可用性以及如何将其集成到现有的 Agent 工作流中。"
            })
        elif len(sections["ai_agent_frontier"]) < 8:
            sections["ai_agent_frontier"].append({
                "title": title, "url": url, "tag": "🤖 AI 前沿",
                "summary": desc,
                "analysis": "体现了当前 AI 模型向更强的推理和多模态能力发展的趋势。",
                "dev_view": "关注模型能力边界的变化，寻找新的应用切入点。"
            })

    # 2. Open Source (github_trending)
    for item in data.get("github_trending", []):
        desc = item.get("description", "")
        if "Trending ·" in desc:
            repos = parse_github_repos(desc)
            for r in repos:
                if len(sections["open_source"]) < 12:
                    sections["open_source"].append({"repo": r, "url": item["url"], "tag": "🛠️ 开源项目", "desc": "GitHub Trending 热点项目。"})
        else:
            repo_match = parse_github_repos(item["title"] + " " + desc)
            repo = repo_match[0] if repo_match else "unknown/repo"
            if len(sections["open_source"]) < 12:
                sections["open_source"].append({
                    "repo": repo, "url": item["url"], "tag": "🛠️ 开源项目",
                    "desc": desc[:150] + "..." if len(desc) > 150 else desc
                })

    # 3. Developer Ecosystem (hacker_news & developer_tools)
    for item in data.get("hacker_news", []):
        if len(sections["developer_ecosystem"]) < 12:
            sections["developer_ecosystem"].append({
                "title": item["title"], "url": item["url"], "tag": "🌐 社区讨论",
                "source": f"HN · Score: {item.get('score', 'N/A')}",
                "summary": "社区正在深入讨论该话题的技术细节与影响。"
            })
    for item in data.get("developer_tools", []):
        if len(sections["developer_ecosystem"]) < 12:
            sections["developer_ecosystem"].append({
                "title": item["title"], "url": item["url"], "tag": "🧰 开发工具",
                "source": "工具趋势", "summary": item["description"][:100]
            })

    # 4. Paper Recommendation
    all_papers = []
    for item in data.get("arxiv_papers", []):
        if any(x in item["url"] for x in ["list", "recent", "current"]): continue
        all_papers.append({"title": item["title"], "url": item["url"], "tag": "📝 学术论文", "source": "ArXiv", "content": item["description"]})
    for item in data.get("huggingface_papers", []):
        if "trending" in item["url"] or "papers" in item["url"] and not any(x in item["url"] for x in ["date", "month"]): continue
        all_papers.append({"title": item["title"], "url": item["url"], "tag": "🤗 模型研究", "source": "Hugging Face", "content": item["description"]})

    for paper in all_papers[:8]:
        sections["paper_recommendation"].append({
            "title": paper["title"], "url": paper["url"], "tag": paper["tag"], "source": paper["source"],
            "contribution": "提出了一种新的方法论或实验结果。", "method": "基于深度学习与大规模数据分析。"
        })

    # --- Render ---
    with open(TEMPLATE_PATH, 'r', encoding='utf-8') as f:
        template = f.read()

    template = template.replace("YYYY-MM-DD", report_date)
    parts = report_date.split('-')
    template = template.replace("YYYY年M月D日", f"{parts[0]}年{int(parts[1])}月{int(parts[2])}日")

    def get_section_html(header, items, builder_func):
        html = f'<section class="card"><h2>{header}</h2>'
        for item in items: html += builder_func(item)
        html += '</section>'
        return html

    def item_today_builder(i):
        return f'''<div class="card-content">
          <h3>📰 {i['title']}</h3>
          <div class="meta">
            <span class="tag">{i['tag']}</span>
            <span class="source"><a href="{i['url']}" target="_blank" rel="noopener noreferrer">🔗 原文</a></span>
          </div>
          <p><strong>一句话总结：</strong>{i['summary']}</p>
          <p><strong>深度分析：</strong>{i['analysis']}</p>
          <p><strong>开发者视角：</strong>{i['dev_view']}</p>
        </div>'''

    def item_open_builder(i):
        return f'''<div class="card-content">
          <h3><a href="{i['url']}" target="_blank" rel="noopener noreferrer">{i['repo']}</a></h3>
          <div class="meta"><span class="tag">{i['tag']}</span></div>
          <p>{i['desc']}</p>
          <p><strong>为什么值得关注：</strong>具有极高的活跃度与社区影响力。</p>
        </div>'''

    def item_eco_builder(i):
        return f'''<div class="card-content">
          <h3><a href="{i['url']}" target="_blank" rel="noopener noreferrer">{i['title']}</a></h3>
          <div class="meta">
            <span class="tag">{i['tag']}</span>
            <span class="source">来源: {i['source']}</span>
          </div>
          <p>{i['summary']}</p>
        </div>'''

    def item_ai_builder(i):
        return f'''<div class="card-content">
          <h3>📰 {i['title']}</h3>
          <div class="meta">
            <span class="tag">{i['tag']}</span>
            <span class="source"><a href="{i['url']}" target="_blank" rel="noopener noreferrer">🔗 详情</a></span>
          </div>
          <p><strong>一句话总结：</strong>{i['summary']}</p>
          <p><strong>深度分析：</strong>{i['analysis']}</p>
          <p><strong>开发者视角：</strong>{i['dev_view']}</p>
        </div>'''

    def item_paper_builder(i):
        return f'''<div class="card-content">
          <h3><a href="{i['url']}" target="_blank" rel="noopener noreferrer">{i['title']}</a></h3>
          <div class="meta">
            <span class="tag">{i['tag']}</span>
            <span class="source">{i['source']} · {report_date}</span>
          </div>
          <p><strong>核心贡献：</strong>{i['contribution']}</p>
          <p><strong>方法：</strong>{i['method']}</p>
        </div>'''

    s1 = get_section_html("📌 今日重点", sections["today_focus"], item_today_builder)
    s2 = get_section_html("🔥 开源动态", sections["open_source"], item_open_builder)
    s3 = get_section_html("🧰 开发者生态", sections["developer_ecosystem"], item_eco_builder)
    s4 = get_section_html("🤖 AI 与 Agent 前沿", sections["ai_agent_frontier"], item_ai_builder)
    s5 = get_section_html("📚 论文推荐", sections["paper_recommendation"], item_paper_builder)

    def replace_section_robust(html, header_text, new_html):
        h_idx = html.find(header_text)
        if h_idx == -1: return html
        s_idx = html.find("</section>", h_idx)
        if s_idx == -1: return html
        start_idx = html.rfind('<section class="card">', 0, h_idx)
        if start_idx == -1: return html
        return html[:start_idx] + new_html + html[s_idx+len("</section>"):]

    template = replace_section_robust(template, "<h2>📌 今日重点</h2>", s1)
    template = replace_section_robust(template, "<h2>🔥 开源动态</h2>", s2)
    template = replace_section_robust(template, "<h2>🧰 开发者生态</h2>", s3)
    template = replace_section_robust(template, "<h2>🤖 AI 与 Agent 前沿</h2>", s4)
    template = replace_section_robust(template, "<h2>📚 论文推荐</h2>", s5)

    now = datetime.datetime.now()
    footer_text = f'<footer>Generated by Hermes Agent · {report_date} {now.strftime("%H:%M")}</footer>'
    template = re.sub(r'<footer>.*?</footer>', footer_text, template, flags=re.DOTALL)

    output_path = os.path.join(DAILY_DIR, f"{report_date}.html")
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(template)
    return output_path, sections

def update_index(report_date, sections):
    print(f"Updating index.html...")
    with open(INDEX_PATH, 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. Remove any existing card for this date (including comments)
    # Using a more careful approach: find the comment and the following card.
    pattern = re.compile(r'<!--\s*' + re.escape(report_date) + r'\s*-->.*?<div class="card archive-card">.*?</div>', re.DOTALL)
    content = pattern.sub('', content)

    # 2. Prepare new card
    focus = sections["today_focus"][0]["title"] if sections["today_focus"] else "无"
    focus = (focus[:50] + '...') if len(focus) > 50 else focus
    excerpt = f"📌 今日重点: {focus} 🔥 开源动态: {len(sections['open_source'])} 个项目 🧰 生态: {len(sections['developer_ecosystem'])} 条动态 🤖 AI前沿: {len(sections['ai_agent_frontier'])} 项前沿 📚 论文: {len(sections['paper_recommendation'])} 篇"

    now = datetime.datetime.now()
    timestamp = now.strftime("%Y-%m-%d %H:%M")
    parts = report_date.split('-')
    date_cn = f"{parts[0]}年{int(parts[1])}月{int(parts[2])}日"

    new_card = f'''
        <!-- {report_date} -->
        <div class="card archive-card">
          <div class="card-header">
            <h2 class="date">{date_cn}</h2>
            <span class="timestamp">{timestamp}</span>
          </div>
          <div class="card-body">
            <p class="excerpt">{excerpt}</p>
            <a href="/daily/{report_date}.html" class="card-link">查看全文</a>
          </div>
        </div>'''

    # 3. Insert BEFORE <div class="archive-list">
    list_start_pattern = r'(<div class="archive-list">)'
    new_content = re.sub(list_start_pattern, f'{new_card}\n\\1', content)

    with open(INDEX_PATH, 'w', encoding='utf-8') as f:
        f.write(new_content)

def main():
    if len(sys.argv) > 1:
        report_date = sys.argv[1]
    else:
        files = sorted([f for f in os.listdir(DATA_DIR) if f.startswith("daily-source-") and f.endswith(".json")], reverse=True)
        if files:
            report_date = get_date_from_filename(files[0])
        else:
            print("No data files found.")
            return

    try:
        report_path, sections = generate_report(report_date)
        update_index(report_date, sections)
        print("Report generation complete.")
    except Exception as e:
        print(f"Error during generation: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
