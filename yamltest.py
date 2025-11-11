import yaml
from pprint import pprint
from io import StringIO

with open('config.yaml', 'r') as f:
    d = yaml.safe_load(f)
    d2 = d.copy()

    d2['addr'] = (19, 23, 34, 5)
f2 = StringIO()
yaml.safe_dump(d2, f2)
pprint(f2.getvalue())
f2.seek(0)
d3 = yaml.safe_load(f2)

print(d3)