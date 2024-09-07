from rest_framework import serializers

from .models import Blog, BlogImage, BlogReview
from users.models import User

class BlogImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = BlogImage
        fields = ['image']

class DetailUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'email', 'username']

class BlogSerializer(serializers.ModelSerializer):
    user = DetailUserSerializer(read_only=True)
    images = BlogImageSerializer(required=False, many=True)
    reviews_count = serializers.SerializerMethodField()

    def get_reviews_count(self, obj):
        reviews = obj.reviews.all()
        return reviews.count()

    class Meta:
        model = Blog
        fields = '__all__'
        read_only_fields = ['user']
    
    def create(self, validated_data):
        request = self.context.get('request')
        validated_data['user'] = request.user
        images = validated_data.pop('images')
        blog = Blog.objects.create(**validated_data)
        for image_data in images:
            BlogImage.objects.create(blog=blog, image=image_data['image'])
        return blog
    
    def update(self, instance, validated_data):
        instance.title = validated_data.get('title', instance.title)
        instance.sub_title = validated_data.get('sub_title', instance.sub_title)
        instance.content = validated_data.get('content', instance.content)

        images_data = validated_data.get('images', [])
        if images_data:
            instance.images.all().delete()
            for image_data in images_data:
                BlogImage.objects.create(blog=instance, image=image_data['image'])
                
        instance.save()
        return instance

class BlogReviewSerializer(serializers.ModelSerializer):
    reviewer = DetailUserSerializer(read_only=True)
    class Meta:
        model = BlogReview
        fields = "__all__"
        read_only_fields = ['reviewer']
    
    def create(self, validated_data):
        request = self.context.get('request')
        validated_data['reviewer'] = request.user
        return super().create(validated_data)