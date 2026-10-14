"""Настройка Django перед сбором тестов проекта."""
import os

import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sportsite.settings')
django.setup()
