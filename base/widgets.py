from django.contrib.admin.widgets import AdminFileWidget
from django.utils.safestring import mark_safe

class AdminImageWidget(AdminFileWidget):
    def render(self, name, value, attrs=None, renderer=None):
        output = []
        if value and getattr(value, "url", None):
            image_url = value.url
            file_name = str(value)
            # Render the image preview with a link to the original image
            output.append(
                f'<a href="{image_url}" target="_blank">'
                f'<img src="{image_url}" alt="{file_name}" width="150" height="150" style="object-fit: cover; border: 1px solid #ddd; margin: 5px;" />'
                f'</a>'
            )
        # Render the default file input field
        output.append(super().render(name, value, attrs, renderer))
        return mark_safe(''.join(output))
