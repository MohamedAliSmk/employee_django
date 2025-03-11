from django.utils import timezone
from django.utils.timezone import now
from django.core.exceptions import ValidationError

def validate_date(value):
    try:
        # datetime.strptime(value, '%Y-%m-%d')
        if value > timezone.now().date():
            raise ValidationError(_("The date cannot be in the future"))
    except ValueError:
        raise ValidationError(_('Invalid date - it must be in YYYY-MM-DD format.'))