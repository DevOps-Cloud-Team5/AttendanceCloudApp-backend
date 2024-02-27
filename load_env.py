import json
from decouple import config

def update_zappa_settings():
    # Load .env variables
    env_vars = {
        "DB_NAME": config('DB_NAME'),
        "DB_HOST": config('DB_HOST'),
        "DB_USER": config('DB_USER'),
        "DB_PORT": config('DB_PORT'),
        "DB_PASSWORD": config('DB_PASSWORD'),
        "AWS_STORAGE_BUCKET_NAME": config('AWS_STORAGE_BUCKET_NAME'),
        "AWS_ACCESS_KEY_ID": config('AWS_ACCESS_KEY_ID'),
        "AWS_SECRET_ACCESS_KEY": config('AWS_SECRET_ACCESS_KEY'),
    }

    # Load existing Zappa settings
    with open('zappa_settings.json', 'r') as file:
        zappa_settings = json.load(file)

    # Update environment variables in Zappa settings
    zappa_settings['prod']['environment_variables'] = env_vars

    # Save updated Zappa settings
    with open('zappa_settings.json', 'w') as file:
        json.dump(zappa_settings, file, indent=4)

if __name__ == "__main__":
    update_zappa_settings()