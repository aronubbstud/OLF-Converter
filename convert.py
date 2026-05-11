import zipfile, json

with zipfile.ZipFile('analisis.olf') as olf_file:
    with olf_file.open('content.json') as content_file:
        content = json.loads(content_file.read())

##1.0     0.0     -10.9031982421875       x       x'
##0.0     1.0     -483.7773437500001  *   y   =   y'
##0.0     0.0     1.0                     1       1

##  svg       me    me but transponalt
##a c e    a b c    a d 0
##b d f    d e f    b e 0
##0 0 1    0 0 1    c f 1
class Matrix:
    def __init__(self, olf_str_repr_or_list):
        self.a, self.b, self.c, self.d, self.e, self.f, z1, z2, o1 = olf_str_repr_or_list if isinstance(olf_str_repr_or_list, list) else list(map(float, olf_str_repr_or_list.split(',')))
        assert z1 == 0 and z2 == 0 and o1 == 1
    def __repr__(self):
        return f'Matrix([{self.a}, {self.b}, {self.c}, {self.d}, {self.e}, {self.f}, 0, 0, 1])'
    def __str__(self): # SVG matrix format
        return ' '.join(map(str, [self.a, self.d, self.b, self.e, self.c, self.f]))
    def det(self):
        return (self.a*self.e) - (self.b*self.d)
    def inv(self):
        d = self.det()
        # ((self.a*self.e)-(self.d*self.b))/d = 1
        return Matrix([self.e/d, -self.b/d, ((self.b*self.f)-(self.e*self.c))/d, -self.d/d, self.a/d, (-(self.a*self.f)+(self.d*self.c))/d, 0, 0, 1])
    def mul(self, m):
        return Matrix([self.a*m.a+self.b*m.d, self.a*m.b+self.b*m.e, self.a*m.c+self.b*m.f+self.c, self.d*m.a+self.e*m.d, self.d*m.b+self.e*m.e, self.d*m.c+self.e*m.f+self.f, 0, 0, 1])

pages = content["olf"]["pageset"]
def convert_page(i):
    page = pages[i]["page"]
    background = "#FFFFFF"
    svg = f'<svg viewBox="{page["viewbox"]}">\n'
    for bg in page['backgrounds']:
        background = bg['background']
        if background['type'] == 'color':
            svg += f'<rect width="100%" height="100%" fill="{background["fill"]}" opacity="{background["opacity"]}" />\n'
    pg_inv_matrix = Matrix(page['matrix']).inv()
    for element in page["elements"]:
        stroke = element["stroke"]
        matrix = Matrix(stroke["matrix"]).mul(pg_inv_matrix)
        svg += f'<polyline stroke="{stroke["stroke"]}" stroke-width="{stroke["pen-width"]}" opacity="{stroke["opacity"]}" fill="none" transform="matrix({matrix})" points="{stroke["points"]}"/>\n'
    svg += '</svg>'
    return svg

import subprocess
out_pdfs = []
for i in range(len(pages)):
    out_svg = f'out/page{i}.svg'
    out_pdf = f'out/page{i}.pdf'
    with open(out_svg, 'wt') as o:
        o.write(convert_page(i))
        proc = subprocess.Popen(['inkscape', out_svg, '--export-area-drawing', '--batch-process', '--export-type=pdf', '--export-filename', out_pdf])
        assert proc.wait() == 0
        out_pdfs.append(out_pdf)

proc = subprocess.Popen(['pdfunite', *out_pdfs, 'output.pdf'])
assert proc.wait() == 0
