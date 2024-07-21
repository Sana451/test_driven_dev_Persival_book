# TO DO LIST (web приложение на Django)

## Описание:

1. Приложение, представляет собой список запланированных дел и разработано 
по методологии TDD/разработка на основе тестирования (Test-Driven Development).
2. Приложение реализовано на Django, DRF, протестировано функциональными,
интеграционными и модульными тестами (Selenium, Pytest, Mock).
3. В качестве CI сервера используется GitHub Actions с ubuntu, в pipline которого
выполняется статический анализ кода (linting) при помощи flake8, а также запуск
автоматических тестов.
4. Проект содержит набор инструментов для автоматизации развертывания на сервере
Nginx и Gunicorn, использующих Fabric (fabfile.py).
5. В проекте реализована беспарольная аутентификация: всякий раз,
когда кто-то хочет войти в систему, мы генерируем для него уникальный
URL-адрес, посылаем ему ссылку на этот URL по электронной почте, а затем
он переходит по ней, чтобы попасть на сайт. 
электронных писем по указанному email адресу.
6. У пользователей есть возможность совместного использования списков
(поделиться списком с другими пользователями).


# Инструкция по развёртыванию
Скачать исходный код проекта: `git clone https://github.com/Sana451/test_driven_dev_Persival_book.git`    
Перейти в папку с проектом: `cd test_driven_dev_Persival_book/`    
Произвести сборку контейнера: `docker build --progress=plain --no-cache -t todo-app .`    
Запустить контейнер: `docker run -it --rm -p 8000:8000 --name todo-app todo-app`    

## Использование
После запуска контейнера перейти на URL: [http://0.0.0.0:8000/](http://0.0.0.0:8000/).