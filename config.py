config = {
    "api_version": "v1",

    ############################## DEV SİSTEMİ #################################
    # "host": "https://sapeccdev.sutas.com.tr/zmm_pur_port/test/",
    # "client": "?sap-client=105",

    # ############################## QA SİSTEMİ ##################################
    "host": "https://10.0.1.64/zmm_pur_port/test/",
    "client": "?sap-client=200",

    ############################ PROD SİSTEMİ ################################
    # "host": "https://10.34.100.44/zmm_pur_port/test/",
    # "client": "?sap-client=200",

    "jwt": {
        "secret_key": "FIZ_BILISIM",
        "exp_sec": 1800,
        "algorithm": "HS256"
    },

    "ume_db": {
        "type": "MySql",
        "host": "localhost",
        "username": "root",
        "password": "",
        "db": "ume"
    },
    "app_db": {
        "type": "MySql",
        "host": "localhost",
        "username": "root",
        "password": "",
        "db": "app"
    },

    # "ume_db": {
    #     "type": "MySql",
    #     "host": "127.0.0.1",
    #     "username": "root",
    #     "password": "3ae!M$Nu",
    #     "db": "ume"
    # },
    # "app_db": {
    #     "type": "MySql",
    #     "host": "127.0.0.1",
    #     "username": "root",
    #     "password": "3ae!M$Nu",
    #     "db": "app"
    # },

    "charset": "utf-8"
}
