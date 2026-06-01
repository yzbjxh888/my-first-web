# Agentic World Project

## 🏗️ Architecture: Headless Semantic Web

This project follows a **Single Source of Truth** architecture designed for both humans and AI.

### 📂 Directory Structure

- **`/content/`**: **[The Knowledge Source]** Contains Markdown (.md) files. This is the ONLY place where content is written.
- **`/api/`**: **[The AI Interface]** Contains auto-generated JSON mirrors of the content. Optimized for LLM consumption.
- **`/public/`**: **[The Human Interface]** Contains the rendered HTML, CSS, and assets. This is what Vercel deploys.
- **`/assets/`**: Static media files.

### 🔄 Workflow
Content (Markdown) $\rightarrow$ AgentCore $\rightarrow$ (HTML + JSON) $\rightarrow$ Deployment
