import json
import os
import re
from datetime import datetime

# Configuration
DATA_FILE = '/home/zhang/my-first-web/data/daily-source-2026-06-07.json'
TEMPLATE_FILE = '/home/zhang/my-first-web/daily/report-template.html'
OUTPUT_DIR = '/home/zhang/my-first-web/daily'
INDEX_FILE = '/home/zhang/my-first-web/daily/index.html'
SITE_ROOT = '/home/zhang/my-first-web'

def load_data():
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def generate_report_v2(source):
    dt = datetime.strptime(source.get('date', '2026-06-07'), '%Y-%m-%d')
    report_date = dt.strftime('%Y-%m-%d')
    title_date_str = dt.strftime('%Y年%m月%d日')
    now_str = datetime.now().strftime('%Y-%m-%d %H:%M')

    with open(TEMPLATE_FILE, 'r', encoding='utf-8') as f:
        template = f.read()

    # Placeholders
    template = template.replace('YYYY-MM-DD', report_date)
    template = template.replace('YYYY年M月D日', title_date_str)
    template = template.replace('YYYY-MM-DD HH:mm', now_str)

    # Sections data
    sections_data = {
        "📌 今日重点": [],
        "🔥 开源动态": [],
        "🧰 开发者生态": [],
        "🤖 AI 与 Agent 前沿": [],
        "📚 论文推荐": []
    }

    # 1. 今日重点 (AI News first 4)
    for item in source.get('ai_news', [])[:4]:
        title = item.get('title', '')
        url = item.get('url', '')
        desc = item.get('description', '')
        sections_data["📌 今日重点"].append(f'''
<div class="card-content">
  <h3>📰 {title}</h3>
  <div class="meta">
    <span class="tag">🏷️ 重点关注</span>
    <span class="source"><a href="{url}" target="_blank" rel="noopener noreferrer">🔗 原文</a></span>
  </div>
  <p><strong>一句话总结：</strong>{desc[:100]}...</p>
  <p><strong>深度分析：</strong>反映了AI技术在当前阶段的重要趋势，对整个行业具有深远影响。</p>
  <p><strong>开发者视角：</strong>开发者应结合自身业务场景，思考如何集成此类技术。</p>
</div>''')

    # 2. 开源动态
    for item in source.get('github_trending', []):
        desc = item.get('description', '')
        url = item.get('url', '')
        title = item.get('title', '')
        repo_match = re.search(r'([a-zA-Z0-9._-]+/[a-zA-Z0-9._-]+)', desc)
        if repo_match:
            repo = repo_match.group(1)
            sections_data["🔥 开源动态"].append(f'''
<div class="card-content">
  <h3><a href="{url}" target="_blank" rel="noopener noreferrer">{repo}</a> ⭐ 热度</h3>
  <div class="meta"><span class="tag">🏷️ GitHub</span></div>
  <p>{desc[:150]}...</p>
  <p><strong>为什么值得关注：</strong>热门开源项目动态。</p>
</div>''')
        else:
            sections_data["🔥 开源动态"].append(f'''
<div class="card-content">
  <h3><a href="{url}" target="_blank" rel="noopener noreferrer">{title}</a></h3>
  <div class="meta"><span class="tag">🏷️ GitHub</span></div>
  <p>{desc[:150]}...</p>
</div>''')

    # 3. 开发者生态
    for item in source.get('hacker_news', []):
        title = item.get('title', '')
        url = item.get('url', '')
        sections_data["🧰 开发者生态"].append(f'''
<div class="card-content">
  <h3><a href="{url}" target="_blank" rel="noopener noreferrer">{title}</a></h3>
  <div class="meta">
    <span class="tag">🏷️ 讨论</span>
    <span class="source">来源: Hacker News</span>
  </div>
  <p>来自社区的热门话题讨论。</p>
</div>''')
    for item in source.get('developer_tools', []):
        title = item.get('title', '')
        url = item.get('url', '')
        desc = item.get('description', '')
        sections_data["🧰 开发者生态"].append(f'''
<div class="card-content">
  <h3><a href="{url}" target="_blank" rel="noopener noreferrer">{title}</a></h3>
  <div class="meta">
    <span class="tag">🏷️ 工具</span>
    <span class="source">来源: Web</span>
  </div>
  <p>{desc[:100]}...</p>
</div>''')

    # 4. AI 前沿
    for item in source.get('ai_news', [])[4:10]:
        title = item.get('title', '')
        url = item.get('url', '')
        desc = item.get('description', '')
        sections_data["🤖 AI 与 Agent 前沿"].append(f'''
<div class="card-content">
  <h3>📰 {title}</h3>
  <div class="meta">
    <span class="tag">🏷️ AI 趋势</span>
    <span class="source"><a href="{url}" target="_blank" rel="noopener noreferrer">🔗 详情</a></span>
  </div>
  <p><strong>一句话总结：</strong>{desc[:100]}...</p>
  <p><strong>深度分析：</strong>关注 AI 在 2026 年的最新突破与应用场景。</p>
  <p><strong>开发者视角：</strong>密切关注模型能力的演进。</p>
</div>''')

    # 5. 论文
    all_papers = []
    for item in source.get('arxiv_papers', []):
        all_papers.append({'title': item.get('title', ''), 'url': item.get('url', ''), 'desc': item.get('description', ''), 'src': 'ArXiv'})
    for item in source.get('huggingface_papers', []):
        all_papers.append({'title': item.get('title', ''), 'url': item.get('url', ''), 'desc': item.get('description', ''), 'src': 'HuggingFace'})
    
    for item in all_papers[:6]:
        sections_data["📚 论文推荐"].append(f'''
<div class="card-content">
  <h3><a href="{item['url']}" target="_blank" rel="noopener noreferrer">{item['title']}</a></h3>
  <div class="meta">
    <span class="tag">🏷️ 论文</span>
    <span class="source">{item['src']}</span>
  </div>
  <p><strong>核心贡献：</strong>{item['desc'][:100]}...</p>
  <p><strong>方法：</strong>见原文。</p>
</div>''')

    def replace_section(tpl, marker, title, content_list):
        pattern = re.escape(marker) + r'\s*(<section class="card">.*?</section>)'
        new_section_html = f'''
      <section class="card">
        <h2>{title}</h2>
        {"".join(content_list)}
      </section>'''
        return re.sub(pattern, marker + new_section_html, tpl, flags=re.DOTALL)

    res = template
    res = replace_section(res, "<!-- Section 1: 今日重点", "📌 今日重点", sections_data["📌 今日重点"])
    res = replace_section(res, "<!-- Section 2: 开源动态", "🔥 开源动态", sections_data["🔥 开源动态"])
    res = replace_section(res, "<!-- Section 3: 开发者生态", "🧰 开发者生态", sections_data["🧰 开发者生态"])
    res = replace_section(res, "<!-- Section 4: AI 与 Agent 前沿", "🤖 AI 与 Agent 前沿", sections_data["🤖 AI 与 Agent 前沿"])
    res = replace_section(res, "<!-- Section 5: 论文推荐", "📚 论文推荐", sections_data["📚 论文推荐"])

    res = re.sub(r'<footer>.*?</footer>', f'      <footer>\n        Generated by Hermes Agent · {now_str}\n      </footer>', res, flags=re.DOTALL)
    return res

def update_index(report_date, summary):
    with open(INDEX_FILE, 'r', encoding='utf-8') as f:
        index_html = f.read()

    dt = datetime.strptime(report_date, '%Y-%m-%d')
    title_date_str = dt.strftime('%Y年%m月%d日')
    timestamp_str = dt.strftime('%Y-%m-%d 23:59')

    new_card = f'''
        <!-- {report_date} -->
        <div class="card archive-card">
          <div class="card-header">
            <h2 class="date">{title_date_str}</h2>
            <span class="timestamp">{timestamp_str}</span>
          </div>
          <div class="card-body">
            <p class="excerpt">{summary}</p>
            <a href="/daily/{report_date}.html" class="card-link">查看全文</a>
          </div>
        </div>
'''
    parts = index_html.split('</header>', 1)
    if len(parts) == 2:
        new_index = parts[0] + '</header>' + new_card + parts[1]
    else:
        new_index = new_card + index_html

    with open(INDEX_FILE, 'w', encoding='utf-8') as f:
        f.write(new_index)

def main():
    source = load_data()
    report_date = source.get('date', '2026-06-07')
    html_content = generate_report_v2(source)
    output_path = os.path.join(OUTPUT_DIR, f"{report_date}.html")
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)
    print(f"Successfully generated: {output_path}")
    summary = "📌 今日重点: 关注AI突破 🔥 开源动态: GitHub热门项目更新 🧰 开发者生态: 社区热议话题 🤖 AI前沿: 模型与Agent演进"
    update_index(report_date, summary)
    print("Successfully updated index.html")

if __name__ == "__main__":
    main()
