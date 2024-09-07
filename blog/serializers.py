from rest_framework import serializers

from .models import Blog, BlogImage

class BlogImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = BlogImage
        fields = ['image']

class BlogSerializer(serializers.ModelSerializer):
    images = BlogImageSerializer(required=False, many=True)

    class Meta:
        model = Blog
        fields = '__all__'
        read_only_fields = ['user']

    def create(self, validated_data):
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