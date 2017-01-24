plugin_mobilelayout
-------------------

Add static/css/w3.css, static/js/vue.min.js, static/js/jquery.min.js.
Use {{extend 'plugin_mobilelayout.html'}} in your view.

Controller can return: js, fs

without js: no js/css supports will be added
with js: list added supports as python set: js = {'w3', 'vue', ''jquery', 'calendar', 'web2py'}  # web2py means ajax support

without fs: <body> without style= is rendered
fs=<integer>: <body> renders with style="font-size: <integer>px;"
fs=None: <body> renders with style="font-size: <xxx>px;" where xxx is: session.fs or auth.user.fs or 14
  see krepo/default/fontsize for user setting of font-size


Hints:

with fs, .btnRow class is defined: <div class="btnRow"> prevents included buttons to be smaller then 12px (to make them always well clickable)

together with w3.css: to improve behaviour of full-width text use <div class="fwt">
  this style will be used: .fwt {padding: 0 3px; overflow-x: hidden;}

for vue.js (or other similar library) instead of changing web2py|vue delimiters you can do following:
controller (or model+controller):
    def JS(txt):
        return '{{%s}}' % txt
    return dict(js={'vue'}, JS=JS)
view:
    {{=JS('message')}}   ## -> {{message}} inside rendered .html
