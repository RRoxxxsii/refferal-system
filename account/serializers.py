from phonenumber_field.serializerfields import PhoneNumberField
from rest_framework import serializers

from account.models import User


class PhoneNumberInputSerializer(serializers.Serializer):
    mobile = PhoneNumberField()


class AuthCodeInputSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('auth_code',)


class InviteCodeInputSerializer(serializers.Serializer):
    invite_code = serializers.CharField(max_length=6)


class ListUserEnteredCode(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ('mobile',)
