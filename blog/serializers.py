from rest_framework import serializers

from .models import Blog, BlogImage, BlogReview, BlogTag
from users.models import User

class BlogImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = BlogImage
        fields = ['id', 'image']

class DetailUserSerializer(serializers.ModelSerializer):
    profile_pic = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'email', 'username', 'profile_pic']
    
    def get_profile_pic(self, obj):
        request = self.context.get('request')
        pp = obj.profile.profile_picture
        if pp:
            return request.build_absolute_uri(pp.url)
        return None

class BlogTagSerializer(serializers.ModelSerializer):
    class Meta:
        model = BlogTag
        fields = ['id', 'tag']

class BlogSerializer(serializers.ModelSerializer):
    tags = BlogTagSerializer(required=False, many=True)

    reviews_count = serializers.SerializerMethodField()
    likes_count = serializers.SerializerMethodField()

    def get_reviews_count(self, obj):
        reviews = obj.reviews.all()
        return reviews.count()
    
    def get_likes_count(self, obj):
        likes = obj.likes.all()
        return likes.count()

    class Meta:
        model = Blog
        fields = '__all__'
        read_only_fields = ['user', 'likes']
    
    def to_representation(self, instance):
        request = self.context.get('request')
        data = super().to_representation(instance)

        image_serializer = BlogImageSerializer(instance.images.all(), many=True, context={'request': request})
        data['images'] = [image_data['image'] for image_data in image_serializer.data]

        data['user'] = DetailUserSerializer(instance.user, read_only=True, context={'request': request}).data
        return data
    
    def create(self, validated_data):
        request = self.context.get('request')
        validated_data['user'] = request.user
        images = validated_data.pop('images', '')
        tags = validated_data.pop('tags', '')

        blog = Blog.objects.create(**validated_data)

        if images:
            blog.images.set(images)
        
        if tags:
            for tag in tags:
                BlogTag.objects.create(blog=blog, tag=tag['tag'])

        return blog
    
    def update(self, instance, validated_data):
        instance.title = validated_data.get('title', instance.title)
        instance.sub_title = validated_data.get('sub_title', instance.sub_title)
        instance.content = validated_data.get('content', instance.content)

        images_data = validated_data.pop('images', [])
        tags = validated_data.pop('tags', [])

        if images_data:
            instance.images.all().delete()
            instance.images.set(images_data)

        if tags:
            instance.tags.all().delete()
            for tag in tags:
                BlogTag.objects.create(blog=instance, tag=tag['tag'])
                
        instance.save()
        return instance

class BlogReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = BlogReview
        fields = "__all__"
        read_only_fields = ['reviewer']
    
    def validate(self, attrs):
        request = self.context.get('request')
        reviewer = request.user
        if BlogReview.objects.filter(blog=attrs.get('blog'), reviewer=reviewer).exists():
            raise serializers.ValidationError({'message':'Review already exists.'})
        return super().validate(attrs)
    
    def to_representation(self, instance):
        request = self.context.get('request')
        data = super().to_representation(instance)
        data['reviewer'] = DetailUserSerializer(instance.reviewer, read_only=True, context={'request': request}).data
        return data
    
    def create(self, validated_data):
        request = self.context.get('request')
        validated_data['reviewer'] = request.user
        return super().create(validated_data)