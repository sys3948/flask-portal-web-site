# application 설정 스크립트 파일

class Config:
    # 공통 설정 class
    SECRET_KEY = 'secret key in flask'
    PROFILE_PATH = 'app/static/profile'


class DevelopConfig(Config):
    # 개발시 설정 class
    SQLALCHEMY_DATABASE_URI ='database uri'
    SQLALCHEMY_TRACK_MODIFICATIONS = False


# 설정 class를 호출하는 config dictionary
config = {
    'default':DevelopConfig
}