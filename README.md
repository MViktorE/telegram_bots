## telegram_bots
# Известные особенности работы antiskyf_bot.py
1. Принимает только целые числа и через точку типа: "80.46" или "81". Все другие случаи отбрасывает. **Решение:** Добавить replace() - для замены запятых на точку. Добавить фильтры через регулярные выражения.
2. Запускается примерно в 21:15 по московскому времени, хотя cron в actions настроен на 18:00.
3. Не смотрит на реальное время сообщений, а считает, что все сообщения пришли в момент считывания.
4. Код работы с потоками написан неаккуратно.
5. Использует устаревшую библиотеку бота 13.13.
