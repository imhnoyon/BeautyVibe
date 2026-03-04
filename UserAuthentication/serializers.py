from rest_framework import serializers
from .models import User  

class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    repassword = serializers.CharField(write_only=True, min_length=8)
    is_terms_service = serializers.BooleanField(required=True)

    class Meta:
        model = User
        fields = ['full_name', 'email', 'password', 'repassword', 'is_terms_service']

    def validate(self, attrs):
        if attrs['password'] != attrs['repassword']:
            raise serializers.ValidationError({"password": "Password fields do not match."})
        if not attrs.get('is_terms_service', False):
            raise serializers.ValidationError({"is_terms_service": "You must accept the terms and conditions."})
        return attrs

    def create(self, validated_data):
        validated_data.pop('repassword')  # remove repassword

        user = User.objects.create_user(
            full_name=validated_data['full_name'],
            email=validated_data['email'],  # fixed
            password=validated_data['password'],
            is_terms_service=validated_data['is_terms_service'],
        )
        return user

#-------Google signin Serializer --------#
class GoogleSignInSerializer(serializers.Serializer):
    id_token = serializers.CharField()
    
    
    
#---------profile image serializer---------#
class ProfileImageSerializer(serializers.ModelSerializer):
    profile_picture = serializers.ImageField(use_url=True)
    class Meta:
        model = User
        fields = ['profile_picture', 'skin_tone', 'undertone', 'face_shape', 'eye_color', 'confidence_score', 'summary']