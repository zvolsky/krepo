# -*- coding: utf-8 -*-

db.define_table('tema',
        Field('tema', 'string', length=192),
        Field('url', 'text'),
        Field('aktivni', 'boolean', default=True),
        Field('pos', 'integer'),
        )

db.define_table('vlakno',
        Field('tema_id', db.tema),
        Field('tema_pos', 'integer'),
        Field('vlakno', 'string', length=192),
        Field('kratce', 'string', length=32),
        Field('url', 'text'),
        Field('aktivni', 'boolean', default=True),
        Field('pos', 'integer'),
        )

db.define_table('user_vlakno',
        Field('auth_user_id', db.auth_user),
        Field('vlakno_id', db.vlakno),
        Field('priorita', 'integer', default=20, requires=IS_INT_IN_RANGE(1, 9999999)),
        common_filter=lambda query: db.user_vlakno.auth_user_id == auth.user_id,
        )
