SECRET_NAME="attendunce"
ROOT_DIR="$(git rev-parse --show-toplevel)"

SECRETS=$(aws secretsmanager get-secret-value --secret-id $SECRET_NAME --query SecretString --output text)
ENV_DIR="$ROOT_DIR/.env"
touch $ENV_DIR
echo $SECRETS | jq -r 'to_entries|map("\(.key)=\(.value|tostring)")|.[]' > $ENV_DIR
echo "Secrets fetched and stored in $ENV_DIR"