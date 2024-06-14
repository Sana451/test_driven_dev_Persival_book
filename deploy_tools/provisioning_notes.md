Обеспечение работы нового сайта
================================
## Необходимые пакеты:
* nginx
* Python 3.12
* virtualenv + pip
* Git

например, в Ubuntu:
    sudo add-apt-repository ppa:fkrull/deadsnakes
    sudo apt-get install nginx git python312 python3.12-venv


## Конфигурация виртуального узла Nginx
* см. nginx.template.conf
* заменить server_name 89.111.170.80, например, на staging.my-domain.com


## Служба Systemd
* см. 89.111.170.80.template.service
* заменить 89.111.170.80, например, на staging.my-domain.com

## Структура папок:
Если допустить, что есть учетная запись пользователя в /home/username
/home/username
└── sites
    └── SITENAME
        ├── database
        ├── source
        ├── static
        └── virtualenv