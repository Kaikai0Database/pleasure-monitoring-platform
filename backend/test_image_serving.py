from app import create_app
import os

app = create_app()

filename = "1_20260125_001124_704296_081abad5633ab925.png"
url = f"/uploads/diary_images/{filename}"
upload_folder = os.path.join(os.path.dirname(os.path.abspath('app/__init__.py')), 'uploads', 'diary_images')

print(f"Debug: Expected Upload Folder: {upload_folder}")
full_path = os.path.join(upload_folder, filename)
print(f"Debug: File Exists? {os.path.exists(full_path)}")

with app.test_client() as client:
    response = client.get(url)
    print(f"GET {url} Status: {response.status_code}")
    if response.status_code != 200:
        print(f"Response: {response.data}")
