from github import Github, GithubException
from typing import Dict, List, Optional
from ..config import get_settings

settings = get_settings()


class GitHubService:
    def __init__(self):
        self.client = Github(settings.github_token)

    def _extract_repo_name(self, repo_url: str) -> str:
        """Helper to extract owner/repo from URL"""
        if "github.com" in repo_url:
            parts = repo_url.split("github.com/")[-1].split("/")
            owner = parts[0]
            repo_name = parts[1].replace(".git", "")
            return f"{owner}/{repo_name}"
        return repo_url

def get_repository_context(self, repo_url: str) -> dict:
    try:
        repo_name = self._extract_repo_name(repo_url)
        repo = self.client.get_repo(repo_name)

        # ✅ Get ALL language percentages
        languages_data = repo.get_languages()
        total_bytes = sum(languages_data.values()) or 1
        language_percentages = {
            lang: round((bytes / total_bytes) * 100, 1)
            for lang, bytes in languages_data.items()
        }

        # ✅ Get topics/tags
        try:
            topics = repo.get_topics()
        except:
            topics = []

        # ✅ Get license
        try:
            license_name = repo.license.name if repo.license else "Not specified"
        except:
            license_name = "Not specified"

        # ✅ Get contributors count
        try:
            contributors_count = repo.get_contributors().totalCount
        except:
            contributors_count = 1

        # Build complete context
        context = {
            # Basic info
            "name": repo.name,
            "full_name": repo.full_name,
            "description": repo.description or "",
            "url": repo.html_url,

            # Stats - ALL real numbers
            "stars": repo.stargazers_count,
            "forks": repo.forks_count,
            "watchers": repo.watchers_count,
            "open_issues": repo.open_issues_count,
            "contributors": contributors_count,

            # Languages with percentages
            "languages": list(languages_data.keys()),
            "language_percentages": language_percentages,
            "primary_language": repo.language or "",

            # Metadata
            "topics": topics,
            "license": license_name,
            "default_branch": repo.default_branch,
            "created_at": repo.created_at.strftime("%B %Y"),
            "last_updated": repo.updated_at.strftime("%B %d, %Y"),

            # File contents (read below)
            "existing_readme": "",
            "requirements": "",
            "package_json": "",
            "main_file_content": "",
            "main_file_name": "",
            "all_files": []
        }

        # Get root file list
        try:
            root_contents = repo.get_contents("")
            context["all_files"] = [f.path for f in root_contents]
        except:
            pass

        # Read README
        for readme_name in ["README.md", "readme.md", "README.txt"]:
            try:
                f = repo.get_contents(readme_name)
                context["existing_readme"] = f.decoded_content.decode("utf-8")[:3000]
                print(f"✅ Found {readme_name}")
                break
            except:
                pass

        # Read requirements.txt
        for req_name in ["requirements.txt", "Requirements.txt"]:
            try:
                f = repo.get_contents(req_name)
                context["requirements"] = f.decoded_content.decode("utf-8")[:1000]
                print(f"✅ Found {req_name}")
                break
            except:
                pass

        # Read package.json
        try:
            f = repo.get_contents("package.json")
            context["package_json"] = f.decoded_content.decode("utf-8")[:1000]
            print("✅ Found package.json")
        except:
            pass

        # Read main file
        for filename in ["app.py", "App.py", "main.py", "index.py",
                         "app.js", "index.js", "server.py", "run.py"]:
            try:
                f = repo.get_contents(filename)
                context["main_file_content"] = f.decoded_content.decode("utf-8")[:2000]
                context["main_file_name"] = filename
                print(f"✅ Found main file: {filename}")
                break
            except:
                pass

        # Summary log
        print(f"\n📊 Context for {context['name']}:")
        print(f"   ⭐ Stars: {context['stars']}")
        print(f"   🍴 Forks: {context['forks']}")
        print(f"   👁️  Watchers: {context['watchers']}")
        print(f"   🔤 Languages: {context['language_percentages']}")
        print(f"   📜 License: {context['license']}")
        print(f"   🏷️  Topics: {context['topics']}")
        print(f"   README: {'✅' if context['existing_readme'] else '❌'}")
        print(f"   Requirements: {'✅' if context['requirements'] else '❌'}")

        return context

    except Exception as e:
        print(f"Error: {e}")
        return {}


    def get_file_content(self, repo_url: str, file_path: str):

        try:
            repo_name = self._extract_repo_name(repo_url)

            repo = self.client.get_repo(repo_name)

            file_content = repo.get_contents(file_path)

            return file_content.decoded_content.decode("utf-8")

        except Exception as e:
            print(f"Error fetching file: {e}")

            return None


    def detect_tech_stack(self, repo_url: str):

        tech_stack = {
            "languages": [],
            "frameworks": [],
            "databases": [],
            "tools": []
        }

        try:
            repo_info = self.get_repository(repo_url)

            if repo_info:
                tech_stack["languages"] = repo_info["languages"]

            repo_name = self._extract_repo_name(repo_url)

            repo = self.client.get_repo(repo_name)

            root_contents = repo.get_contents("")

            for file_content in root_contents:

                filename = file_content.path.split("/")[-1]

                if filename == "requirements.txt":

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

                    except:
                        pass

                if filename == "package.json":

                    try:
                        content = (
                            file_content.decoded_content
                            .decode("utf-8")
                            .lower()
                        )

                        if "react" in content:
                            tech_stack["frameworks"].append("React")

                        if "next" in content:
                            tech_stack["frameworks"].append("Next.js")

                        if "express" in content:
                            tech_stack["frameworks"].append("Express")

                    except:
                        pass

            tech_stack["frameworks"] = list(set(tech_stack["frameworks"]))

            return tech_stack

        except Exception as e:
            print(f"Error detecting tech stack: {e}")

            return tech_stack


    def get_repository_context(self, repo_url: str) -> dict:

        try:
            repo_name = self._extract_repo_name(repo_url)

            repo = self.client.get_repo(repo_name)

            context = {
                "name": repo.name,
                "description": repo.description or "",
                "languages": list(repo.get_languages().keys()),
                "stars": repo.stargazers_count,
                "existing_readme": "",
                "requirements": "",
                "package_json": "",
                "main_file_content": "",
                "main_file_name": "",
                "all_files": []
            }

            try:
                root_contents = repo.get_contents("")

                context["all_files"] = [
                    f.path for f in root_contents
                    if hasattr(f, 'path')
                ]

            except:
                pass

            for readme_name in ["README.md", "readme.md"]:

                try:
                    f = repo.get_contents(readme_name)

                    context["existing_readme"] = (
                        f.decoded_content.decode("utf-8")[:3000]
                    )

                    break

                except:
                    pass

            for req_name in ["requirements.txt"]:

                try:
                    f = repo.get_contents(req_name)

                    context["requirements"] = (
                        f.decoded_content.decode("utf-8")[:1000]
                    )

                    break

                except:
                    pass

            try:
                f = repo.get_contents("package.json")

                context["package_json"] = (
                    f.decoded_content.decode("utf-8")[:1000]
                )

            except:
                pass

            main_file_candidates = [
                "app.py",
                "main.py",
                "server.py",
                "index.js"
            ]

            for filename in main_file_candidates:

                try:
                    f = repo.get_contents(filename)

                    context["main_file_content"] = (
                        f.decoded_content.decode("utf-8")[:2000]
                    )

                    context["main_file_name"] = filename

                    break

                except:
                    pass

            return context

        except Exception as e:
            print(f"Error getting context: {e}")

            return {}