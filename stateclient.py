import redis
from environs import Env


def saves_last_state_client(client_id, latest_state):
    try:
        env = Env()
        env.read_env()
        redis_port = env.str("REDIS_PORT")
        redis_pass = env.str("REDIS_PASS")
        redis_host = env.str("REDIS_HOST")

        redis_conn = redis.StrictRedis(
            host=redis_host,
            port=redis_port,
            password=redis_pass,
            charset="utf-8",
            decode_responses=True,
        )
        redis_conn.hset(
            "user-session",
            mapping={"client_id": client_id, "latest_state": latest_state},
        )
        # print(redis_conn.hgetall(f"user-session"))

    except redis.exceptions.ConnectionError:
        print("Ошибка подключения к Redis.")
    except redis.exceptions.TimeoutError:
        print("Превышено время ожидания при работе с Redis.")
    except redis.exceptions.AuthenticationError:
        print("Ошибка аутентификации при подключении к Redis.")
    except Exception as e:
        print(f"Произошла неизвестная ошибка: {e}")
