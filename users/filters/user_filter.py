from  ..models.user import User

def filter_user_for_login(user_name,password,device_sc):
    return User.objects.filter(password=password,user_name=user_name,device_sc=device_sc)