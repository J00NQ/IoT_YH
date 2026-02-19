from flask import Flask, request, jsonify, current_app
from flask.json.provider import DefaultJSONProvider
from sqlalchemy import create_engine, text

class CustomJSONProvider(DefaultJSONProvider):
    def default(self, obj):
        if isinstance(obj, set):
            return list(obj)
        return super().default(obj)

def insert_user(user):
    with current_app.database.connect() as conn:
        result = conn.execute(text("""
            INSERT INTO users (
                name,
                email,
                profile,
                hashed_password
            ) VALUES (
                :name,
                :email,
                :profile,
                :password
            )
        """), user)
        conn.commit()
        return result.lastrowid

def update_user(user_id, name, profile):
    with current_app.database.connect() as conn:
        with conn.begin():
            user = conn.execute(text("""
                UPDATE users SET
                    name = :name,
                    profile = :profile
                WHERE id = :user_id
            """), {
                'user_id': user_id, 
                'name': name, 
                'profile': profile
            })

def get_user(user_id):
    with current_app.database.connect() as conn:
        user = conn.execute(text("""
            SELECT
                id,
                name,
                email,
                profile
            FROM users
            WHERE id = :user_id
        """), {'user_id': user_id}).fetchone()

    return {
        'id'      : user[0],
        'name'    : user[1],
        'email'   : user[2],
        'profile' : user[3]
    } if user else None

def get_all_users():
    with current_app.database.connect() as conn:
        users = conn.execute(text("""
            SELECT
                id,
                name,
                email,
                profile
            FROM users
        """)).fetchall()

    return [{
        'id'      : user[0],
        'name'    : user[1],
        'email'   : user[2],
        'profile' : user[3]
    } for user in users]

def insert_tweet(user_tweet):
    with current_app.database.connect() as conn:
        result = conn.execute(text("""
            INSERT INTO tweets (
                user_id,
                tweet
            ) VALUES (
                :id,
                :tweet
            )
        """), user_tweet)
        conn.commit()
        return result.rowcount

def insert_follow(user_follow):
    with current_app.database.connect() as conn:
        result = conn.execute(text("""
            INSERT INTO users_follow_list (
                user_id,
                follow_user_id
            ) VALUES (
                :id,
                :follow
            )
        """), user_follow)
        conn.commit()
        return result.rowcount

def insert_unfollow(user_unfollow):
    with current_app.database.connect() as conn:
        result = conn.execute(text("""
            DELETE FROM users_follow_list
            WHERE user_id = :id
            AND follow_user_id = :unfollow
        """), user_unfollow)
        conn.commit()
        return result.rowcount

def get_timeline(user_id):
    with current_app.database.connect() as conn:
        timeline = conn.execute(text("""
            SELECT
                t.user_id,
                t.tweet
            FROM tweets t
            LEFT JOIN users_follow_list ufl ON ufl.user_id = :user_id
            WHERE t.user_id = :user_id
            OR t.user_id = ufl.follow_user_id
        """), {'user_id': user_id}).fetchall()

    return [{
        'user_id' : tweet[0],
        'tweet'   : tweet[1]
    } for tweet in timeline]

def delete_tweet(tweet_id):
    with current_app.database.begin() as conn:
        result = conn.execute(text("""
            DELETE FROM tweets
            WHERE id = :tweet_id
        """), {'tweet_id': tweet_id})
        return result.rowcount

def create_app(test_config=None):
    app = Flask(__name__)
    app.json_provider_class = CustomJSONProvider
    app.json = CustomJSONProvider(app)

    if test_config is None:
        app.config.from_pyfile("config.py")
    else:
        app.config.update(test_config)

    database = create_engine(app.config['DB_URL'], max_overflow=0)
    app.database = database

   # 메모리 기반 데이터 (4단계에서 DB로 교체 예정)
#    app.users = {}
#    app.id_count = 1
#    app.tweets = []

    @app.route("/ping", methods=['GET'])
    def ping():
        return "pong"

    @app.route("/sign-up", methods=['POST'])
    def sign_up():
        new_user = request.json
        new_user_id = insert_user(new_user)
        new_user = get_user(new_user_id)
        return jsonify(new_user)

    @app.route('/user/<int:user_id>', methods=['GET'])
    def get_user_info(user_id):
        user = get_user(user_id)
        if user is None:
           return '사용자가 존재하지 않습니다.', 404
        return jsonify(user)

    @app.route('/users', methods=['GET'])
    def user_list():
        return jsonify(get_all_users())

    @app.route('/user/<int:user_id>', methods=['PUT'])
    def modify_user(user_id):
        payload = request.json

        name = payload.get('name')
        profile = payload.get('profile')

        user = get_user(user_id)
        if user is None:
            return '사용자가 존재하지 않습니다.', 404
        
        update_user(user_id, name, profile)
        return jsonify({
            'user_id' : user_id,
            'name'    : name,
            'profile' : profile
        }), 200

    @app.route('/tweet', methods=['POST'])
    def tweet():
        user_tweet = request.json
        tweet = user_tweet['tweet']

        if len(tweet) > 300:
            return '300자를 초과했습니다.', 400

        insert_tweet(user_tweet)

        return '', 200

    @app.route('/tweet/<int:tweet_id>', methods=['DELETE'])
    def delete_tweet_endpoint(tweet_id):
        rows = delete_tweet(tweet_id)
        if rows == 0:
            return '트윗이 존재하지 않습니다.', 404
        return '', 200

    @app.route('/follow', methods=['POST'])
    def follow():
        payload = request.json
        insert_follow(payload)

        return '', 200

    @app.route('/unfollow', methods=['POST'])
    def unfollow():
        payload = request.json
        insert_unfollow(payload)

        return '', 200

    @app.route('/timeline/<int:user_id>', methods=['GET'])
    def timeline(user_id):
        return jsonify({
            'user_id'  : user_id,
            'timeline' : get_timeline(user_id)
        })

    return app

 