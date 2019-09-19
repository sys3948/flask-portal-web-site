# main page의 route & view function들이 있는 스크립트 파일
from flask import current_app, flash, request, redirect, session, render_template, url_for, jsonify
from . import main
from ..models import User
from .. import db
from sqlalchemy.sql.expression import func
import os


@main.route('/')
def index():
    # 메인 페이지 뷰함수
    user = None
    if 'id' in session:
        user = User.query.filter_by(id = session['id']).first_or_404()

    return render_template('main/index.html', user = user)


@main.route('/login', methods=['GET', 'POST'])
def login():
    # 로그인 뷰함수
    if request.method == 'POST':
        id = request.form['id']
        pw = request.form['pw']
        password_hash = db.session.query(func.sha2(pw, 224))
        user = User.query.filter_by(user_id = id, password_hash = password_hash).first()

        if not user:
            flash('존재하지 않는 아이디거나, 비밀번호가 옳바르지 않습니다.')
            return redirect(url_for('.login'))

        session['id'] = user.id

        return redirect(url_for('.index'))

    return render_template('main/login.html')


@main.route('/register', methods =['GET', 'POST'])
def register():
    # 회원가입 뷰함수
    if request.method == "POST":
        # ajax 통신을 할 경우(http method == post)
        data = request.get_json()

        if 'id' in data:
            # id 중복체크
            user = User.query.filter_by(user_id = data['id']).first()

            if user:
                return jsonify(data = False)
            else:
                return jsonify(data = True)

        elif 'userName' in data:
            # 닉네임 중복체크
            user = User.query.filter_by(username = data['userName']).first()

            if user:
                return jsonify(data = False)
            else:
                return jsonify(data = True)

        elif 'form' in data:
            # 회원가입 submit
            try:
                password_hash = db.session.query(func.sha2(data["form"]["password"], 224))
                user = User(user_id = data['form']['id'], username = data["form"]["username"], password_hash = password_hash)
                db.session.add(user)
                db.session.commit()
                os.mkdir(os.path.join(current_app.config['PROFILE_PATH'], user.user_id))
            except Exception as e:
                return jsonify(data = False, msg = e)

            return jsonify(data = True)

    return render_template('main/register.html')


@main.route('/search', methods=['GET', 'POST'])
def search():
    # 비밀번호 찾기 뷰함수
    if not 'id' in session:
        if request.method == 'POST':
            # 아이디 검색
            id = request.form['id']
            user = User.query.filter_by(user_id = id).first_or_404()

            session['id'] = user.id
            session['url'] = 'search'

            return redirect(url_for('.reset'))
        return render_template('main/search_password.html')

    else:
        flash('로그인이 되어있습니다.')
        return redirect(url_for('.index'))


@main.route('/reset', methods=['GET', 'POST'])
def reset():
    # 비밀번호 변경 뷰함수
    if 'id' in session:
        if request.method == 'POST':
            # 비밀번호 변경
            user = User.query.filter_by(id = session['id']).first()
            password_hash = db.session.query(func.sha2(request.form['pw'], 224))
            user.password_hash = password_hash
            db.session.commit()
            flash('비밀번호 변경했습니다.')

            if 'url' in session:
                # 이전 url이 /search인 경우
                if session['url'] == 'search':
                    # /search에서 넘어온 경우
                    session.pop('id', None)
                    session.pop('url', None)

                    return redirect(url_for('.login'))

                if session['url'] == 'check':
                    # /check에서 넘어온 경우
                    session.pop('url', None)

                    return redirect(url_for('.profile'))

        return render_template('main/reset_password.html')
    else:
        flash('로그인이 되어있지 않거나, 해당 접근 방식으로는 비밀번호 변경이 불가능합니다.')
        return redirect(url_for('.index'))


@main.route('/logout')
def logout():
    # 로그아웃 뷰함수
    if 'id' in session:
        session.pop('id', None)
    else:
        flash('로그인이 되어있지 않는 상태입니다.')

    return redirect(url_for('.index'))


@main.route('/profile')
def profile():
    # 프로필 뷰함수
    if 'id' in session:
        user = User.query.filter_by(id = session['id']).first_or_404()
        return render_template('main/profile.html', user = user)
    else:
        flash('로그인이 되어있지 않습니다.')
        return redirect(url_for('.index'))


@main.route('/edit_profile', methods=['GET', 'POST'])
def edit_profile():
    # 프로필 수정 뷰함수
    if 'id' in session:
        user = User.query.filter_by(id = session['id']).first()
        if request.method == 'POST':
            username = request.form['userName']
            profile_name = request.form['profileName']
            if profile_name == 'default-profile.png' and profile_name != user.profile_name:
                # 프로필 이미지의 파일명이 기본 프로필 이미지 파일명과 같은 경우
                user.profile_name = profile_name
            elif profile_name == user.profile_name:
                pass
            else:
                # 파일명이 같지 않는 경우
                profile_file = request.files['file']
                profile_file.save(os.path.join(current_app.config['PROFILE_PATH'], user.user_id, profile_name))
                user.profile_name = profile_name

            if username == user.username:
                # 닉네임 변경시 저장된 닉네임과 같을 경우
                pass
            else:
                # 다를 경우
                user.username = username

            db.session.commit()
            return jsonify(confirm = False)
        return render_template('main/edit_profile.html', user = user)
    else:
        flash('로그인이 되어있지 않습니다.')
        return redirect(url_for('.index'))


@main.route('/check_current_password', methods=['GET', 'POST'])
def check():
    # 현재 비밀번호를 확인하는 뷰함수
    if request.method == 'POST':
        current_password = request.form['currentPw']
        current_password_hash = db.session.query(func.sha2(current_password,224))
        user = User.query.filter_by(id = session['id'], password_hash = current_password_hash).first()
        if not user:
            flash('입력하신 비밀번호는 현재 비밀번호와 맞지 않습니다.')
            return redirect(url_for('.check'))

        session['url'] = 'check'

        return redirect(url_for('.reset'))
    return render_template('main/check_old_password.html')