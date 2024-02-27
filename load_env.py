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
        "CLOUD_NAME": config('CLOUD_NAME'),
        "API_KEY": config('API_KEY'),
        "API_SECRET": config('API_SECRET'),
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