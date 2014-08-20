from django import forms
from django.db import models
from models import Verse, RangeError

class VerseFormField(forms.Field):
    def clean(self, value):
        """Form field for custom validation entering verses"""

        try:
            verse = Verse(value)
        except (RangeError, Exception) as err:
            raise forms.ValidationError(err.__str__())

        # return the cleaned and processed data
        return str(verse)


class VerseField(models.Field):
    description = "A scripture reference to a specific verse"
    empty_strings_allowed = False
    __metaclass__ = models.SubfieldBase

    def __init__(self, *args, **kwargs):
        kwargs['max_length'] = 104
        super(VerseField, self).__init__(*args, **kwargs)

    def db_type(self):
        return 'varchar(%s)' % self.max_length

    def get_internal_type(self):
        return "VerseField"

    def to_python(self, value):
        if value is None:
            return value

        try:
            return Verse(value)
        except (RangeError, Exception) as err:
            raise forms.ValidationError(err.__str__())

    def get_db_prep_lookup(self, lookup_type, value):
        # For "__book", "__chapter", and "__verse" lookups, convert the value
        # to an int so the database backend always sees a consistent type.
        if lookup_type in ('book', 'verse', 'chapter'):
            return [int(value)]
        return super(VerseField, self).get_db_prep_lookup(lookup_type, value)

    def get_db_prep_value(self, value):
        # Casts dates into a string for saving to db
        return str(value)

    def value_to_string(self, obj):
        val = self._get_val_from_obj(obj)
        return self.get_db_prep_value(val)

    def formfield(self, **kwargs):
        defaults = {'form_class': VerseFormField}
        defaults.update(kwargs)
        return super(VerseField, self).formfield(**defaults)
