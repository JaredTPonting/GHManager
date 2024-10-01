import requests
import argparse
import os
import yaml
import base64
from pathlib import Path
from cryptography.fernet import Fernet
from getpass import getpass


def generate_key():
    return Fernet.generate_key()


def encrypt_token(token, key):
    fernet = Fernet(key)
    return fernet.encrypt(token.encode()).decode()


def decrypt_token(encrypted_token, key):
    fernet = Fernet(key)
    return fernet.decrypt(encrypted_token.encode()).decode()


def setup_github_manager():
    token = getpass("Enter your GitHub token: ").strip()
    username = input("Enter your GitHub username: ").strip()

    # Generate key and store it securely
    # key = generate_key()
    #
    # # Encrypt the token using the generated key
    # encrypted_token = encrypt_token(token, key)

    # Save username, encrypted token, and encryption key to a YAML config file
    config_data = {
        "username": username,
        "token": token,
        # "encryption_key": base64.urlsafe_b64encode(key).decode()  # Encode key to save as string
    }

    config_file = os.path.expanduser("~/.github_config.yaml")
    with open(config_file, "w") as file:
        yaml.dump(config_data, file)

    print(f"Setup complete! Configuration saved to {config_file}")


def load_config():
    config_file = os.path.expanduser("~/.github_config.yaml")

    if os.path.exists(config_file):
        with open(config_file, "r") as file:
            config = yaml.safe_load(file)

        # Extract the encrypted token and key from the config
        # encrypted_token = config.get("encrypted_token")
        # encryption_key = base64.urlsafe_b64decode(config.get("encryption_key").encode())

        # Decrypt the token
        # decrypted_token = decrypt_token(encrypted_token, encryption_key)

        return {
            "username": config.get("username"),
            "token": config.get("token")
        }
    else:
        print(f"Configuration file not found. Run the setup action to store your details.")
        return None


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


def change_repo_visibility(token, user_name, repo_name, visibility):
    url = f"https://api.github.com/repos/{user_name}/{repo_name}"
    headers = {"Authorization": f"token {token}"}
    data = {"visibility": visibility}

    response = requests.patch(url, json=data, headers=headers)
    if response.status_code == 200:
        print(f"Visibility of {repo_name} has been changed to {visibility}.")
    else:
        print(f"Failed to change visibility: {response.status_code}")


def get_issues(token, username, repo_name):
    url = f"https://api.github.com/repos/{username}/{repo_name}/issues"
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
    parser.add_argument("action", choices=["list", "visibility", "issues", "setup"], help="Action to perform")
    parser.add_argument("--token", help="GitHub personal access token (option)")
    parser.add_argument("--username", help="GitHub username (option)")
    parser.add_argument("--repo", help="Repository name (required for visibility and issues)")
    parser.add_argument("--visibility", choices=["public", "private"], help="Visibility to be set")

    args = parser.parse_args()
    config = load_config()
    if config:
        token = config["token"]
        username = config["username"]
    else:
        token = args.token
        username = args.username
    if not token:
        print("Github token is required. Use --token or run setup action to save to config.")

    if args.action == "setup":
        setup_github_manager()
    elif args.action == "list":
        list_repos(token)
    elif args.action == "visibility":
        if args.repo and args.visibility and username:
            change_repo_visibility(token, username, args.repo, args.visibility)
        else:
            print("--repo and --visibility and --username are required for this action. (or store username with setup)")
    elif args.action == "issues":
        if args.repo and username:
            get_issues(token, username, args.repo)
        else:
            print("both --repo and --username are required for this action. (or store username with setup)")


if __name__ == "__main__":
    main()
