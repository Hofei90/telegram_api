from setuptools import setup

setup(
    name='telegram_api',
    version='1.0',
    py_modules = ["telegram_bot_api"],
    url='https://github.com/Hofei90/telegram_api/',
    license='MIT',
    author='Hofei90',
    author_email='29521028+Hofei90@users.noreply.github.com',
    description='Telegram Bot API',
    install_requires=["requests~=2.25.1"]
)
