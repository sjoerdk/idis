from django.db import models
from django.core.exceptions import ValidationError
from django.conf import settings

from os import urandom
from base64 import b64encode, b64decode
from Crypto.Cipher import ARC4
from django import forms


PREFIX = u'\u2620'


class EncryptedCharField(models.CharField):

    SALT_SIZE = 8

    def __init__(self, *args, **kwargs):
        self.widget = forms.TextInput
        super(EncryptedCharField, self).__init__(*args, **kwargs)

    def get_internal_type(self):
        return 'TextField'

    def to_python(self, value):
        if not value:
            return None
        if isinstance(value, str):
            if value.startswith(PREFIX):
                return self.decrypt(value)
            else:
                return value
        else:
            raise ValidationError(u'Failed to encrypt %s.' % value)

    def get_db_prep_value(self, value, connection, prepared=False):
        return self.encrypt(value)

    def value_to_string(self, instance):
        encriptado = getattr(instance, self.name)
        return self.decrypt(encriptado) if encriptado else None

    @staticmethod
    def encrypt(plaintext):
        plaintext = str(plaintext)
        salt = urandom(EncryptedCharField.SALT_SIZE)
        arc4 = ARC4.new(salt + settings.SECRET_KEY)
        plaintext = u"%3d%s%s" % (len(plaintext), plaintext, b64encode(urandom(256-len(plaintext))))
        return PREFIX + u"%s$%s" % (b64encode(salt), b64encode(arc4.encrypt(plaintext.encode('utf-8-sig'))))

    @staticmethod
    def decrypt(ciphertext):
        salt, ciphertext = map(b64decode, ciphertext[1:].split('$'))
        arc4 = ARC4.new(salt + settings.SECRET_KEY)
        plaintext = arc4.decrypt(ciphertext).decode('utf-8-sig')
        return plaintext[3:3+int(plaintext[:3].strip())]

