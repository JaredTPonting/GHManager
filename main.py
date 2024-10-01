import requests
import argparse
import os
import yaml


def load_config():
    config_file = os.path.expanduser("~/.github_config.yaml")
    if os.path.exists(config_file):
        with open(config_file, "r") as file:
            config = yaml.safe_load(file)
            return config.get("github_token")
    return None


def save_token_to_config(token):
    config_file = os.path.expanduser("~/.github_config.yaml")
    config = {"github_token": token}
    with open(config_file, "w") as file:
        yaml.safe_dump(config, file)
    print("Token saved to config file.")


# def save_repository_to_config():
#     config_file = os.path.expanduser("~/.github_config.yaml")


def list_repos(token):
    url = "https://api.github.com/user/repos"

    headers = {"Authorization": f"token {token}"}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        repos = response.json()
        for repo in repos:
            print(f"{repo['name']} - {repo['visibility']}")
    else:
        print(f"Failed to fetch repositories: {response.status_code}")


def change_repo_visibility(token, repo_name, visibility):
    url = f"https://api.github.com/repos/JaredTPonting/{repo_name}"
    headers = {"Authorization": f"token {token}"}
    data = {"visibility": visibility}

    response = requests.patch(url, json=data, headers=headers)
    if response.status_code == 200:
        print(f"Visibility of {repo_name} has been changed to {visibility}.")
    else:
        print(f"Failed to change visibility: {response.status_code}")


def get_issues(token, repo_name):
    url = f"https://api.github.com/repos/JaredTPonting/{repo_name}/issues"
    headers = {"Authorization": f"token {token}"}

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        issues = response.json()
        for issue in issues:
            print(f"Issue #{issue['number']}: {issue['title']} (State: {issue['state']})")
    else:
        print(f"Failed to fetch issues: {response.status_code}")


def main():
    parser = argparse.ArgumentParser(description="Github Repository manager")
    parser.add_argument("action", choices=["list", "visibility", "issues", "set-token"], help="Action to perform")
    parser.add_argument("--token", help="GitHub personal access token (option)")
    parser.add_argument("--repo", help="Repository name (required for visibility and issues)")
    parser.add_argument("--visibility", choices=["public", "private"], help="Visibility to be set")

    args = parser.parse_args()

    token = args.token or load_config()
    if not token:
        print("Github token is required. Use --token or save it in the config.")

    if args.action == "list":
        list_repos(token)
    elif args.action == "set-token":
        if args.token:
            save_token_to_config(args.token)
        else:
            print("--token is required to save it to the config")
    elif args.action == "visibility":
        if args.repo and args.visibility:
            change_repo_visibility(token, args.repo, args.visibility)
        else:
            print("both --repo and --visibility are required for this action.")
    elif args.action == "issues":
        if args.repo:
            get_issues(token, args.repo)


if __name__ == "__main__":
    main()
