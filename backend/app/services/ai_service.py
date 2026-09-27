from openai import OpenAI
from ..config import get_settings


settings = get_settings()


class AIService:

    def __init__(self):
        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=settings.openrouter_api_key
        )

        # Free OpenRouter router
        self.model = "openrouter/free"

    def generate_all_docs(self, repo_context: dict) -> dict:
        """
        Generate README, setup guide, and architecture documentation
        using actual repository information.
        """

        # ============================================================
        # BASIC REPOSITORY INFORMATION
        # ============================================================

        name = repo_context.get("name", "Unknown")

        description = repo_context.get(
            "description",
            "No description available"
        )

        stars = repo_context.get("stars", 0)
        forks = repo_context.get("forks", 0)
        watchers = repo_context.get("watchers", 0)

        license_name = repo_context.get(
            "license",
            "Not specified"
        )

        topics = repo_context.get("topics", [])

        created = repo_context.get("created_at", "")
        updated = repo_context.get("last_updated", "")

        contributors = repo_context.get(
            "contributors",
            1
        )

        primary_language = repo_context.get(
            "primary_language",
            ""
        )

        full_name = repo_context.get(
            "full_name",
            name
        )

        # ============================================================
        # LANGUAGE INFORMATION
        # ============================================================

        lang_percentages = repo_context.get(
            "language_percentages",
            {}
        )

        if lang_percentages:
            languages_text = ", ".join(
                f"{lang} ({pct}%)"
                for lang, pct in lang_percentages.items()
            )
        else:
            languages_text = ", ".join(
                repo_context.get("languages", [])
            )

        # ============================================================
        # ACTUAL REPOSITORY FILE INFORMATION
        # ============================================================

        package_json = repo_context.get(
            "package_json",
            ""
        )

        requirements = repo_context.get(
            "requirements",
            ""
        )

        all_files = repo_context.get(
            "all_files",
            []
        )

        main_file_name = repo_context.get(
            "main_file_name",
            ""
        )

        existing_readme = repo_context.get(
            "existing_readme",
            ""
        )

        # Convert values safely to strings
        package_json = package_json or ""
        requirements = requirements or ""
        existing_readme = existing_readme or ""

        package_lower = package_json.lower()
        requirements_lower = requirements.lower()

        files_lower = [
            str(file).lower()
            for file in all_files
        ]

        # ============================================================
        # DETECT PROJECT TYPE
        # ============================================================

        project_type = "Unknown"

        if package_json:
            project_type = "JavaScript/Node.js"

        elif requirements:
            project_type = "Python"

        elif any(
            file.endswith("pom.xml")
            for file in files_lower
        ):
            project_type = "Java/Maven"

        elif any(
            file.endswith("build.gradle")
            or file.endswith("build.gradle.kts")
            for file in files_lower
        ):
            project_type = "Java/Gradle"

        elif any(
            file.endswith(".csproj")
            for file in files_lower
        ):
            project_type = "C#/.NET"

        elif any(
            file.endswith("go.mod")
            for file in files_lower
        ):
            project_type = "Go"

        # ============================================================
        # DETECT INSTALLATION COMMAND
        # ============================================================

        install_commands = []

        if package_json:
            install_commands = [
                "npm install"
            ]

        elif requirements:
            install_commands = [
                "python -m venv venv",
                "source venv/bin/activate",
                "pip install -r requirements.txt"
            ]

        elif "pom.xml" in files_lower:
            install_commands = [
                "./mvnw install"
            ]

        elif (
            "build.gradle" in files_lower
            or "build.gradle.kts" in files_lower
        ):
            install_commands = [
                "./gradlew build"
            ]

        elif "go.mod" in files_lower:
            install_commands = [
                "go mod download"
            ]

        elif any(
            file.endswith(".csproj")
            for file in files_lower
        ):
            install_commands = [
                "dotnet restore"
            ]

        # ============================================================
        # DETECT RUN COMMAND
        # ============================================================

        run_command = (
            "Refer to the repository README for the correct "
            "run command."
        )

        # -----------------------------
        # JavaScript / Node.js
        # -----------------------------

        if package_json:

            if '"dev"' in package_lower:
                run_command = "npm run dev"

            elif '"start"' in package_lower:
                run_command = "npm start"

            elif '"serve"' in package_lower:
                run_command = "npm run serve"

            else:
                run_command = (
                    "Check package.json scripts for the "
                    "available run command."
                )

        # -----------------------------
        # Python
        # -----------------------------

        elif requirements:

            if "fastapi" in requirements_lower:

                if main_file_name:
                    module_name = (
                        main_file_name
                        .replace(".py", "")
                        .replace("/", ".")
                    )

                    run_command = (
                        f"uvicorn {module_name}:app --reload"
                    )

                else:
                    run_command = (
                        "uvicorn main:app --reload"
                    )

            elif "flask" in requirements_lower:

                run_command = "flask run"

            elif "django" in requirements_lower:

                if "manage.py" in files_lower:
                    run_command = (
                        "python manage.py runserver"
                    )

                else:
                    run_command = (
                        "Use the Django project's documented "
                        "run command."
                    )

            elif (
                "streamlit" in requirements_lower
                and any(
                    file.endswith("app.py")
                    for file in files_lower
                )
            ):
                run_command = "streamlit run app.py"

            elif main_file_name:

                run_command = (
                    f"python {main_file_name}"
                )

        # -----------------------------
        # Go
        # -----------------------------

        elif "go.mod" in files_lower:

            run_command = "go run ."

        # -----------------------------
        # .NET
        # -----------------------------

        elif any(
            file.endswith(".csproj")
            for file in files_lower
        ):

            run_command = "dotnet run"

        # -----------------------------
        # Java / Maven
        # -----------------------------

        elif "pom.xml" in files_lower:

            run_command = "./mvnw spring-boot:run"

        # ============================================================
        # DATABASE DETECTION
        # ============================================================

        db_setup = ""

        topics_text = " ".join(
            str(topic)
            for topic in topics
        ).lower()

        if (
            "mysql" in topics_text
            or "mysql-database" in topics_text
        ):
            db_setup = (
                "\n# MySQL setup should follow the "
                "repository documentation."
            )

        elif "postgresql" in topics_text:

            db_setup = (
                "\n# PostgreSQL setup should follow the "
                "repository documentation."
            )

        # ============================================================
        # BUILD INSTALL COMMAND TEXT
        # ============================================================

        if install_commands:

            installation_commands = "\n".join(
                install_commands
            )

        else:

            installation_commands = (
                "# Follow the installation instructions "
                "provided by the repository."
            )

        # ============================================================
        # CONTEXT FOR AI
        # ============================================================

        context_parts = [

            f"Repository: {name}",

            f"Full Name: {full_name}",

            f"URL: https://github.com/{full_name}",

            f"Description: {description}",

            f"Project Type: {project_type}",

            f"Primary Language: {primary_language}",

            f"All Languages: {languages_text}",

            f"Stars: {stars}",

            f"Forks: {forks}",

            f"Watchers: {watchers}",

            f"Contributors: {contributors}",

            f"License: {license_name}",

            f"Created: {created}",

            f"Last Updated: {updated}",

            (
                f"Topics: "
                f"{', '.join(topics) if topics else 'None'}"
            ),

            (
                f"Detected Installation Commands:\n"
                f"{installation_commands}"
            ),

            f"Detected Run Command: {run_command}",
        ]

        # ============================================================
        # TECHNOLOGY INFORMATION
        # ============================================================

        if topics:

            context_parts.append(
                "\n--- DETECTED TECHNOLOGIES ---\n"
                + ", ".join(topics)
            )

        # ============================================================
        # README
        # ============================================================

        if existing_readme:

            context_parts.append(
                "\n--- EXISTING README ---\n"
                + existing_readme[:5000]
            )

        # ============================================================
        # REQUIREMENTS
        # ============================================================

        if requirements:

            context_parts.append(
                "\n--- REQUIREMENTS.TXT ---\n"
                + requirements[:5000]
            )

        # ============================================================
        # PACKAGE.JSON
        # ============================================================

        if package_json:

            context_parts.append(
                "\n--- PACKAGE.JSON ---\n"
                + package_json[:5000]
            )

        # ============================================================
        # MAIN FILE
        # ============================================================

        if repo_context.get("main_file_content"):

            context_parts.append(
                (
                    "\n--- MAIN FILE "
                    f"({main_file_name}) ---\n"
                    f"{repo_context['main_file_content'][:3000]}"
                )
            )

        # ============================================================
        # FILE STRUCTURE
        # ============================================================

        if all_files:

            context_parts.append(
                "\n--- FILES IN REPOSITORY ---\n"
                + "\n".join(
                    str(file)
                    for file in all_files[:50]
                )
            )

        full_context = "\n".join(
            context_parts
        )

        # ============================================================
        # AI PROMPT
        # ============================================================

        prompt = f"""
You are an expert technical writer generating onboarding
documentation for a GitHub repository.

Use ONLY the repository evidence provided below.

Do NOT invent:
- technologies
- dependencies
- commands
- files
- frameworks
- databases
- features
- architecture components
- setup instructions

If the repository does not provide enough evidence for something,
say that it is not available instead of guessing.

================ REPOSITORY DATA ================

{full_context}

================ STRICT RULES ================

1. Use the exact repository statistics provided.

2. Use the exact language percentages provided.

3. Only mention technologies supported by:
   - repository files
   - package.json
   - requirements.txt
   - README
   - detected topics
   - detected project type

4. Installation commands MUST match the detected project type.

5. Do NOT add Python commands to a JavaScript/Node.js project
   unless actual Python files/dependencies prove Python is required.

6. Do NOT add npm commands to a Python project unless actual
   package.json evidence proves Node.js is required.

7. If package.json exists, inspect its scripts and dependencies
   before suggesting npm commands.

8. If requirements.txt exists, use it as evidence for Python
   dependencies.

9. Use the detected run command:
   {run_command}

10. If no reliable run command can be determined, explicitly say:
    "The repository does not provide enough evidence to determine
    the exact run command."

11. Base architecture descriptions only on the provided file
    structure and repository content.

12. Do not claim that a feature exists unless repository evidence
    supports it.

13. Keep the generated documentation practical for a developer
    who has just cloned the repository.

================ OUTPUT FORMAT ================

Return exactly these three sections:

===README===

A professional README containing:

- project overview
- verified features
- technology stack
- repository statistics
- installation
- usage
- project structure
- contributing
- license

===SETUP===

A practical setup guide containing:

- prerequisites
- installation
- environment setup if supported by evidence
- how to run
- common issues

===ARCHITECTURE===

A technical architecture document containing:

- overview
- major components
- project organization
- data flow

Remember:

ONLY use information supported by the repository evidence.
Never guess commands or technologies.
"""

        # ============================================================
        # OPENROUTER REQUEST
        # ============================================================

        try:

            response = self.client.chat.completions.create(
                model=self.model,
                max_tokens=4000,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )

            content = response.choices[0].message.content

            print(
                f"Generated {len(content)} characters"
            )

            # ========================================================
            # PARSE AI RESPONSE
            # ========================================================

            import re

            readme = ""
            setup = ""
            architecture = ""

            # Normalize line endings
            content = content.replace(
                "\r\n",
                "\n"
            ).strip()

            # --------------------------------------------------------
            # Find section markers
            #
            # Accept formatting variations:
            #
            # ===README===
            # ===README====
            # ===README==
            # ===ARCHITECTURE===
            # ===ARCHITECTURE==
            # --------------------------------------------------------

            pattern = re.compile(
                r"={2,}\s*"
                r"(README|SETUP|ARCHITECTURE)"
                r"\s*={2,}",
                re.IGNORECASE
            )

            matches = list(
                pattern.finditer(content)
            )

            # --------------------------------------------------------
            # Extract sections
            # --------------------------------------------------------

            for i, match in enumerate(matches):

                section_name = (
                    match.group(1).upper()
                )

                start = match.end()

                if i + 1 < len(matches):
                    end = matches[i + 1].start()
                else:
                    end = len(content)

                section_content = (
                    content[start:end]
                    .strip()
                )

                if section_name == "README":

                    readme = section_content

                elif section_name == "SETUP":

                    setup = section_content

                elif section_name == "ARCHITECTURE":

                    architecture = section_content

            # ========================================================
            # FALLBACKS
            # ========================================================

            if not readme:

                readme = content

            if not setup:

                setup = (
                    "## Setup\n\n"
                    "See the repository README for "
                    "installation instructions."
                )

            if not architecture:

                architecture = (
                    "## Architecture\n\n"
                    "Architecture details could not be "
                    "determined from the available repository data."
                )

            # ========================================================
            # RETURN DOCUMENTATION
            # ========================================================

            return {
                "readme": readme,
                "setup_guide": setup,
                "architecture": architecture
            }

        except Exception as e:

            print(
                f"OpenRouter Error (generate_all_docs): {e}"
            )

            return {
                "readme": None,
                "setup_guide": None,
                "architecture": None
            }

    # ================================================================
    # BACKWARD COMPATIBILITY
    # ================================================================

    def generate_readme(
        self,
        repo_context: dict
    ) -> str:

        """
        Keep for backward compatibility.
        """

        result = self.generate_all_docs(
            repo_context
        )

        return result.get("readme")

    def generate_setup_guide(
        self,
        repo_name: str,
        languages: list,
        frameworks: list,
        dependencies: str = None
    ) -> str:

        """
        Keep for backward compatibility.
        """

        prompt = f"""
Generate a step-by-step setup guide for this project.

Project:
{repo_name}

Languages:
{', '.join(languages)}

Frameworks:
{', '.join(frameworks) if frameworks else 'None detected'}

Dependencies:
{dependencies or 'Not available'}

Rules:
- Do not invent technologies.
- Do not invent dependencies.
- Do not invent commands.
- Use only the provided information.
- If information is unavailable, explicitly say so.

Include:

1. Prerequisites
2. Installation steps
3. Environment setup
4. How to run
5. Common issues

Return markdown only.
"""

        try:

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )

            return response.choices[0].message.content

        except Exception as e:

            print(
                f"OpenRouter Error (setup): {e}"
            )

            return None

    # ================================================================
    # ARCHITECTURE
    # ================================================================

    def generate_architecture_description(
        self,
        repo_name: str,
        file_structure: list,
        languages: list
    ) -> str:

        """
        Keep for backward compatibility.
        """

        files_text = "\n".join(
            [
                f["path"]
                for f in file_structure[:30]
                if isinstance(f, dict)
                and "path" in f
            ]
        )

        prompt = f"""
Analyze the architecture of this project.

Project:
{repo_name}

Languages:
{', '.join(languages)}

Files:
{files_text}

Rules:
- Base the architecture only on the provided files.
- Do not invent components or technologies.
- If something cannot be determined, say so.

Describe:

1. Architecture overview
2. Key components
3. Project organization
4. Data flow

Return markdown only.
"""

        try:

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )

            return response.choices[0].message.content

        except Exception as e:

            print(
                f"OpenRouter Error (architecture): {e}"
            )

            return None

    # ================================================================
    # CONNECTION TEST
    # ================================================================

    def test_connection(self) -> bool:

        try:

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "user",
                        "content": "Reply only with: API working"
                    }
                ]
            )

            content = response.choices[0].message.content

            return (
                "working" in content.lower()
            )

        except Exception as e:

            print(e)

            return False