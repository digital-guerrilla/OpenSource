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
        print(payload)
        # Send POST request
        #response = requests.post(
            #f'https://api.morta.io/v1/project/{project_id}/invite-multiple',
            #headers=headers,
            #json=payload
        #)

        # Handle response
        #if response.status_code == 201:
            #print(f"Successfully invited {email}")
        #else:
           # print(f"Failed to invite {email}: {response.text}")

# Example usage
file_path = "D:\\temp\\BulkUserCreationTemplate.xlsx"  # Replace with your file path
project_id = "6a4f29e6-7954-4688-945e-2a8371c58da8"  # Replace with your project ID
api_key = "hg9vSr5NBGQFjwMkPqEQeSspxEkPAQp8mmRraXJLlNw"
headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}

payload = [
    {
        'email': 'andrew@digital-guerrilla.scot',
        'tags': ['table/b9d9d3b2-2f68-4dec-8ad4-e965420d4e78/3ab3cc96-da30-4449-9326-0bd179a30615/c41e7c47-6dd0-4484-b473-ac651ebd3873', 'table/4c3013a5-78b5-4011-9f40-0a601fe784a7/04e7cbe3-f43a-4b9a-85ca-56cd93d377f5/5a844c0f-2b5d-45be-bc04-174b2ca0da7a']
    }

]

users = requests.get(f'https://api.morta.io/v1/project/{project_id}/members',headers=headers)
data = users.json()["data"]
existing_emails = {entry['user']['email'] for entry in data}
email_to_firebase = {entry['user']['email']: entry['user']['firebaseUserId'] for entry in data}
userstoremove = [
    (entry['user']['firebaseUserId'], entry['user']['email'])
    for entry in data
    if entry['user']['email'] not in {item['email'] for item in payload}
]
for user_id, email in userstoremove:
    response = requests.delete(f'https://api.morta.io/v1/project/{project_id}/removeuser/{user_id}',headers=headers)
    if response.status_code == 200:
        print(f"User with email {email} removed successfully.")
    else:
        print(f"Failed to remove user with email {email}. Response: {response.text}")


invites = requests.get(f'https://api.morta.io/v1/project/{project_id}/invitedmembers',headers=headers)
data = invites.json()["data"]
existing_invites = {entry['email'] for entry in data}
invites_to_firebase = {entry['email']: entry['publicId'] for entry in data}
invitestoremove = [
    (entry['publicId'], entry['email'])
    for entry in data
    if entry['email'] not in {item['email'] for item in payload}
]
for invite_id, email in invitestoremove:
    response = requests.delete(f'https://api.morta.io/v1/project/{project_id}/invite/{invite_id}',headers=headers)
    if response.status_code == 200:
        print(f"Invite with email {email} removed successfully.")
    else:
        print(f"Failed to remove invite with email {email}. Response: {response.text}")
