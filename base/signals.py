import os
from django.db.models.signals import post_delete, pre_save
from django.dispatch import receiver
from .models import Employee

@receiver(post_delete, sender=Employee)
def auto_delete_image_on_delete(sender, instance, **kwargs):
    if instance.employee_image and instance.employee_image.name:
        image_path = instance.employee_image.path
        if os.path.isfile(image_path):
            os.remove(image_path)
            print(f"[DELETED] {image_path}")

@receiver(pre_save, sender=Employee)
def auto_delete_image_on_change(sender, instance, **kwargs):
    if not instance.pk:
        return

    try:
        old_instance = Employee.objects.get(pk=instance.pk)
    except Employee.DoesNotExist:
        return

    old_file = old_instance.employee_image
    new_file = instance.employee_image

    if old_file and old_file != new_file:
        if os.path.isfile(old_file.path):
            os.remove(old_file.path)
            print(f"[UPDATED] Deleted old image: {old_file.path}")
