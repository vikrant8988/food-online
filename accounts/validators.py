from pathlib import Path
from django.core.exceptions import ValidationError

def image_type_validator(value):
    ext = Path(value.name).suffix.lower()
    print(ext)
    valid_extensions = ['.png', '.jpg', '.jpeg']
    if ext not in valid_extensions:
        raise ValidationError(f'Unsupported File extension. Allowed extensions: {", ".join(valid_extensions)}')
