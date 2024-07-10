from django.db import models

class Novel(models.Model):
    title = models.CharField(max_length=255, unique=True)
    description = models.TextField()
    author = models.CharField(max_length=255)

class Chapter(models.Model):
    LANGUAGE_CHOICES = (
        ('en', 'English'),
        ('es', 'Spanish'),
    )

    novel = models.ForeignKey(Novel, related_name='chapters', on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    content = models.TextField()
    chapter_number = models.IntegerField()
    language = models.CharField(max_length=2, choices=LANGUAGE_CHOICES, default='en')