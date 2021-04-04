from environs import Env

# Теперь используем вместо библиотеки python-dotenv библиотеку environs
env = Env()
env.read_env()

BOT_TOKEN = '1588332634:AAE5wS_KT6q8bogD4DkOfRAG6vuQlxaLb3g' # "1798798058:AAER1qW9lTMVOWQSOBtH4DE91pV40gFeOek"
ADMIN_CHAT =  int('-1001302831004') # int("-1001153113056")  
ADMINS =  ["766099159"] # ["254507320"]  # Тут у нас будет список из админов
IP = "194.87.214.180"  # Тоже str, но для айпи адреса хоста

