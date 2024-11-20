import pandas as pd
import requests

def get_tag_mapping(project_id, headers):
    """
    Fetches tags from the API and returns a mapping of tag names to tag IDs.
    """
    response = requests.get(f'https://api.morta.io/v1/project/{project_id}/tags', headers=headers)
    
    if response.status_code != 200:
        raise ValueError(f"Failed to fetch tags: {response.text}")

    tags = response.json()["data"]
    tag_name_to_id = {}
    
    for tag in tags:
        for cell in tag["cells"]:
            tag_name = cell["value"]
            tag_id = cell["id"]
            tag_name_to_id[tag_name] = tag_id

    return tag_name_to_id

def invite_users_from_excel(file_path, project_id, headers):
    """
    Reads user data from an Excel file and sends invites using the API.
    """
    # Fetch tags and create a name-to-ID mapping
    tag_name_to_id = get_tag_mapping(project_id, headers)

    # Read the Excel file into a DataFrame
    df = pd.read_excel(file_path)

    # Extract the email column
    emails = df.iloc[:, 0]  # Assuming the first column contains emails

    # Process tags: Replace tag names with their reference IDs
    tags_columns = df.columns[1:]  # Assuming all columns except the first are tags
    formatted_tags = [
        [tag_name_to_id[tag.strip()] for col in tags_columns for tag in str(row[col]).split(",") 
         if pd.notna(row[col]) and tag.strip() in tag_name_to_id]
        for _, row in df.iterrows()
    ]

    # Prepare the API payloads
    for email, tags in zip(emails, formatted_tags):
        payload = {
            "emails": [email],
            "tags": tags  # This should be a list of valid tag IDs
        }

        # Send POST request
        response = requests.post(
            f'https://api.morta.io/v1/project/{project_id}/invite-multiple',
            headers=headers,
            json=payload
        )

        # Handle response
        if response.status_code == 201:
            print(f"Successfully invited {email}")
        else:
            print(f"Failed to invite {email}: {response.text}")

# Example usage
file_path = "insert file path"  # Replace with your file path
project_id = "insert project id"  # Replace with your project ID
api_key = "insert API Key"
headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}

invite_users_from_excel(file_path, project_id, headers)
