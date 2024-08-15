import subprocess

def list_terraform_resources():
    try:
        result = subprocess.run(['terraform', 'state', 'list'], capture_output=True, text=True, check=True)
        return result.stdout.splitlines()
    except subprocess.CalledProcessError as e:
        print(f"Error listing resources: {e}")
        return []

def remove_resource(resource_name):
    try:
        subprocess.run(['terraform', 'state', 'rm', resource_name], check=True)
        print(f"Successfully removed {resource_name} from state")
    except subprocess.CalledProcessError as e:
        print(f"Error removing resource {resource_name}: {e}")

def main():
    resources = list_terraform_resources()

    for resource in resources:
        if "github_repository_tag_protection.default" in resource:
            remove_resource(resource)

if __name__ == "__main__":
    main()
