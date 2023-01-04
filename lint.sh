find src examples -name '*.py' | xargs black
find src examples -name '*.py' | xargs isort
find src examples -name '*.py' | xargs pylint
find src examples -name '*.py' | xargs mypy
