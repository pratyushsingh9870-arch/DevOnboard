from github import Github, GithubException
from typing import Dict, List, Optional

from ..config import get_settings


settings = get_settings()


class GitHubService:

    def __init__(self):
        self.client = Github(settings.github_token)

    # ============================================================
    # HELPER
    # ============================================================

    def _extract_repo_name(self, repo_url: str) -> str:
        """
        Extract owner/repository from a GitHub URL.

        Examples:
        https://github.com/facebook/react
        -> facebook/react

        https://github.com/facebook/react.git
        -> facebook/react

        facebook/react
        -> facebook/react
        """

        if not repo_url:
            raise ValueError("Repository URL cannot be empty")

        repo_url = repo_url.strip().rstrip("/")

        if "github.com/" in repo_url:
            parts = repo_url.split("github.com/")[-1].split("/")

            if len(parts) < 2:
                raise ValueError("Invalid GitHub repository URL")

            owner = parts[0]
            repo_name = parts[1].replace(".git", "")

            return f"{owner}/{repo_name}"

        return repo_url.replace(".git", "")

    # ============================================================
    # BASIC REPOSITORY INFORMATION
    # ============================================================

    def get_repository(self, repo_url: str) -> dict:
        """
        Get basic repository information from GitHub.
        """

        try:
            repo_name = self._extract_repo_name(repo_url)

            repo = self.client.get_repo(repo_name)

            languages_data = repo.get_languages()

            return {
                "name": repo.name,
                "full_name": repo.full_name,
                "url": repo.html_url,
                "description": repo.description or "",
                "primary_language": repo.language or "",
                "languages": [
                    lang
                    for lang, byte_count in languages_data.items()
                    if isinstance(byte_count, (int, float))
                ],
                "stars": repo.stargazers_count,
                "forks": repo.forks_count,
            }

        except GithubException as e:
            print(f"GitHub API error: {e}")
            return {}

        except Exception as e:
            print(f"Error fetching repository: {e}")
            return {}

    # ============================================================
    # REPOSITORY STRUCTURE
    # ============================================================

    def get_repository_structure(self, repo_url: str) -> List[dict]:
        """
        Get the repository file/folder structure.

        Returns a list like:

        [
            {
                "path": "README.md",
                "type": "file",
                "name": "README.md"
            },
            {
                "path": "src",
                "type": "dir",
                "name": "src"
            }
        ]
        """

        try:
            repo_name = self._extract_repo_name(repo_url)

            repo = self.client.get_repo(repo_name)

            root_contents = repo.get_contents("")

            structure = []

            for item in root_contents:
                structure.append({
                    "path": item.path,
                    "type": item.type,
                    "name": item.name,
                })

            return structure

        except GithubException as e:
            print(f"GitHub API error while getting structure: {e}")
            return []

        except Exception as e:
            print(f"Error getting repository structure: {e}")
            return []

    # ============================================================
    # DETAILED REPOSITORY CONTEXT
    # ============================================================

    def get_repository_context(self, repo_url: str) -> dict:
        """
        Get detailed repository context for AI documentation.
        """

        try:
            repo_name = self._extract_repo_name(repo_url)

            repo = self.client.get_repo(repo_name)

            # ----------------------------------------------------
            # Languages
            # ----------------------------------------------------

            languages_data = repo.get_languages()

            # Keep only actual language byte counts.
            # GitHub may sometimes return extra metadata such as "url".
            languages_data = {
                lang: byte_count
                for lang, byte_count in languages_data.items()
                if isinstance(byte_count, (int, float))
            }

            total_bytes = sum(languages_data.values()) or 1

            language_percentages = {
                lang: round((byte_count / total_bytes) * 100, 1)
                for lang, byte_count in languages_data.items()
            }

            # ----------------------------------------------------
            # Topics
            # ----------------------------------------------------

            try:
                topics = repo.get_topics()
            except Exception:
                topics = []

            # ----------------------------------------------------
            # License
            # ----------------------------------------------------

            try:
                license_name = (
                    repo.license.name
                    if repo.license
                    else "Not specified"
                )
            except Exception:
                license_name = "Not specified"

            # ----------------------------------------------------
            # Contributors
            # ----------------------------------------------------

            try:
                contributors_count = repo.get_contributors().totalCount
            except Exception:
                contributors_count = 1

            # ----------------------------------------------------
            # Base context
            # ----------------------------------------------------

            context = {
                # Basic information
                "name": repo.name,
                "full_name": repo.full_name,
                "description": repo.description or "",
                "url": repo.html_url,

                # Repository statistics
                "stars": repo.stargazers_count,
                "forks": repo.forks_count,
                "watchers": repo.watchers_count,
                "open_issues": repo.open_issues_count,
                "contributors": contributors_count,

                # Languages
                "languages": list(languages_data.keys()),
                "language_percentages": language_percentages,
                "primary_language": repo.language or "",

                # Metadata
                "topics": topics,
                "license": license_name,
                "default_branch": repo.default_branch,

                "created_at": (
                    repo.created_at.strftime("%B %Y")
                    if repo.created_at
                    else ""
                ),

                "last_updated": (
                    repo.updated_at.strftime("%B %d, %Y")
                    if repo.updated_at
                    else ""
                ),

                # File information
                "existing_readme": "",
                "requirements": "",
                "package_json": "",
                "main_file_content": "",
                "main_file_name": "",
                "all_files": [],
            }

            # ----------------------------------------------------
            # Get repository structure
            # ----------------------------------------------------

            try:
                root_contents = repo.get_contents("")

                context["all_files"] = [
                    item.path
                    for item in root_contents
                    if hasattr(item, "path")
                ]

            except Exception as e:
                print(f"Could not read repository structure: {e}")

            # ----------------------------------------------------
            # Read README
            # ----------------------------------------------------

            for readme_name in [
                "README.md",
                "readme.md",
                "README.txt",
            ]:

                try:
                    file = repo.get_contents(readme_name)

                    context["existing_readme"] = (
                        file.decoded_content
                        .decode("utf-8")[:3000]
                    )

                    print(f"Found {readme_name}")

                    break

                except Exception:
                    pass

            # ----------------------------------------------------
            # Read requirements.txt
            # ----------------------------------------------------

            for requirements_name in [
                "requirements.txt",
                "Requirements.txt",
            ]:

                try:
                    file = repo.get_contents(requirements_name)

                    context["requirements"] = (
                        file.decoded_content
                        .decode("utf-8")[:1000]
                    )

                    print(f"Found {requirements_name}")

                    break

                except Exception:
                    pass

            # ----------------------------------------------------
            # Read package.json
            # ----------------------------------------------------

            try:
                file = repo.get_contents("package.json")

                context["package_json"] = (
                    file.decoded_content
                    .decode("utf-8")[:1000]
                )

                print("Found package.json")

            except Exception:
                pass

            # ----------------------------------------------------
            # Find main file
            # ----------------------------------------------------

            main_file_candidates = [
                "app.py",
                "App.py",
                "main.py",
                "index.py",
                "app.js",
                "index.js",
                "server.py",
                "run.py",
            ]

            for filename in main_file_candidates:

                try:
                    file = repo.get_contents(filename)

                    context["main_file_content"] = (
                        file.decoded_content
                        .decode("utf-8")[:2000]
                    )

                    context["main_file_name"] = filename

                    print(f"Found main file: {filename}")

                    break

                except Exception:
                    pass

            # ----------------------------------------------------
            # Debug summary
            # ----------------------------------------------------

            print(f"\nContext for {context['name']}:")
            print(f"Stars: {context['stars']}")
            print(f"Forks: {context['forks']}")
            print(f"Watchers: {context['watchers']}")
            print(f"Languages: {context['language_percentages']}")
            print(f"License: {context['license']}")
            print(f"Topics: {context['topics']}")

            print(
                f"README: "
                f"{'Yes' if context['existing_readme'] else 'No'}"
            )

            print(
                f"Requirements: "
                f"{'Yes' if context['requirements'] else 'No'}"
            )

            print(
                f"Files found: "
                f"{len(context['all_files'])}"
            )

            return context

        except GithubException as e:
            print(f"GitHub API error while getting context: {e}")
            return {}

        except Exception as e:
            print(f"Error getting repository context: {e}")
            return {}

    # ============================================================
    # GET FILE CONTENT
    # ============================================================

    def get_file_content(
        self,
        repo_url: str,
        file_path: str
    ) -> Optional[str]:
        """
        Get the content of a specific file from a repository.
        """

        try:
            repo_name = self._extract_repo_name(repo_url)

            repo = self.client.get_repo(repo_name)

            file_content = repo.get_contents(file_path)

            # get_contents() can return a list for directories
            if isinstance(file_content, list):
                print(f"{file_path} is a directory, not a file")
                return None

            return (
                file_content.decoded_content
                .decode("utf-8")
            )

        except GithubException as e:
            print(f"GitHub API error while fetching file: {e}")
            return None

        except Exception as e:
            print(f"Error fetching file: {e}")
            return None

    # ============================================================
    # DETECT TECH STACK
    # ============================================================

    def detect_tech_stack(self, repo_url: str) -> dict:
        """
        Detect technologies from repository languages,
        requirements.txt and package.json.
        """

        tech_stack = {
            "languages": [],
            "frameworks": [],
            "databases": [],
            "tools": [],
        }

        try:

            # ----------------------------------------------------
            # Languages from GitHub
            # ----------------------------------------------------

            repo_info = self.get_repository(repo_url)

            if repo_info:
                tech_stack["languages"] = repo_info.get(
                    "languages",
                    []
                )

            # ----------------------------------------------------
            # Get repository
            # ----------------------------------------------------

            repo_name = self._extract_repo_name(repo_url)

            repo = self.client.get_repo(repo_name)

            root_contents = repo.get_contents("")

            # ----------------------------------------------------
            # Inspect files
            # ----------------------------------------------------

            for file_content in root_contents:

                filename = file_content.path.split("/")[-1]

                # =================================================
                # Python dependencies
                # =================================================

                if filename.lower() == "requirements.txt":

                    try:
                        content = (
                            file_content.decoded_content
                            .decode("utf-8")
                            .lower()
                        )

                        if "django" in content:
                            tech_stack["frameworks"].append("Django")

                        if "flask" in content:
                            tech_stack["frameworks"].append("Flask")

                        if "fastapi" in content:
                            tech_stack["frameworks"].append("FastAPI")

                        if "sqlalchemy" in content:
                            tech_stack["tools"].append("SQLAlchemy")

                        if "streamlit" in content:
                            tech_stack["frameworks"].append(
                                "Streamlit"
                            )

                        if "tensorflow" in content:
                            tech_stack["tools"].append(
                                "TensorFlow"
                            )

                        if "torch" in content or "pytorch" in content:
                            tech_stack["tools"].append(
                                "PyTorch"
                            )

                    except Exception:
                        pass

                # =================================================
                # JavaScript dependencies
                # =================================================

                if filename.lower() == "package.json":

                    try:
                        content = (
                            file_content.decoded_content
                            .decode("utf-8")
                            .lower()
                        )

                        if '"react"' in content:
                            tech_stack["frameworks"].append(
                                "React"
                            )

                        if '"next"' in content:
                            tech_stack["frameworks"].append(
                                "Next.js"
                            )

                        if '"express"' in content:
                            tech_stack["frameworks"].append(
                                "Express"
                            )

                        if '"vite"' in content:
                            tech_stack["tools"].append(
                                "Vite"
                            )

                        if '"tailwindcss"' in content:
                            tech_stack["tools"].append(
                                "Tailwind CSS"
                            )

                    except Exception:
                        pass

            # ----------------------------------------------------
            # Remove duplicates
            # ----------------------------------------------------

            tech_stack["languages"] = list(
                dict.fromkeys(tech_stack["languages"])
            )

            tech_stack["frameworks"] = list(
                dict.fromkeys(tech_stack["frameworks"])
            )

            tech_stack["databases"] = list(
                dict.fromkeys(tech_stack["databases"])
            )

            tech_stack["tools"] = list(
                dict.fromkeys(tech_stack["tools"])
            )

            return tech_stack

        except GithubException as e:
            print(f"GitHub API error while detecting tech stack: {e}")
            return tech_stack

        except Exception as e:
            print(f"Error detecting tech stack: {e}")
            return tech_stack