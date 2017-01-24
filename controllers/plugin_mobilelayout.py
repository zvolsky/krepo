# -*- coding: utf-8 -*-


'''
# requires (in model (db.py), before auth.define_tables()):
auth.settings.extra_fields['auth_user'] = [
    Field('fs', 'integer', readable=False, writable=False, default=14),
    ]

# calling example
<a href="{{=URL('plugin_mobilelayout', 'fontsize', args='default/index/20')}}">set font size +/-</a>
'''


def fontsize():
    fs1 = session.fs or auth.user and auth.user.fs or 14
    if request.args(1):
        if request.args(1) == 'plus':
            fs1 = min(1000, int(fs1 * 1.1))
        elif request.args(1) == 'minus':
            fs1 = max(10, int(fs1 / 1.1))
        session.fs = fs1

    back_path = request.args(0)
    path_parts = back_path.split('-')
    back_url = URL(path_parts[0], path_parts[1], args=path_parts[2:])
    return dict(back_path=back_path, back_url=back_url, js={'w3'})
