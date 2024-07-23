import os

file_path = 'static/images/header1.png'
if os.path.exists(file_path):
    print(f"File exists at {file_path}")
else:
    print(f"File not found at {file_path}")