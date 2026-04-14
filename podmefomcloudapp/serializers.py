from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Track, Like
from drf_spectacular.utils import extend_schema_field

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'avatar', 'bio', 'date_joined']
        read_only_fields = ['id', 'date_joined']


class TrackSerializer(serializers.ModelSerializer):
    artist = UserSerializer(read_only=True)
    audio_url = serializers.SerializerMethodField()
    cover_url = serializers.SerializerMethodField()

    class Meta:
        model = Track
        fields = [
            'id', 
            'title', 
            'artist', 
            'audio', 
            'audio_url',
            'cover', 
            'cover_url', 
            'description', 
            'category',
            'likes_count', 
            'status',
            'rejection_reason',
            'created_at'
        ]
        read_only_fields = ['id', 'artist', 'likes_count', 'status', 'rejection_reason', 'created_at']

    @extend_schema_field(str)
    def get_audio_url(self, obj):
        if obj.audio:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.audio.url)
            return obj.audio.url
        return None

    @extend_schema_field(str)
    def get_cover_url(self, obj):
        if obj.cover:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.cover.url)
            return obj.cover.url
        return None


class TrackCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Track
        fields = ['title', 'audio', 'cover', 'description', 'category']


class TrackModerationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Track
        fields = ['status', 'rejection_reason']