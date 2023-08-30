import redis
from dotenv import dotenv_values

env_vars = dotenv_values(".env")

redis1 = redis.Redis(
    host=env_vars["REDIS1_HOST"],
    port=int(env_vars["REDIS1_PORT"]),
    password=env_vars["REDIS1_PASSWORD"],
    decode_responses=True,
)

redis2 = redis.Redis(
    host=env_vars["REDIS2_HOST"],
    port=int(env_vars["REDIS2_PORT"]),
    password=env_vars["REDIS2_PASSWORD"],
    decode_responses=True,
)

keys = redis1.keys()

for key in keys:
    value = ""
    try:
        value = redis1.get(key)
        print(f"Setting {key} to {value}")
        redis2.set(key, value)
    except:
        print(f"Failed to set {key} to {value}")

redis2.save()

print("Migration complete.")
