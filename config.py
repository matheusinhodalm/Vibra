import os

# Troque isto em produção (ou defina via variável de ambiente)
SECRET_KEY = os.environ.get("SECRET_KEY", "dde0da26d69b1e8cc0c32c6c843ecb78bd4a9897c0d1414d137ec2570ff9ca41")
DATABASE = os.environ.get("DATABASE", os.path.join(os.path.dirname(__file__), "vibra.db"))
APP_NAME = "VIBRA"
