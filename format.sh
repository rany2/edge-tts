set -eux
find src examples -name '*.py' | xargs black
find src examples -name '*.py' | xargs isort
