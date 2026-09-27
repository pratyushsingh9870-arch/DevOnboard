from typing import List


class ScriptGenerator:
    """
    Generate repository-aware setup scripts.

    Important:
    Scripts are based only on evidence supplied by the repository
    analysis. The generator does not assume Docker, databases,
    Homebrew, NodeSource, or other external tooling.
    """

    # ================================================================
    # HELPERS
    # ================================================================

    @staticmethod
    def _has_language(
        languages: List[str],
        language: str
    ) -> bool:

        return any(
            str(item).lower() == language.lower()
            for item in languages
        )

    @staticmethod
    def _contains(
        values: List[str],
        value: str
    ) -> bool:

        value = value.lower()

        return any(
            value in str(item).lower()
            for item in values
        )

    # ================================================================
    # BASH
    # ================================================================

    def generate_bash_script(
        self,
        repo_name: str,
        languages: List[str],
        frameworks: List[str],
        dependencies_file: str = None
    ) -> str:
        """
        Generate a conservative Bash setup script.

        The script only performs actions supported by the supplied
        repository evidence.
        """

        languages = languages or []
        frameworks = frameworks or []
        dependencies_file = dependencies_file or ""

        script_lines = [
            "#!/bin/bash",
            "set -e",
            "",
            "echo '🚀 DevOnboard Setup Script'",
            f"echo 'Setting up {repo_name}...'",
            "echo ''",
            ""
        ]

        # ============================================================
        # PYTHON
        # ============================================================

        has_python = (
            self._has_language(languages, "Python")
            or self._contains(frameworks, "django")
            or self._contains(frameworks, "flask")
            or self._contains(frameworks, "fastapi")
            or "requirements.txt" in dependencies_file.lower()
        )

        if has_python:

            script_lines.extend([
                "# Python Setup",
                "echo '📦 Python project detected'",
                "",
                "# Verify Python",
                "if ! command -v python3 &> /dev/null; then",
                "    echo 'Python 3 is required but was not found.'",
                "    echo 'Install Python 3 and run this script again.'",
                "    exit 1",
                "fi",
                "",
                "# Create virtual environment",
                "python3 -m venv venv",
                "",
                "# Activate virtual environment",
                "source venv/bin/activate",
                ""
            ])

            if "requirements.txt" in dependencies_file.lower():

                script_lines.extend([
                    "# Install Python dependencies",
                    "if [ -f \"requirements.txt\" ]; then",
                    "    echo 'Installing Python dependencies...'",
                    "    python -m pip install -r requirements.txt",
                    "else",
                    "    echo 'requirements.txt was not found.'",
                    "fi",
                    ""
                ])

        # ============================================================
        # NODE.JS
        # ============================================================

        has_node = (
            self._has_language(languages, "JavaScript")
            or self._has_language(languages, "TypeScript")
            or self._contains(frameworks, "react")
            or self._contains(frameworks, "vue")
            or self._contains(frameworks, "angular")
            or "package.json" in dependencies_file.lower()
        )

        if has_node:

            script_lines.extend([
                "# Node.js Setup",
                "echo '📦 JavaScript/Node.js project detected'",
                "",
                "# Verify Node.js",
                "if ! command -v node &> /dev/null; then",
                "    echo 'Node.js is required but was not found.'",
                "    echo 'Install Node.js and run this script again.'",
                "    exit 1",
                "fi",
                "",
                "# Verify npm",
                "if ! command -v npm &> /dev/null; then",
                "    echo 'npm is required but was not found.'",
                "    exit 1",
                "fi",
                "",
                "# Install dependencies",
                "if [ -f \"package.json\" ]; then",
                "    echo 'Installing Node.js dependencies...'",
                "    npm install",
                "else",
                "    echo 'package.json was not found.'",
                "fi",
                ""
            ])

        # ============================================================
        # UNKNOWN PROJECT
        # ============================================================

        if not has_python and not has_node:

            script_lines.extend([
                "echo 'No supported dependency manifest was detected.'",
                "echo 'Please follow the repository README for setup instructions.'",
                ""
            ])

        # ============================================================
        # FINAL MESSAGE
        # ============================================================

        script_lines.extend([
            "echo ''",
            "echo '✅ Setup preparation complete!'",
            f"echo 'Repository: {repo_name}'",
            "echo ''",
            "echo 'Next steps:'",
            "echo '  1. Review the repository README'",
            "echo '  2. Follow the documented run command'",
            "echo '  3. Start developing!'",
            ""
        ])

        return "\n".join(script_lines)

    # ================================================================
    # POWERSHELL
    # ================================================================

    def generate_powershell_script(
        self,
        repo_name: str,
        languages: List[str],
        frameworks: List[str],
        dependencies_file: str = None
    ) -> str:
        """
        Generate a conservative PowerShell setup script.
        """

        languages = languages or []
        frameworks = frameworks or []
        dependencies_file = dependencies_file or ""

        script_lines = [
            "# DevOnboard Setup Script for Windows",
            "$ErrorActionPreference = 'Stop'",
            "",
            "Write-Host '🚀 DevOnboard Setup Script' -ForegroundColor Green",
            f"Write-Host 'Setting up {repo_name}...'",
            "Write-Host ''",
            ""
        ]

        # ============================================================
        # PYTHON
        # ============================================================

        has_python = (
            self._has_language(languages, "Python")
            or self._contains(frameworks, "django")
            or self._contains(frameworks, "flask")
            or self._contains(frameworks, "fastapi")
            or "requirements.txt" in dependencies_file.lower()
        )

        if has_python:

            script_lines.extend([
                "# Python Setup",
                "Write-Host '📦 Python project detected' -ForegroundColor Cyan",
                "",
                "# Verify Python",
                "$pythonInstalled = Get-Command python -ErrorAction SilentlyContinue",
                "",
                "if (-not $pythonInstalled) {",
                "    Write-Host 'Python is required but was not found.' -ForegroundColor Red",
                "    Write-Host 'Install Python 3 and run this script again.'",
                "    exit 1",
                "}",
                "",
                "# Create virtual environment",
                "python -m venv venv",
                "",
                "# Activate virtual environment",
                ".\\venv\\Scripts\\Activate.ps1",
                ""
            ])

            if "requirements.txt" in dependencies_file.lower():

                script_lines.extend([
                    "# Install Python dependencies",
                    "if (Test-Path requirements.txt) {",
                    "    Write-Host 'Installing Python dependencies...'",
                    "    python -m pip install -r requirements.txt",
                    "}",
                    ""
                ])

        # ============================================================
        # NODE.JS
        # ============================================================

        has_node = (
            self._has_language(languages, "JavaScript")
            or self._has_language(languages, "TypeScript")
            or self._contains(frameworks, "react")
            or self._contains(frameworks, "vue")
            or self._contains(frameworks, "angular")
            or "package.json" in dependencies_file.lower()
        )

        if has_node:

            script_lines.extend([
                "# Node.js Setup",
                "Write-Host '📦 JavaScript/Node.js project detected' -ForegroundColor Cyan",
                "",
                "# Verify Node.js",
                "$nodeInstalled = Get-Command node -ErrorAction SilentlyContinue",
                "",
                "if (-not $nodeInstalled) {",
                "    Write-Host 'Node.js is required but was not found.' -ForegroundColor Red",
                "    Write-Host 'Install Node.js and run this script again.'",
                "    exit 1",
                "}",
                "",
                "# Verify npm",
                "$npmInstalled = Get-Command npm -ErrorAction SilentlyContinue",
                "",
                "if (-not $npmInstalled) {",
                "    Write-Host 'npm is required but was not found.' -ForegroundColor Red",
                "    exit 1",
                "}",
                "",
                "# Install dependencies",
                "if (Test-Path package.json) {",
                "    Write-Host 'Installing Node.js dependencies...'",
                "    npm install",
                "}",
                ""
            ])

        # ============================================================
        # UNKNOWN PROJECT
        # ============================================================

        if not has_python and not has_node:

            script_lines.extend([
                "Write-Host 'No supported dependency manifest was detected.'",
                "Write-Host 'Please follow the repository README for setup instructions.'",
                ""
            ])

        # ============================================================
        # FINAL MESSAGE
        # ============================================================

        script_lines.extend([
            "Write-Host ''",
            "Write-Host '✅ Setup preparation complete!' -ForegroundColor Green",
            f"Write-Host 'Repository: {repo_name}'",
            "Write-Host ''",
            "Write-Host 'Next steps:' -ForegroundColor Yellow",
            "Write-Host '  1. Review the repository README'",
            "Write-Host '  2. Follow the documented run command'",
            "Write-Host '  3. Start developing!'",
            ""
        ])

        return "\n".join(script_lines)

    # ================================================================
    # DOCKER COMPOSE
    # ================================================================

    def generate_docker_compose(
        self,
        repo_name: str,
        languages: List[str],
        frameworks: List[str],
        has_database: bool = False
    ) -> str:
        """
        Generate a Docker Compose file only from explicitly supplied
        project evidence.

        This method does NOT assume PostgreSQL or any other database.
        """

        languages = languages or []
        frameworks = frameworks or []

        compose_lines = [
            "services:"
        ]

        # ============================================================
        # NODE.JS SERVICE
        # ============================================================

        has_node = (
            self._has_language(languages, "JavaScript")
            or self._has_language(languages, "TypeScript")
        )

        if has_node:

            compose_lines.extend([
                "  app:",
                "    build:",
                "      context: .",
                "      dockerfile: Dockerfile",
                "    ports:",
                "      - \"3000:3000\"",
                "    volumes:",
                "      - .:/app",
                "      - /app/node_modules",
                ""
            ])

        # ============================================================
        # PYTHON SERVICE
        # ============================================================

        has_python = self._has_language(
            languages,
            "Python"
        )

        if has_python:

            compose_lines.extend([
                "  app:",
                "    build:",
                "      context: .",
                "      dockerfile: Dockerfile",
                "    ports:",
                "      - \"8000:8000\"",
                "    volumes:",
                "      - .:/app",
                ""
            ])

        # ============================================================
        # DATABASE
        # ============================================================

        if has_database:

            compose_lines.extend([
                "  db:",
                "    # Database configuration must be supplied",
                "    # from repository evidence.",
                "    image: postgres:14",
                "    environment:",
                "      POSTGRES_DB=app",
                "      POSTGRES_USER=postgres",
                "      POSTGRES_PASSWORD=postgres",
                "    ports:",
                "      - \"5432:5432\"",
                ""
            ])

        # ============================================================
        # NO SERVICE DETECTED
        # ============================================================

        if len(compose_lines) == 1:

            compose_lines.extend([
                "  app:",
                "    # No supported runtime was detected.",
                "    # Add repository-specific Docker configuration.",
                ""
            ])

        return "\n".join(compose_lines)