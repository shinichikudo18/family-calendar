import uuid
import secrets
from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify


class Family(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    invite_code = models.CharField(max_length=20, unique=True, editable=False)
    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True,
        related_name='created_families'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = 'families'
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.name)
            self.slug = base
            # Ensure unique slug
            existing = Family.objects.filter(slug=self.slug).exists()
            if existing:
                self.slug = f'{base}-{secrets.token_hex(3)}'
        if not self.invite_code:
            self.invite_code = secrets.token_hex(10)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class FamilyMember(models.Model):
    ROLE_CHOICES = [
        ('admin', 'Administrador'),
        ('member', 'Miembro'),
        ('viewer', 'Espectador'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    family = models.ForeignKey(
        Family, on_delete=models.CASCADE, related_name='members'
    )
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='family_memberships'
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='member')
    is_active = models.BooleanField(default=True)
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('family', 'user')
        ordering = ['-joined_at']

    def __str__(self):
        return f'{self.user.username} - {self.family.name} ({self.get_role_display()})'
