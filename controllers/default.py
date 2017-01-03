# -*- coding: utf-8 -*-

import bs4
import requests


USER_FOR_DEFAULT_SETTING = 'krepo.default@zitranavylet.cz'


def index():
    '''
        args(0) je aktuální pozice v nastavene (ve sledovaných)
        nebo
        args(0)=='id', args(1) je id vlakna (při prohlížení nesledovaných)
    '''
    def get_row_label(nastavene_row):
        return nastavene_row.kratce or nastavene_row.vlakno.split(' ', 1)[0]

    def get_label(nastavene, pos):
        if 0 <= pos < len(nastavene):
            return get_row_label(nastavene[pos].vlakno)
        else:
            return None

    def get_nastavene():
        return db(db.user_vlakno).select(
                db.user_vlakno.ALL, db.vlakno.ALL,
                join=db.vlakno.on(db.vlakno.id == db.user_vlakno.vlakno_id),
                orderby=~db.user_vlakno.priorita
                )

    def get_kr_tag(el, kr_tag):   # '<!--name-->'
        el = str(el)
        if kr_tag in el:
            return el.split(kr_tag[4:])[1][:-5].strip()  # split('name-->'), z konce výsledku odstranit <!--/
        return ''

    def cas_z_necasu(neco_jako_cas):
        try:
            parts = neco_jako_cas.split()
            parts[3] = ' '
            parts[1] = str(['ledna', 'února', 'března', 'dubna', 'května', 'června',
                                'července', 'srpna', 'září', 'října', 'listopadu', 'prosince'].index(parts[1].encode('utf-8')) + 1) + '.'
            return datetime.datetime.strptime(''.join(parts), '%d.%m.%Y %H:%M:%S')
        except Exception:
            return datetime.datetime(1900, 1, 1)

    def get_from_krepo(url, vcetne_archivu=False, archivy=None):
        # stáhnout vlákno z k-report
        ok = True
        results = requests.get(url)
        if not results or results.status_code != 200:
            ok = False

        jeste_nebereme = True
        prispevky = []
        if ok:
            # extrahovat příspěvky
            soup = bs4.BeautifulSoup(results.content, 'lxml')
            netisk = soup.find_all('table', 'netisk')
            if netisk:
                netisk = netisk[0]
            diskuse_tabulka = soup.find_all('table', 'diskuse_tabulka')
            for tbl in diskuse_tabulka[::-1]:
                if tbl != netisk:
                    break

            if tbl:
                trows = tbl.tbody.find_all('tr')
                if limit:                           # neběží při byhledání aktualizací / TODO: při problémech tento if vyhodit
                    trows = trows[-limit * 2 - 1:]  # 2 řádky na příspěvek a na konci je ještě falešný řádek
                    jeste_nebereme = False
                allow_txt = False
                potrebujeme_jeste_starsi = True
                for trow in trows:
                    if allow_txt:
                        allow_txt = False  # není-li text zde, v dalším <tr> už nás nezajímá (zmatek autor/txt)
                        txt = trow.find_all('td', 'dftext')
                        if txt:
                            txt = get_kr_tag(txt[0], '<!--Text-->')
                            prispevky[-1]['txt'] = txt.replace('style="background: url(\'/', 'style="background: url(\'http://www.k-report.net/')
                    else:
                        if jeste_nebereme:
                            neco_jako_cas = trow.find_all('td', 'dfautorpravy')
                            if neco_jako_cas:  # jinak havaruje na posledním falešném <tr class="netisk">
                                neco_jako_cas = neco_jako_cas[0].div.em.text.split(',', 1)[1]
                                kdy = cas_z_necasu(neco_jako_cas)
                                if kdy >= dosud_naposled:
                                    jeste_nebereme = False

                                    # rekurzivně zpracovat archivy?
                                    if potrebujeme_jeste_starsi:  # toto je pouze na 1.řádku, zde nemůžeme mít už nabrané staré příspěvky
                                        if vcetne_archivu:   # voláno z nearchivní stránky
                                            for tbla in diskuse_tabulka[::-1]:
                                                if tbla != netisk and tbla != tbl:
                                                    archivy = parse_archivy(tbla)
                                                    break
                                        if archivy:          # jsou k dispozici nezpracované archivy
                                            _ok, prispevky, _nezacaly_nove = get_from_krepo(archivy[0], vcetne_archivu=False, archivy=archivy[1:])

                                    else:                         # zde můžeme mít už nabrané staré příspěvky - omezme jejich počet
                                        prispevky = zkrat_stare(prispevky)

                            potrebujeme_jeste_starsi = False

                        autor = trow.find_all('td', 'dfautorlevy')
                        if autor:
                            prispevky.append({'aut': get_kr_tag(autor[0], '<!--name-->')})
                            allow_txt = True   # text povolen jen v následujícím <tr>
        return ok, prispevky, jeste_nebereme

    def parse_archivy(tbla):
        archivy = []
        odkazy = tbla.find_all('a')
        for odkaz in odkazy[::-1]:
            url = odkaz['href']
            if url.startswith('http://www.k-report.net/discus/messages/'):
                archivy.append(url)
            elif url.startswith('http://www.k-report.net/discus/archiv20'):
                archivy.append(url)
                break
        return archivy[:8]  # vzhledem k rekurzivnímu volání omezíme počet

    def zkrat_stare(prispevky):
        prispevky = prispevky[-kontext:]  # ponechat jen kontext: pár posledních starých
        for prispevek in prispevky:
            prispevek['old'] = True
        return prispevky

    # seznam sledovaných
    nastavene = get_nastavene()
    if len(nastavene):
        moje_nastaveni = True
        nove_naposled = datetime.datetime.now() - datetime.timedelta(seconds=10)  # radši kousek zpět
    else:
        moje_nastaveni = False
        corr_user = db(db.auth_user.email == USER_FOR_DEFAULT_SETTING).select(db.auth_user.id).first()
        if corr_user:
            auth.corrected_user_id = corr_user.id
            nastavene = get_nastavene()
        if not len(nastavene):
            return "Nebylo nalezeno defaultní nastavení krepo.default. Informuj prosím administrátora: zvolsky@seznam.cz."

    forced_by_id = False
    if request.args(0) == 'id':
        vlakno = db(db.vlakno.id == request.args(1)).select(db.vlakno.ALL).first()
        if vlakno:
            forced_by_id = True
        pos = 0
    else:
        # aktuální pozice v seznamu sledovaných
        try:
            pos = max(0, int(request.args(0)))
            if pos >= len(nastavene):
                pos = 0   # z posledního jdi na první, viz *1
        except (ValueError, TypeError):
            pos = 0

    # počet příspěvků
    if moje_nastaveni and not forced_by_id:
        dosud_naposled = nastavene[pos].user_vlakno.naposled
        if dosud_naposled:
            limit = 0
            kontext = 2                     # kontext: kolik starých ponecháme
        else:
            limit = 5
    else:
        limit = 15

    # buttony a label
    all_pages = [get_row_label(nastavene_row.vlakno) for nastavene_row in nastavene]
    tato = get_label(nastavene, pos)
    vzad = get_label(nastavene, pos - 1)
    vpred = get_label(nastavene, pos + 1)
    if not vpred:
        vpred = get_label(nastavene, 0)   # z posledního jdi na první, viz *1

    # stáhnout a extrahovat z k-report
    ok, prispevky, nezacaly_nove = get_from_krepo(
            vlakno.url if forced_by_id else nastavene[pos].vlakno.url, vcetne_archivu=not limit)

    # omezit počet zobrazených; při aktualizacích zjistit, jestli jsou nějaké nové
    if limit:
        prispevky = prispevky[-limit:]
    elif nezacaly_nove:
        prispevky = zkrat_stare(prispevky)

    # zapsat čas posledního prohlížení
    if moje_nastaveni:
        if forced_by_id:
            db((db.user_vlakno.auth_user_id == auth.user_id) &
                    (db.user_vlakno.vlakno_id == vlakno.id)).update(
                    naposled=nove_naposled
                    )
        else:
            db((db.user_vlakno.auth_user_id == auth.user_id) &
                    (db.user_vlakno.id == nastavene[pos].user_vlakno.id)).update(
                    naposled=nove_naposled
                    )

    fs = session.fs or 150
    return dict(pos=pos, tato=tato, vpred=vpred, vzad=vzad, ok=ok, prispevky=prispevky,
                vlakno_id=vlakno.id if forced_by_id else nastavene[pos].vlakno.id,
                all_pages=all_pages, nejsou_nove=not limit and nezacaly_nove,
                fs=fs, fs2=int(12*max(100, fs)/100))


def nabidka():
    if request.args(2):
        fs = session.fs or 150
        if request.args(2) == 'plus':
            fs = min(1000, int(fs * 1.1))
        elif request.args(2) == 'minus':
            fs = max(10, int(fs / 1.1))
        session.fs = fs
    else:
        fs = None

    temata = db().select(db.tema.ALL, orderby=db.tema.pos)
    vlakna = None
    rozvin_tema = None
    try:
        vlakno_id = int(request.args(0))
    except Exception:
        vlakno_id = None
    if vlakno_id is not None:   # parametr je vlakno, pro které promítneme (rozvinutá) všechna vlákna téhož tématu
        predvolene = db(db.vlakno.id == vlakno_id).select(db.tema.id,
                join=db.tema.on(db.tema.id == db.vlakno.tema_id)).first()
        if predvolene:
            rozvin_tema = predvolene.id
    elif request.vars.get('tema'):
        rozvin_tema = request.vars.get('tema')

    if rozvin_tema:
        temata = [tema for tema in temata if tema.id != rozvin_tema]
        vlakna = db(db.vlakno.tema_id == rozvin_tema).select(db.vlakno.id, db.vlakno.vlakno,
                                orderby=db.vlakno.pos)

    return dict(temata=temata, vlakna=vlakna,
                vlakno_id=vlakno_id or '-', return_pos=request.args(1) or 0,
                fs=fs, fs2=int(12*max(100, (fs or 100))/100))


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


