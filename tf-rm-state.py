import subprocess
import re

def list_terraform_resources():
    try:
        # List all resources in the state
        result = subprocess.run(['terraform', 'state', 'list'], capture_output=True, text=True, check=True)
        return result.stdout.splitlines()
    except subprocess.CalledProcessError as e:
        print(f"Error listing resources: {e}")
        return []

def remove_resource(resource_name):
    print(resource_name)
    # try:
    #     # Remove the resource from the state
    #     subprocess.run(['terraform', 'state', 'rm', resource_name], check=True)
    #     print(f"Successfully removed {resource_name} from state")
    # except subprocess.CalledProcessError as e:
    #     print(f"Error removing resource {resource_name}: {e}")

def main():
    # Define the pattern to match the resources
    pattern = re.compile(r'^module\.[^\.]+\.[^\.]+\.github_tag_protection\.default$')

    # List all resources
    resources = list_terraform_resources()

    # Filter resources based on the pattern
    for resource in resources:
        if pattern.match(resource):
            remove_resource(resource)

if __name__ == "__main__":
    main()
