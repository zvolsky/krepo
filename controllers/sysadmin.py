# -*- coding: utf-8 -*-

import bs4
import requests


@auth.requires_membership('admin')
def temata():
    db(db.tema).update(aktivni=False)
    tema = db(db.tema).select()
    temata = {tema1.tema: tema1 for tema1 in tema}

    res_tema = requests.get('http://www.k-report.net/cgi-bin/discus/discus.pl')
    if not res_tema or res_tema.status_code != 200:
        return 'Selhal get: témata.'

    try:
        soup = bs4.BeautifulSoup(res_tema.content, 'lxml')
    except:
        try:
            soup = bs4.BeautifulSoup(res_tema.content, 'lxml')
        except:
            soup = bs4.BeautifulSoup(res_tema.content)

    tbl = soup.find('table', "diskuse_tabulka")
    if not tbl:
        return 'Témata: Nenalezena tabulka témat.'
    pos = 0
    for tr in tbl.find_all('tr'):
        if len(tr.find_all('a')) == 1:
            txt = tr.a.text.encode('utf-8')
            url = tr.a['href']
            if txt in temata:
                row = temata[txt]
                row.update_record(aktivni=True)
                if row.url != url:
                    row.update_record(url=url)
                if row.pos != pos:
                    row.update_record(pos=pos)
            else:
                db.tema.insert(tema=txt, url=url, aktivni=True, pos=pos)
            pos += 1
    return 'Ok.'

@auth.requires_membership('admin')
def vlakna():
    letos = datetime.date.today().year
    vloni = str(letos - 1)
    letos = str(letos)

    tema = db(db.tema).select()

    db(db.vlakno).update(aktivni=False)
    vlakno = db(db.vlakno).select()
    vlakna = {(vlakno1.tema_id, vlakno1.vlakno): vlakno1 for vlakno1 in vlakno}

    for tema1 in tema:
        res_vlakno = requests.get(tema1.url)
        if not res_vlakno or res_vlakno.status_code != 200:
            return 'Selhal get: %s.' % tema1.txt

        try:
            soup = bs4.BeautifulSoup(res_vlakno.content, 'lxml')
        except:
            try:
                soup = bs4.BeautifulSoup(res_vlakno.content, 'lxml')
            except:
                soup = bs4.BeautifulSoup(res_vlakno.content)

        tbl = soup.find('table', "diskuse_tabulka")
        if not tbl:
            return 'Téma %s: Nenalezena tabulka vláken.' % tema1.txt
        pos = 0
        for tr in tbl.find_all('tr'):
            td = tr.find_all('td')
            if len(td) >= 2 and len(td[1].find_all('a', recursive=False)) == 1:    # další odkazy mohou být v komentáři ve stejném <td>
                posledni = tr.find('td', "dtdatum")
                if posledni:
                    posledni = posledni.text
                    if letos in posledni or vloni in posledni:
                        txt = tr.a.text.encode('utf-8')
                        try:
                            url = tr.a['href']
                        except:
                            from pdb import set_trace; set_trace()
                            pass
                        if (tema1.id, txt) in vlakna:
                            row = vlakna[(tema1.id, txt)]
                            row.update_record(aktivni=True)
                            if row.url != url:
                                row.update_record(url=url)
                            if row.pos != pos:
                                row.update_record(pos=pos)
                        else:
                            db.vlakno.insert(tema_id=tema1.id, vlakno=txt, url=url, aktivni=True, pos=pos)
                    pos += 1  # bez ohledu na posledni, aby se zbytečně neaktualizovalo pos
    return 'Ok.'

@auth.requires_membership('admin')
def seznam_vlaken():
    return dict(grid=SQLFORM.grid(db.vlakno))
