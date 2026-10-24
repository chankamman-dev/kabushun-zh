import sys; sys.path.insert(0,'tools')
import objedit, gfxpatch as g
def run(of, rep):
    g.restyle(of, 503, range(3,11), '平仓', rect=(16, 10, 112, 30), box=(30,11,98,29), fill=(255,255,255), outline=(0,16,120), stroke=1)
    g.restyle(of, 704, [6], '破产宣告')
    g.restyle(of, 704, range(7,12), '破产宣告', box=(4,3,124,29), fill=(255,50,50), outline=(120,240,255))
g.t_run = run
