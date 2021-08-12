import pymysql


class DBBase(object):
    _instances = []
    _connection = None

    @staticmethod
    def get_instance(**kwargs):
        """ Creating only one instance for every db config
        """
        for instance in DBBase._instances:
            instance_found = False
            for key, value in kwargs.items():
                instance_val = getattr(instance, "_" + key, None)
                if instance_val is None or instance_val is not value:
                    instance_found = False
                    break
                else:
                    instance_found = True

            if instance_found:
                return instance
        instance = DBBase(**kwargs)
        DBBase._instances.append(instance)
        return instance

    @staticmethod
    def refresh():
        for instance in DBBase._instances:
            try:
                instance._connection.close()
            except:
                pass

        DBBase._instances = []
        return

    def __init__(self, type, host, username, password, db, port=0000):
        """
            Getting DB configration parameters and
            opening a new connection
        """
        self._type = type
        self._host = host
        self._username = username
        self._password = password
        self._db = db
        self._port = port
        self._connect_db()

    def _connect_db(self):
        self._con = pymysql.connect(host=self._host,
                                    user=self._username,
                                    password=self._password,
                                    db=self._db,
                                    cursorclass=pymysql.cursors.DictCursor)

    def get_main_menu(self, username):
        cursor = self._con.cursor()
        cursor.execute(
            'SELECT menu.menu_id, menu.top_menu_id, menu.icon, menu.color, menu.url, menu.description, menu.row, user.username ,user.user_type ,user.user_sys_id, user.type_desc FROM (((menu INNER JOIN role ON menu.menu_id = role.menu_id) INNER JOIN user_role ON role.role_id = user_role.role_id) INNER JOIN user ON user_role.username = user.username) WHERE user.username = %s ', (username))
        return cursor.fetchall()

    def get_ids(self):
        cursor = self._con.cursor()
        cursor.execute(
            'SELECT user_sys_id, username, company FROM user WHERE user_type = "SUP"')
        return cursor.fetchall()

    def get_user_info(self, kullanıcı):
        cursor = self._con.cursor()
        cursor.execute(
            'SELECT user_type, user_sys_id, username, password, email, company FROM user WHERE username = %s ', (kullanıcı))
        return cursor.fetchall()

    def get_anounces(self, supid):
        cursor = self._con.cursor()
        cursor.execute(
            'SELECT * FROM anounces WHERE who = "GENEL" OR who = %s', (supid))
        return cursor.fetchall()

    def get_anounces_all(self):
        cursor = self._con.cursor()
        cursor.execute(
            'SELECT * FROM anounces')
        return cursor.fetchall()

    def add_anounce(self, anons, who):
        cursor = self._con.cursor()
        cursor.execute(
            'INSERT INTO anounces (title, anounce, created_by, created_date, created_time, from_date, from_time, to_date, to_time, importance, who) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s )', (anons['title'], anons['anounce'], anons['created_by'], anons['created_date'], anons['created_time'], anons['from_date'], anons['from_time'], anons['to_date'], anons['to_time'], anons['importance'], who))
        self._con.commit()
        return cursor.fetchall()

    def del_anounce(self, no):
        cursor = self._con.cursor()
        cursor.execute(
            'DELETE FROM anounces WHERE anounces.title = %s AND anounces.anounce = %s', (no['title'], no['anounce']))
        self._con.commit()
        return cursor.fetchall()

    def push_attach(self, file):
        cursor = self._con.cursor()
        cursor.execute(
            'INSERT INTO h_attaches (data_content, data_name, data_size) VALUES (%s, %s, %s)', (
                file['content'], file['name'], file['size'])
        )
        self._con.commit()
        return cursor.fetchall()

    def del_attach(self, parsed):
        cursor = self._con.cursor()
        cursor.execute(
            'DELETE FROM h_attaches WHERE id = %s', (parsed['id'])
        )
        self._con.commit()
        return cursor.fetchall()

    def get_help_attach(self):
        cursor = self._con.cursor()
        cursor.execute(
            'SELECT * FROM h_attaches')
        return cursor.fetchall()

    def insert_rev_desc(self, parsed):
        cursor = self._con.cursor()
        cursor.execute(
            'INSERT INTO rev_info (po_number, po_item, rev_desc) VALUES (%s, %s, %s)', (
                parsed['po_number'], parsed['po_item'], parsed['zrev_desc'])
        )
        self._con.commit()
        return cursor.fetchall()

    def get_rev_desc(self):
        cursor = self._con.cursor()
        cursor.execute(
            'SELECT * FROM rev_info'
        )
        return cursor.fetchall()

    def del_rev_desc(self, parsed):
        cursor = self._con.cursor()
        cursor.execute(
            'DELETE FROM rev_info WHERE po_number = %s AND po_item = %s', (parsed['po_number'], parsed['po_item']))
        self._con.commit()
        return cursor.fetchall()

    def get_po_attach_id(self, parsed):
        cursor = self._con.cursor()
        cursor.execute(
            'SELECT attach_id FROM s_attach_item WHERE data_name = %s AND data_size = %s AND doc_type = %s', (
                parsed['name'], parsed['size'], parsed['doc_type'])
        )
        return cursor.fetchall()

    def post_po_attach_item(self, parsed):
        cursor = self._con.cursor()
        cursor.execute(
            'INSERT INTO s_attach_item (data_content, data_name, data_type, data_size, doc_type, date) VALUES (%s, %s, %s, %s, %s, %s)', (
                parsed['content'], parsed['name'], parsed['type'], parsed['size'], parsed['doc_type'], parsed['date'])
        )
        self._con.commit()
        return cursor.fetchall()

    def post_po_attach_header(self, parsed, id):
        cursor = self._con.cursor()
        cursor.execute(
            'INSERT INTO s_attach_header (po_number, po_item, attach_id) VALUES (%s, %s, %s)', (
                parsed['EBELN'], parsed['EBELP'], id[0]['attach_id'])
        )
        self._con.commit()
        return cursor.fetchall()

    def get_po_attach(self, parsed):
        cursor = self._con.cursor()
        cursor.execute(
            'SELECT * FROM s_attach_header INNER JOIN s_attach_item ON s_attach_header.attach_id = s_attach_item.attach_id WHERE s_attach_header.po_number = %s AND s_attach_header.po_item = %s', (
                parsed['EBELN'], parsed['EBELP'])
        )
        return cursor.fetchall()

    def get_ven_attach(self, parsed):
        cursor = self._con.cursor()
        cursor.execute(
            'SELECT * FROM v_attach WHERE user_sys_id = %s', (parsed)
        )
        return cursor.fetchall()

    def control_ven_attach(self, user_sys_id, doc_type):
        cursor = self._con.cursor()
        cursor.execute(
            'SELECT * FROM v_attach WHERE user_sys_id = %s AND doc_type = %s', (
                user_sys_id, doc_type)
        )
        return cursor.fetchall()

    def post_ven_attach(self, parsed):
        cursor = self._con.cursor()
        cursor.execute(
            'INSERT INTO v_attach (user_sys_id, data_content, data_name, data_type, data_size, doc_type, date) VALUES (%s, %s, %s, %s, %s, %s, %s)', (
                parsed['sup_id'], parsed['content'], parsed['name'], parsed['type'], parsed['size'], parsed['doc_type'], parsed['date'])
        )
        self._con.commit()
        return cursor.fetchall()

    def update_ven_attach(self, attach, id):
        cursor = self._con.cursor()
        cursor.execute(
            'UPDATE v_attach SET data_content = %s , data_name = %s, data_type = %s, data_size = %s, date = %s WHERE attach_id = %s', (
                attach['content'], attach['name'], attach['type'], attach['size'], attach['date'], id)
        )
        self._con.commit()
        return cursor.fetchall()

    def delete_ven_attach(self, id):
        cursor = self._con.cursor()
        cursor.execute(
            'DELETE FROM v_attach WHERE attach_id = %s', (id)
        )
        self._con.commit()
        return cursor.fetchall()

    def get_alerts_db(self):
        cursor = self._con.cursor()
        cursor.execute(
            'SELECT * FROM alerts'
        )
        return cursor.fetchall()

    def delete_alerts_db(self, parsed):
        cursor = self._con.cursor()
        cursor.execute(
            'DELETE FROM alerts WHERE id = %s', (parsed['id'])
        )
        self._con.commit()
        return cursor.fetchall()

    def insert_alerts_db(self, parsed):
        cursor = self._con.cursor()
        cursor.execute(
            'INSERT INTO alerts (date, time, message, type) VALUES (%s, %s, %s, %s)', (
                parsed['date'], parsed['time'], parsed['message'], parsed['type'])
        )
        self._con.commit()
        return cursor.fetchall()

    def get_users(self):
        cursor = self._con.cursor()
        cursor.execute('SELECT * FROM user')
        return cursor.fetchall()

    def modify_user(self, parsed):
        cursor = self._con.cursor()
        cursor.execute(
            'INSERT INTO user (username, user_sys_id, user_type, company, password, email, type_desc) VALUES (%s, %s, %s, %s, %s, %s, %s) ON DUPLICATE KEY UPDATE username = %s, user_sys_id = %s, user_type = %s, company = %s, password = %s, email = %s, type_desc = %s', (
                parsed['username'], parsed['user_sys_id'], parsed['user_type'], parsed['company'], parsed['password'], parsed['email'], parsed['type_desc'], parsed['username'], parsed['user_sys_id'], parsed['user_type'], parsed['company'], parsed['password'], parsed['email'], parsed['type_desc'])
        )
        self._con.commit()
        return cursor.fetchall()

    def modify_user_role(self, username, role_id):
        cursor = self._con.cursor()
        cursor.execute(
            'INSERT INTO user_role (username, role_id) VALUES (%s, %s) ON DUPLICATE KEY UPDATE username = %s, role_id = %s', (
                username, role_id, username, role_id)
        )
        self._con.commit()
        return cursor.fetchall()

    def delete_user(self, parsed):
        cursor = self._con.cursor()
        cursor.execute(
            'DELETE FROM user WHERE username = %s', (parsed['username'])
        )
        self._con.commit()
        return cursor.fetchall()

    def delete_user_role(self, parsed):
        cursor = self._con.cursor()
        cursor.execute(
            'DELETE FROM user_role WHERE username = %s', (parsed['username'])
        )
        self._con.commit()
        return cursor.fetchall()

    def change_pass(self, username, newpass):
        cursor = self._con.cursor()
        cursor.execute(
            'UPDATE user SET password = %s WHERE username = %s', (
                newpass, username)
        )
        self._con.commit()
        return cursor.fetchall()

    def get_user_sys_ids(self):
        cursor = self._con.cursor()
        cursor.execute(
            'SELECT user_sys_id FROM user WHERE user_type = "SUP"'
        )
        return cursor.fetchall()

    def del_on_error_head(self, a, b):
        cursor = self._con.cursor()
        cursor.execute(
            'DELETE FROM s_attach_header WHERE po_number = %s AND po_item = %s', (
                a, b)
        )
        self._con.commit()
        return cursor.fetchall()

    def del_on_error_item(self, a):
        cursor = self._con.cursor()
        cursor.execute(
            'DELETE FROM s_attach_item WHERE attach_id = %s', (a)
        )
        self._con.commit()
        return cursor.fetchall()

    def get_attach_id_head(self, a, b):
        cursor = self._con.cursor()
        cursor.execute(
            'SELECT attach_id FROM s_attach_header WHERE po_number = %s AND po_item = %s', (
                a, b)
        )
        return cursor.fetchall()

    def insert_dec_desc(self, parsed):
        cursor = self._con.cursor()
        cursor.execute(
            'INSERT INTO dec_info (po_number, po_item, dec_desc) VALUES (%s, %s, %s)', (
                parsed['po_number'], parsed['po_item'], parsed['dec_info'])
        )
        self._con.commit()
        return cursor.fetchall()

    def get_dec_desc(self):
        cursor = self._con.cursor()
        cursor.execute(
            'SELECT * FROM dec_info'
        )
        return cursor.fetchall()

    def del_dec_desc(self, parsed):
        cursor = self._con.cursor()
        cursor.execute(
            'DELETE FROM dec_info WHERE po_number = %s AND po_item = %s', (parsed['po_number'], parsed['po_item']))
        self._con.commit()
        return cursor.fetchall()

    def insert_rej_desc(self, parsed):
        cursor = self._con.cursor()
        cursor.execute(
            'INSERT INTO rej_info (po_number, po_item, rej_desc) VALUES (%s, %s, %s)', (
                parsed['po_number'], parsed['po_item'], parsed['rej_info'])
        )
        self._con.commit()
        return cursor.fetchall()

    def get_rej_desc(self):
        cursor = self._con.cursor()
        cursor.execute(
            'SELECT * FROM rej_info'
        )
        return cursor.fetchall()

    def del_rej_desc(self, parsed):
        cursor = self._con.cursor()
        cursor.execute(
            'DELETE FROM rej_info WHERE po_number = %s AND po_item = %s', (parsed['po_number'], parsed['po_item']))
        self._con.commit()
        return cursor.fetchall()

    def del_v_attach(self, parsed):
        cursor = self._con.cursor()
        cursor.execute(
            'DELETE FROM v_attach WHERE doc_type = %s', (parsed))
        self._con.commit()
        return cursor.fetchall()

    def insert_plan_rej_desc(self, parsed):
        cursor = self._con.cursor()
        cursor.execute(
            'INSERT INTO plan_rej_desc (po_number, po_item, rej_desc) VALUES (%s, %s, %s)', (
                parsed['po_number'], parsed['po_item'], parsed['rej_info'])
        )
        self._con.commit()
        return cursor.fetchall()

    def del_plan_rej_desc(self, parsed):
        cursor = self._con.cursor()
        cursor.execute(
            'DELETE FROM plan_rej_desc WHERE po_number = %s AND po_item = %s', (parsed['po_number'], parsed['po_item']))
        self._con.commit()
        return cursor.fetchall()

    def get_plan_rej_desc(self):
        cursor = self._con.cursor()
        cursor.execute(
            'SELECT * FROM plan_rej_desc'
        )
        return cursor.fetchall()

    def set_token(self, username, access_token, refresh_token, datetime, datetime_string):
        cursor = self._con.cursor()
        cursor.execute(
            'INSERT INTO login (username, access_token, refresh_token, datetime, datetime_string) VALUES (%s, %s, %s, %s, %s) ON DUPLICATE KEY UPDATE username = %s, access_token = %s, refresh_token = %s, datetime = %s, datetime_string = %s', (
                username, access_token, refresh_token, datetime, datetime_string, username, access_token, refresh_token, datetime, datetime_string)
        )
        self._con.commit()
        return cursor.fetchall()

    def get_token(self, username):
        cursor = self._con.cursor()
        cursor.execute(
            'SELECT refresh_token FROM login WHERE username = %s', (username)
        )
        self._con.commit()
        return cursor.fetchall()
