from rest_framework import serializers

class HtmlToPdfSerializer(serializers.Serializer):
    id_arborescence = serializers.IntegerField()
    user_ref = serializers.CharField()
    docFormat = serializers.CharField()  # raw HTML
    description = serializers.CharField()
    orientation = serializers.ChoiceField(choices=['portrait', 'paysage'], required=False, default='portrait')
