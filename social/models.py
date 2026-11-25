```python
"""
Modelos principales de CodeSphere.
"""

from django.db import models
from django.contrib.auth.models import User


class Post(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="posts"
    )
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}: {self.content[:40]}"

    @property
    def likes_count(self):
        return self.likes.count()


class Like(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="post_likes"
    )
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name="likes"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "post"],
                name="unique_user_post_like"
            )
        ]

    def __str__(self):
        return f"{self.user.username} - publicación {self.post_id}"


class Profile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="profile"
    )
    bio = models.TextField(blank=True)

    def __str__(self):
        return f"Perfil de {self.user.username}"
```
