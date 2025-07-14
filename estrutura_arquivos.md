Segue como a estrutura ficou

Nova Estrutura de Arquivos:

crm-azevix/
├── backend/
│   ├── __init__.py
│   ├── auth.py
│   ├── contas.py
│   ├── main.py
│   ├── models.py
│   ├── user.py
│   ├── utils.py
│   ├── static/
│   │   ├──css
│   │   │   └── main.cs
│   │   └──js
│   │      ├── contas.js
│   │      ├── detalhe_conta.js
│   │      ├── lista_contas.js
│   │      └── nova_conta.js
│   └── templates/
│       ├──auth
│       │   ├── login.html
│       │   ├── register.html
│       │   └── set_password.html
│       ├──contas
│       │   ├── detalhe_conta.html
│       │   ├── lista_contas.html
│       │   └── nova_conta.html
│       ├──user
│       │   └── perfil.html
│       ├── base.html
│       └── dashboard.html
├── .env
├── .env.example
├── .gitignore
├── boot.sh
├── docker-compose.yml
├── Dockerfile
├── nginx.conf
├── README.md
├── requirements.txt
└── run.py