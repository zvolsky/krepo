Mobile support w3 (based on w3.css)

Controller can return: w3, fs

without w3: all supports are added: w3 = {'w3', 'jquery', 'calendar', 'web2py'}  # web2py means ajax support
with w3: listed supports only are added, example: w3 = {'w3', 'jquery', 'calendar', 'web2py'}

without fs: <body> without style= is rendered
fs=<integer>: <body> renders with style="font-size: <integer>px;"
fs=None: <body> renders with style="font-size: <xxx>px;" where xxx is: session.fs or auth.user.fs or 14
  see krepo/default/fontsize for user setting of font-size


Hints:

with fs, .btnRow class is defined: <div class="btnRow"> prevents included buttons to be smaller then 12px (to make them always well clickable)

to improve behaviour of full-width text use <div class="fwt">
  this style will be used: .fwt {padding: 0 3px; overflow-x: hidden;}
