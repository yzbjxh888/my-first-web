import argparse
import json
import os
from datetime import datetime, timedelta

def generate_report(target_date_str=None):
    # 1. Configuration & Setup
    if target_date_str:
        report_date_obj = datetime.strptime(target_date_str, '%Y-%m-%d')
    else:
        # Default: Yesterday's date
        report_date_obj = datetime.now() - timedelta(days=1)
    
    report_date_str = report_date_obj.strftime('%Y-%m-%d')
    
    # Paths
    base_dir = '/home/zhang/my-first-web'
    data_dir = os.path.join(base_dir, 'data')
    daily_dir = os.path.join(base_dir, 'daily')
    template_path = os.path.join(daily_dir, 'report-template.html')
    output_path = os.path.join(daily_dir, f'{report_date_str}.html')
    index_path = os.path.join(daily_dir, 'index.html')
    
    source_file = os.path.join(data_dir, f'daily-source-{report_date_str}.json')
    
    print(f"--- Generating Report for {report_date_str} ---")
    
    # 2. Load Data
    if not os.path.exists(source_file):
        print(f"ERROR: Source file not found: {source_file}")
        return
    
    with open(source_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print(f"Loaded data from {source_file}")

    # 3. Load Template
    if not os.path.exists(template_path):
        print(f"ERROR: Template file not found: {template_path}")
        return
        
    with open(template_path, 'r', encoding='utf-8') as f:
        template = f.read()

    # 4. Process Sections
    sections_content = {
        "focus": [],
        "opensource": [],
        "ecosystem": [],
        "ai_agent": [],
        "papers": []
    }

    # 5. Mapping Data to Sections
    
    # A. GitHub Trending -> 🔥 开源动态
    if "github_trending" in data:
        for item in data["github_trending"][:12]:
            url = item.get("url", "#")
            title = item.get("title", "Unknown Repo")
            desc = item.get("description", "")
            
            repo_name = "unknown/repo"
            if "/" in title:
                repo_name = title
            elif "Trending · " in desc:
                import re
                match = re.search(r'([\w-]+)\s*/\s*([\w-]+)', desc)
                if match:
                    repo_name = f"{match.group(1)}/{match.group(2)}"
            
            sections_content["opensource"].append(f"""
        <div class="card-content">
          <h3><a href="{url}" target="_blank" rel="noopener noreferrer">{repo_name}</a> ⭐</h3>
          <div class="meta">
            <span class="tag">🏷️ 开源</span>
          </div>
          <p>{desc}</p>
          <p><strong>为什么值得关注：</strong>热门开源项目，值得开发者关注其技术实现。</p>
        </div>""")

    # B. Hacker News -> 🧰 开发者生态
    if "hacker_news" in data:
        for item in data["hacker_news"][:12]:
            url = item.get("url", "#")
            title = item.get("title", "Unknown Title")
            score = item.get("score", 0)
            sections_content["ecosystem"].append(f"""
        <div class="card-content">
          <h3><a href="{url}" target="_blank" rel="noopener noreferrer">{title}</a></h3>
          <div class="meta">
            <span class="tag">🏷️ 社区热点</span>
            <span class="source">来源: HN ({score} pts)</span>
          </div>
          <p>来自 Hacker News 的热门讨论。</p>
        </div>""")

    # C. AI News -> 🤖 AI 与 Agent 前沿
    if "ai_news" in data:
        for item in data["ai_news"][:8]:
            url = item.get("url", "#")
            title = item.get("title", "Unknown AI News")
            desc = item.get("description", "")
            sections_content["ai_agent"].append(f"""
        <div class="card-content">
          <h3>📰 {title}</h3>
          <div class="meta">
            <span class="tag">🏷️ AI 动态</span>
            <span class="source"><a href="{url}" target="_blank" rel="noopener noreferrer">🔗 详情</a></span>
          </div>
          <p><strong>一句话总结：</strong>{desc[:100]}...</p>
          <p><strong>深度分析：</strong>AI 领域持续快速迭代，此类动态反映了行业趋势。</p>
          <p><strong>开发者视角：</strong>关注模型与应用结合的可能性。</p>
        </div>""")

    # D. ArXiv / HuggingFace -> 📚 论文推荐
    paper_sources = []
    if "arxiv_papers" in data:
        paper_sources.extend(data["arxiv_papers"])
    if "huggingface_papers" in data:
        paper_sources.extend(data["huggingface_papers"])
        
    for item in paper_sources[:8]:
        url = item.get("url", "#")
        title = item.get("title", "Unknown Paper")
        desc = item.get("description", "")
        sections_content["papers"].append(f"""
        <div class="card-content">
          <h3><a href="{url}" target="_blank" rel="noopener noreferrer">{title}</a></h3>
          <div class="meta">
            <span class="tag">🏷️ 论文</span>
            <span class="source">ArXiv / HF</span>
          </div>
          <p><strong>核心贡献：</strong>{desc[:150]}...</p>
          <p><strong>方法：</strong>基于深度学习的最新研究成果。</p>
        </div>""")

    # E. Today's Focus
    if sections_content["ai_agent"]:
        sections_content["focus"].append(sections_content["ai_agent"][0])
    
    # 6. Construct HTML
    report_title_h1 = f"{report_date_obj.year}年{report_date_obj.month}月{report_date_obj.day}日 技术日报"
    
    section1 = "".join(sections_content["focus"])
    if not section1: section1 = "<p>暂无今日重点内容。</p>"
    
    section2 = "".join(sections_content["opensource"])
    if not section2: section2 = "<p>暂无开源动态。</p>"

    section3 = "".join(sections_content["ecosystem"])
    if not section3: section3 = "<p>暂无生态动态。</p>"

    section4 = "".join(sections_content["ai_agent"])
    if not section4: section4 = "<p>暂无 AI 前沿信息。</p>"

    section5 = "".join(sections_content["papers"])
    if not section5: section5 = "<p>暂无论文推荐。</p>"

    html = template
    html = html.replace("YYYY-MM-DD 日报 | Hermes Agent", f"{report_date_str} 日报 | Hermes Agent")
    html = html.replace("YYYY年M月D日 技术日报", report_title_h1)
    
    import re
    def replace_section(html_str, marker, content):
        parts = re.split(rf"<!--.*?{marker}.*?-->", html_str)
        if len(parts) < 2: return html_str
        section_part = parts[1]
        header_match = re.search(r"(<section class=\"card\">\s*<h2>.*?</h2>\s*)", section_part)
        if not header_match: return html_str
        header = header_match.group(1)
        content_end_match = re.search(r"(</section>)", section_part[len(header.strip()):])
        if not content_end_match: return html_str
        new_section = header + "\n\n" + content + "\n      </section>"
        return parts[0] + new_section + parts[2]

    html = replace_section(html, "Section 1: 今日重点", section1)
    html = replace_section(html, "Section 2: 开源动态", section2)
    html = replace_section(html, "Section 3: 开发者生态", section3)
    html = replace_section(html, "Section 4: AI 与 Agent 前沿", section4)
    html = replace_section(html, "Section 5: 论文推荐", section5)

    footer_text = f"Generated by Hermes Agent · {report_date_obj.strftime('%Y-%m-%d %H:%M')}"
    html = html.replace("Generated by Hermes Agent · YYYY-MM-DD", footer_text)

    # 5. Save File
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f"SUCCESS: Report saved to {output_path}")

    # 6. Update Index
    if os.path.exists(index_path):
        with open(index_path, 'r', encoding='utf-8') as f:
            index_content = f.read()
        
        excerpt = f"📌 今日重点: {len(sections_content['focus'])} 条 | 🔥 开源动态: {len(sections_content['opensource'])} 条 | 🧰 生态: {len(sections_content['ecosystem'])} 条 | 🤖 AI前沿: {len(sections_content['ai_agent'])} 条"
        new_card = f"""        <!-- {report_date_str} -->
        <div class="card archive-card">
          <div class="card-header">
            <h2 class="date">{report_date_obj.year}年{report_date_obj.month}月{report_date_obj.day}日</h2>
            <span class="timestamp">{report_date_str} 23:59</span>
          </div>
          <div class="card-body">
            <p class="excerpt">{excerpt}</p>
            <a href="/daily/{report_date_str}.html" class="card-link">查看全文</a>
          </div>
        </div>
"""
        import re
        match = re.search(r"(</header>)", index_content)
        if match:
            insertion_point = match.end()
            new_index_content = index_content[:insertion_point] + "\n" + new_card + index_content[insertion_point:]
            with open(index_path, 'w', encoding='utf-8') as f:
                f.write(new_index_content)
            print(f"SUCCESS: Index updated at {index_path}")
        else:
            print("WARNING: Could not find insertion point in index.html. Skipping index update.")
    else:
        print(f"WARNING: Index file not found: {index_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--date", type=str, help="Target report date (YYYY-MM-DD)")
    args = parser.parse_args()
    generate_report(args.date)
