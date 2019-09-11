# main site(portal)의 blueprint를 등록하는 스크립트 파일
from flask import Blueprint

main = Blueprint('main', __name__)

from . import views