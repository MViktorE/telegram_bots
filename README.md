# telegram_bots
## Известные особенности работы antiskyf_bot.py
1. Если отправить сообщение, потом его успеть отредактировать, то считает все равно сообщение до редакции.
2. Запускается примерно в 21:15 по московскому времени, хотя cron в actions настроен на 18:00.
3. Не смотрит на реальное время сообщений, а считает, что все сообщения пришли в момент считывания.
4. Код работы с потоками написан неаккуратно.
5. Использует устаревшую библиотеку бота 13.13.
