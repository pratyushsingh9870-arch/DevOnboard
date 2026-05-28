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
        """
        Generate README + Setup Guide + Architecture in ONE API call.
        3x faster than separate calls!
        """

        context_parts = []
        context_parts.append(f"Repository: {repo_context.get('name', 'Unknown')}")
        context_parts.append(f"Description: {repo_context.get('description', 'No description')}")
        context_parts.append(f"Languages: {', '.join(repo_context.get('languages', []))}")

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
                f"\n--- MAIN FILE ({repo_context.get('main_file_name', 'unknown')}) ---\n"
                f"{repo_context['main_file_content'][:1000]}"
            )

        if repo_context.get('all_files'):
            context_parts.append(
                f"\n--- ALL FILES ---\n" + "\n".join(repo_context['all_files'][:20])
            )

        full_context = "\n".join(context_parts)

        prompt = f"""Based on this REAL GitHub repository data, generate 3 documents.

REPOSITORY DATA:
{full_context}

STRICT RULES:
- Use ONLY information from the data above
- Do NOT invent files, features, or tech that are not mentioned
- Be accurate and specific to this actual project

Generate exactly in this format with these exact markers:

===README===
(Professional README.md with title, description, features, installation, usage, tech stack, project structure, contributing guide, license)

===SETUP===
(Step-by-step setup guide with prerequisites, installation steps, environment setup, how to run)

===ARCHITECTURE===
(Brief architecture description based on actual files and structure)"""

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                max_tokens=3000,
                messages=[{"role": "user", "content": prompt}]
            )

            content = response.choices[0].message.content
            print(f"✅ AI response received ({len(content)} chars)")

            # Parse the three sections
            readme = ""
            setup = ""
            architecture = ""

            if "===README===" in content and "===SETUP===" in content:
                readme = content.split("===README===")[1].split("===SETUP===")[0].strip()

            if "===SETUP===" in content and "===ARCHITECTURE===" in content:
                setup = content.split("===SETUP===")[1].split("===ARCHITECTURE===")[0].strip()

            if "===ARCHITECTURE===" in content:
                architecture = content.split("===ARCHITECTURE===")[1].strip()

            # Fallback if markers not found
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