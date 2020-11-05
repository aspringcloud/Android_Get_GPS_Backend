from django.contrib.auth.forms import UserCreationForm
from .models import User
from django.contrib.auth import get_user_model
# get_user_model => AUTH_USER_MODEL에 적용시킨 모델 클래스
# 나중에도 유저 모델을 갖다 쓰고 싶으면 이걸 언급해야 한다.
# 그냥 유저로 써도 되지만, django는 최대한 유저를 쓰지 말아줬으면 해서

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = get_user_model()
        fields = ('username', 'password1', 'password2')
