# -*- coding: utf-8 -*-

import bs4
import requests


USER_FOR_DEFAULT_SETTING = 'krepo.default@zitranavylet.cz'


def index():
    def get_label(nastavene, pos):
        if 0 <= pos < len(nastavene):
            return nastavene[pos].vlakno.kratce or nastavene[pos].vlakno.vlakno.split(' ', 1)[0]
        else:
            return None

    def get_nastavene():
        return db(db.user_vlakno).select(
                db.user_vlakno.ALL, db.vlakno.ALL,
                join=db.vlakno.on(db.vlakno.id == db.user_vlakno.vlakno_id),
                orderby=~db.user_vlakno.priorita
                )

    nastavene = get_nastavene()
    if not len(nastavene):
        corr_user = db(db.auth_user.email == USER_FOR_DEFAULT_SETTING).select(db.auth_user.id).first()
        if corr_user:
            auth.corrected_user_id = corr_user.id
            nastavene = get_nastavene()
        if not len(nastavene):
            return "Nebylo nalezeno defaultní nastavení krepo.default. Informuj prosím administrátora: zvolsky@seznam.cz."

    try:
        pos = int(request.args(0))
    except (ValueError, TypeError):
        pos = 0

    tato = get_label(nastavene, pos)
    vzad = get_label(nastavene, pos - 1)
    vpred = get_label(nastavene, pos + 1)

    ok = True
    results = requests.get(nastavene[pos].vlakno.url)
    if not results or results.status_code != 200:
        ok = False

    if ok:
        soup = bs4.BeautifulSoup(results.content, 'lxml')
        netisk = soup.find_all('table', 'netisk')
        if netisk:
            netisk = netisk[0]
        diskuse_tabulka = soup.find_all('table', 'diskuse_tabulka')
        for tbl in diskuse_tabulka[::-1]:
            if tbl != netisk:
                break

        prispevky = []
        if tbl:
            trows = tbl.tbody.find_all('tr')
            allow_txt = False
            for trow in trows:
                if allow_txt:
                    allow_txt = False  # není-li text zde, v dalším <tr> už nás nezajímá (zmatek autor/txt)
                    txt = trow.find_all('td', 'dftext')
                    if txt:
                        prispevky[-1]['txt'] = txt[0].text.encode('utf-8')
                else:
                    autor = trow.find_all('td', 'dfautorlevy')
                    if autor:
                        prispevky.append({})
                        allow_txt = True   # text povolen jen v následujícím <tr>
        prispevky = prispevky[-3:]
        naposled = datetime.datetime.now()

        db((db.user_vlakno.auth_user_id == auth.user_id) &
                (db.user_vlakno.id == nastavene[pos].user_vlakno.id)).update(
                naposled=naposled
                )


    return dict(pos=pos, tato=tato, vpred=vpred, vzad=vzad, ok=ok, prispevky=prispevky)


@auth.requires_login()
def nastav():
    nastavene = db(db.user_vlakno).select(
            db.user_vlakno.ALL, db.vlakno.ALL, db.tema.ALL,
            join=(db.vlakno.on(db.vlakno.id == db.user_vlakno.vlakno_id),
                  db.tema.on(db.tema.id == db.vlakno.tema_id)),
            orderby=~db.user_vlakno.priorita
            )
    nastavene_ids = [row.vlakno.id for row in nastavene]
    vse = db(db.vlakno).select(
            db.vlakno.id, db.vlakno.vlakno, db.tema.tema,
            join=db.tema.on(db.tema.id == db.vlakno.tema_id),
            orderby=(db.tema.pos, db.vlakno.pos)
            )
    return dict(nastavene=nastavene, nastavene_ids=nastavene_ids, vse=vse)


@auth.requires_login()
def nesleduj():
    if request.args:
        db((db.user_vlakno.auth_user_id == auth.user_id) & (db.user_vlakno.id == request.args(0))).delete()
    redirect(URL('nastav'))


@auth.requires_login()
def sleduj():
    try:
        vlakno_id = int(request.args(0))
    except (ValueError, TypeError):
        redirect(URL('nastav'))
    if not db((db.vlakno.id == vlakno_id) & (db.vlakno.aktivni == True)).select():
        redirect(URL('nastav'))

    form = SQLFORM.factory(
            Field('priorita', 'integer', default=20, requires=IS_INT_IN_RANGE(1, 9999999, error_message="Zadej číslo 1..9999999"), label="priorita", comment="vyšší číslo ~ zobrazuj dříve")
            )
    if form.process().accepted:
        dosud = db((db.user_vlakno.auth_user_id == auth.user_id) & (db.user_vlakno.vlakno_id == vlakno_id)).select().first()
        if dosud:
            if db.user_vlakno.priorita != form.vars.priorita:
                dosud.update_record(priorita=form.vars.priorita)
        else:
            db.user_vlakno[0] = dict(auth_user_id=auth.user_id, vlakno_id=vlakno_id, priorita=form.vars.priorita)
        redirect(URL('nastav'))
    return dict(form=form)


def user():
    """
    exposes:
    http://..../[app]/default/user/login
    http://..../[app]/default/user/logout
    http://..../[app]/default/user/register
    http://..../[app]/default/user/profile
    http://..../[app]/default/user/retrieve_password
    http://..../[app]/default/user/change_password
    http://..../[app]/default/user/bulk_register
    use @auth.requires_login()
        @auth.requires_membership('group name')
        @auth.requires_permission('read','table name',record_id)
    to decorate functions that need access control
    also notice there is http://..../[app]/appadmin/manage/auth to allow administrator to manage users
    """
    return dict(form=auth())


@cache.action()
def download():
    """
    allows downloading of uploaded files
    http://..../[app]/default/download/[filename]
    """
    return response.download(request, db)


def call():
    """
    exposes services. for example:
    http://..../[app]/default/call/jsonrpc
    decorate with @services.jsonrpc the functions to expose
    supports xml, json, xmlrpc, jsonrpc, amfrpc, rss, csv
    """
    return service()


