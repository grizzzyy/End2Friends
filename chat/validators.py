from django.core.exceptions import ValidationError
import os

# Only these file types are allowed
ALLOWED_EXTENSIONS = {
    '.pdf', '.doc', '.docx', '.txt', '.md',
    '.png', '.jpg', '.jpeg', '.gif', '.webp',
    '.zip', '.py', '.js', '.html', '.csv',
}

MAX_FILE_SIZE = 25 * 1024 * 1024  # 25MB

def validate_uploaded_file(file):
    # Check file size
    if file.size > MAX_FILE_SIZE:
        raise ValidationError(
            f'File too large. Maximum size is 25MB.'
        )

    # Check extension
    ext = os.path.splitext(file.name)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise ValidationError(
            f'File type {ext} is not allowed.'
        )