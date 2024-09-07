from django.db import models

from users.models import User

# Create your models here.
class Blog(models.Model):
    user = models.ForeignKey(User, related_name="blogs", on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    sub_title = models.TextField(null=True, blank=True)
    content = models.TextField()
    likes = models.ManyToManyField(User)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class BlogImage(models.Model):
    blog = models.ForeignKey(Blog, related_name="images", on_delete=models.CASCADE)
    image = models.ImageField(upload_to='blog/images/')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class BlogReview(models.Model):
    blog = models.ForeignKey(Blog, on_delete=models.CASCADE, related_name='reviews')
    reviewer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='blog_reviews')
    rating = models.PositiveIntegerField(null=True, blank=True)
    review = models.TextField()   
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
