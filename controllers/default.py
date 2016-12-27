# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

# -------------------------------------------------------------------------
# This is a sample controller
# - index is the default action of any application
# - user is required for authentication and authorization
# - download is for downloading files uploaded in the db (does streaming)
# -------------------------------------------------------------------------


def index():
    return "zatim nezprovozneno"


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
    except ValueError:
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


