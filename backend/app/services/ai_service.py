from openai import OpenAI
from ..config import get_settings

settings = get_settings()


class AIService:

    def __init__(self):
        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=settings.openrouter_api_key
        )
        self.model = "openai/gpt-oss-20b:free"

    def generate_all_docs(self, repo_context: dict) -> dict:

        name = repo_context.get('name', 'Unknown')
        description = repo_context.get('description', 'No description')
        stars = repo_context.get('stars', 0)
        forks = repo_context.get('forks', 0)
        watchers = repo_context.get('watchers', 0)
        license_name = repo_context.get('license', 'MIT')
        topics = repo_context.get('topics', [])
        created = repo_context.get('created_at', '')
        updated = repo_context.get('last_updated', '')
        contributors = repo_context.get('contributors', 1)
        primary_language = repo_context.get('primary_language', '')
        full_name = repo_context.get('full_name', name)

        print(f"TOPICS: {topics}")
        print(f"STARS: {stars} | FORKS: {forks}")

        lang_percentages = repo_context.get('language_percentages', {})
        languages_text = ", ".join([
            f"{lang} ({pct}%)" for lang, pct in lang_percentages.items()
        ]) if lang_percentages else ", ".join(repo_context.get('languages', []))

        # Detect run command from topics
        if 'streamlit' in topics:
            run_command = "streamlit run App/App.py"
        elif 'flask' in ' '.join(topics).lower():
            run_command = "flask run"
        elif 'django' in ' '.join(topics).lower():
            run_command = "python manage.py runserver"
        elif 'fastapi' in ' '.join(topics).lower():
            run_command = "uvicorn main:app --reload"
        else:
            run_command = "python main.py"

        # Detect database from topics
        db_setup = ""
        if 'mysql' in ' '.join(topics).lower() or 'mysql-database' in topics:
            db_setup = "\n# Setup MySQL database\nmysql -u root -p\nCREATE DATABASE project_db;"
        elif 'postgresql' in ' '.join(topics).lower():
            db_setup = "\n# Setup PostgreSQL\ncreatedb project_db"

        context_parts = [
            f"Repository: {name}",
            f"Full Name: {full_name}",
            f"URL: https://github.com/{full_name}",
            f"Description: {description}",
            f"Primary Language: {primary_language}",
            f"All Languages: {languages_text}",
            f"Stars: {stars}",
            f"Forks: {forks}",
            f"Watchers: {watchers}",
            f"Contributors: {contributors}",
            f"License: {license_name}",
            f"Created: {created}",
            f"Last Updated: {updated}",
            f"Topics (actual tech stack): {', '.join(topics) if topics else 'None'}",
        ]

        if topics:
            context_parts.append(
                f"IMPORTANT TECHNOLOGIES FROM TOPICS: {', '.join(topics)}"
            )

        if repo_context.get('existing_readme'):
            context_parts.append(
                f"\n--- EXISTING README ---\n{repo_context['existing_readme'][:1500]}"
            )
        if repo_context.get('requirements'):
            context_parts.append(
                f"\n--- REQUIREMENTS.TXT ---\n{repo_context['requirements']}"
            )
        if repo_context.get('package_json'):
            context_parts.append(
                f"\n--- PACKAGE.JSON ---\n{repo_context['package_json']}"
            )
        if repo_context.get('main_file_content'):
            context_parts.append(
                f"\n--- MAIN FILE ({repo_context.get('main_file_name')}) ---\n"
                f"{repo_context['main_file_content'][:1000]}"
            )
        if repo_context.get('all_files'):
            context_parts.append(
                f"\n--- FILES IN REPO ---\n"
                + "\n".join(repo_context['all_files'][:25])
            )

        full_context = "\n".join(context_parts)

       
# Build prompt as separate variable - no indentation issues!
        prompt = (
            "You are a technical writer. Generate 3 documents for this GitHub repository.\n\n"
            f"REAL DATA (use ONLY this - do not invent anything):\n{full_context}\n\n"
            f"CRITICAL RULES:\n"
            f"1. Stars = {stars}, Forks = {forks} - USE THESE EXACT NUMBERS IN BADGES\n"
            f"2. Topics = {', '.join(topics) if topics else 'none'} - ACTUAL TECHNOLOGIES\n"
            f"3. Languages = {languages_text} - USE EXACT PERCENTAGES\n"
            f"4. Run command = {run_command}\n"
            f"5. Do NOT invent any technology not in topics/requirements/files\n"
            f"6. Topics are the most important technology indicators\n\n"
            "Generate with NO spaces before markers:\n\n"
            f"===README===\n"
            f"# {name}\n\n"
            f"![Stars](https://img.shields.io/badge/stars-{stars}-yellow?style=flat-square) "
            f"![Forks](https://img.shields.io/badge/forks-{forks}-blue?style=flat-square) "
            f"![Language](https://img.shields.io/badge/language-{primary_language}-green?style=flat-square) "
            f"![License](https://img.shields.io/badge/license-{license_name.replace(' ', '_')}-orange?style=flat-square)\n\n"
            f"> {description}\n\n"
            "---\n\n"
            "## 📌 Overview\n\n"
            "[2-3 paragraphs about what this project does based on README and code]\n\n"
            "---\n\n"
            "## ✨ Features\n\n"
            "| Feature | Description |\n"
            "|---------|-------------|\n"
            "[Only features visible in existing README or main file]\n\n"
            "---\n\n"
            "## 🛠️ Tech Stack\n\n"
            "| Category | Technology |\n"
            "|----------|------------|\n"
            f"| Language | {languages_text} |\n"
            "[Add rows for technologies found in topics]\n\n"
            "---\n\n"
            "## 📊 Repository Stats\n\n"
            "| Metric | Value |\n"
            "|--------|-------|\n"
            f"| ⭐ Stars | {stars} |\n"
            f"| 🍴 Forks | {forks} |\n"
            f"| 👁️ Watchers | {watchers} |\n"
            f"| 👥 Contributors | {contributors} |\n"
            f"| 📜 License | {license_name} |\n"
            f"| 🕒 Last Updated | {updated} |\n\n"
            "---\n\n"
            "##  Installation\n\n"
            "```bash\n"
            f"git clone https://github.com/{full_name}.git\n"
            f"cd {name}\n"
            "python -m venv venv\n"
            "source venv/bin/activate\n"
            f"pip install -r requirements.txt{db_setup}\n"
            "```\n\n"
            "---\n\n"
            "## 📖 Usage\n\n"
            "```bash\n"
            f"{run_command}\n"
            "```\n\n"
            "[2-3 sentences about how to use based on README]\n\n"
            "---\n\n"
            "##  Project Structure\n\n"
            "```\n"
            f"{name}/\n"
            "[Show actual files from FILES IN REPO - do not invent]\n"
            "```\n\n"
            "---\n\n"
            "## 🤝 Contributing\n\n"
            "1. Fork the repository\n"
            "2. Create feature branch\n"
            "3. Commit changes\n"
            "4. Push and open a Pull Request\n\n"
            "---\n\n"
            "## 📜 License\n\n"
            f"{license_name}\n\n"
            "===SETUP===\n"
            f"# Setup Guide - {name}\n\n"
            "## Prerequisites\n\n"
            f"[Only what is needed for: {languages_text}]\n\n"
            "## Installation\n\n"
            "```bash\n"
            f"git clone https://github.com/{full_name}.git\n"
            f"cd {name}\n"
            "python -m venv venv\n"
            "source venv/bin/activate\n"
            f"pip install -r requirements.txt{db_setup}\n"
            "```\n\n"
            "## Running the Project\n\n"
            "```bash\n"
            f"{run_command}\n"
            "```\n\n"
            "## Common Issues\n\n"
            "[2-3 issues specific to this tech stack]\n\n"
            "===ARCHITECTURE===\n"
            f"# Architecture - {name}\n\n"
            "## Overview\n\n"
            "[Describe architecture based on actual file structure]\n\n"
            "## Key Components\n\n"
            "[Describe each major file/folder from FILES list]\n\n"
            "## Data Flow\n\n"
            "[How data moves through the system]"
        )

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                max_tokens=3000,
                messages=[{"role": "user", "content": prompt}]
            )

            content = response.choices[0].message.content
            print(f" Generated {len(content)} chars")

            readme = setup = architecture = ""

            if "===README===" in content and "===SETUP===" in content:
                readme = content.split("===README===")[1].split("===SETUP===")[0].strip()

            if "===SETUP===" in content and "===ARCHITECTURE===" in content:
                setup = content.split("===SETUP===")[1].split("===ARCHITECTURE===")[0].strip()

            if "===ARCHITECTURE===" in content:
                architecture = content.split("===ARCHITECTURE===")[1].strip()

            if not readme:
                readme = content
            if not setup:
                setup = "## Setup\n\nSee README for installation instructions."
            if not architecture:
                architecture = "## Architecture\n\nSee project files for structure."

            return {
                "readme": readme,
                "setup_guide": setup,
                "architecture": architecture
            }

        except Exception as e:
            print(f"OpenRouter Error (generate_all_docs): {e}")
            return {
                "readme": None,
                "setup_guide": None,
                "architecture": None
            }

    def generate_readme(self, repo_context: dict) -> str:
        """Keep for backward compatibility"""
        result = self.generate_all_docs(repo_context)
        return result.get("readme")

    def generate_setup_guide(
        self,
        repo_name: str,
        languages: list,
        frameworks: list,
        dependencies: str = None
    ) -> str:
        """Keep for backward compatibility"""

        prompt = f"""Generate a step-by-step setup guide for this project.

Project: {repo_name}
Languages: {', '.join(languages)}
Frameworks: {', '.join(frameworks) if frameworks else 'None detected'}
Dependencies:
{dependencies or 'Not available'}

Include:
1. Prerequisites
2. Installation steps
3. Environment setup
4. How to run
5. Common issues

Return markdown only."""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}]
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"OpenRouter Error (setup): {e}")
            return None

    def generate_architecture_description(
        self,
        repo_name: str,
        file_structure: list,
        languages: list
    ) -> str:
        """Keep for backward compatibility"""

        files_text = "\n".join([
            f["path"] for f in file_structure[:30]
            if isinstance(f, dict)
        ])

        prompt = f"""Analyze the architecture of this project.

Project: {repo_name}
Languages: {', '.join(languages)}
Files:
{files_text}

Describe architecture, key components, and project organization.
Return markdown only."""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}]
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"OpenRouter Error (architecture): {e}")
            return None

    def test_connection(self) -> bool:
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": "Reply only with: API working"}]
            )
            return "working" in response.choices[0].message.content.lower()
        except Exception as e:
            print(e)
            return False