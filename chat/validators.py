from django.core.exceptions import ValidationError
import os
import magic

ALLOWED_MIME_TYPES = {
    'application/pdf',
    'application/msword',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    'text/plain',
    'image/png',
    'image/jpeg',
    'image/gif',
    'image/webp',
    'application/zip',
    'text/csv',
}

ALLOWED_EXTENSIONS = {
    '.pdf', '.doc', '.docx', '.txt', '.md',
    '.png', '.jpg', '.jpeg', '.gif', '.webp',
    '.zip', '.py', '.js', '.html', '.csv',
}

MAX_FILE_SIZE = 25 * 1024 * 1024  # 25MB

def validate_uploaded_file(file):
    # Check file size
    if file.size > MAX_FILE_SIZE:
        raise ValidationError('File too large. Maximum size is 25MB.')

    # Check extension
    ext = os.path.splitext(file.name)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise ValidationError(f'File type {ext} is not allowed.')

    # Check actual file content using python-magic
    mime = magic.from_buffer(file.read(2048), mime=True)
    file.seek(0)  # reset file pointer after reading
    if mime not in ALLOWED_MIME_TYPES:
        raise ValidationError(f'File content type {mime} is not allowed.')