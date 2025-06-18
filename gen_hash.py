from passlib.hash import django_pbkdf2_sha256
print(django_pbkdf2_sha256.hash("test123"))