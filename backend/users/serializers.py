from django.contrib.auth import get_user_model
from rest_framework import serializers
from backend.tagging.models import ClientTag
from backend.tagging.serializers import TagSerializer

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False)
    role = serializers.CharField(write_only=True, required=False)
    client_tags = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'is_active', 'is_staff', 'is_superuser', 'password', 'role', 'client_tags']
        read_only_fields = ['id', 'is_superuser', 'client_tags']

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        role = validated_data.pop('role', None)
        user = super().create(validated_data)
        if password:
            user.set_password(password)
        if role:
            if role == 'admin':
                user.is_staff = True
                user.is_superuser = True
            elif role == 'employee':
                user.is_staff = True
            elif role == 'client':
                user.is_staff = False
            # Add more role logic as needed
        user.save()
        return user

    def get_client_tags(self, obj):
        # Only return tags for client users
        if obj.is_staff or obj.is_superuser:
            return []
        tag_qs = ClientTag.objects.filter(client=obj).select_related('tag')
        return [
            {
                'id': ct.id,
                'client': obj.id,
                'tag': TagSerializer(ct.tag).data,
            }
            for ct in tag_qs
        ]
