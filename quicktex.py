import base64
import os
import os.path as op
from pathlib import Path
import subprocess
import tempfile

from IPython.lib.latextools import genelatex, LaTeXTool
from flask import Flask, Response, render_template


def cmd(c, args, tmpdir=None):
    with open(os.devnull, 'w') as devnull:
        try:
            subprocess.check_call(
                (c % args).split(' '), cwd=tmpdir,
                stdout=devnull, stderr=devnull)
        except Exception as e:
            raise(e)


def latex(content, tmpdir=None):
    tmpfile = op.join(tmpdir, 'tmp.tex')
    outfile = Path(tmpfile).with_suffix('.dvi')
    lines = list(genelatex(content, False))
    with open(tmpfile, 'w') as f:
        f.writelines(lines)
    cmd('latex -halt-on-error %s',
        (tmpfile,), tmpdir=tmpdir)
    return outfile


def dvi_ps(path):
    tmpdir = op.dirname(path)
    cmd('dvips %s -o %s', (path, Path(path).with_suffix('.ps')), tmpdir=tmpdir)


def ps_pdf(path, output):
    tmpdir = op.dirname(path)
    cmd('gs -o %s -dNoOutputFonts -sDEVICE=pdfwrite -dEPSCrop %s',
        (output, path), tmpdir=tmpdir)


def make_svg(content, preamble='', outfile=None):
    LaTeXTool.instance().preamble = preamble
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpfile = latex(content, tmpdir=tmpdir)
        outfile = outfile or op.join(tmpdir, 'tmp.svg')
        assert op.exists(tmpfile)
        cmd('dvisvgm %s -o %s', (tmpfile, outfile))
        dvi_ps(tmpfile)
        psfile = Path(tmpfile).with_suffix('.ps')
        epsfile1 = Path(tmpfile).with_suffix('.eps')
        epsfile2 = Path(tmpfile).with_suffix('.tight.eps')
        assert op.exists(psfile)
        cmd('ps2eps -f %s', (psfile,))
        assert op.exists(epsfile1)
        cmd('epstool --bbox --copy %s %s', (epsfile1, epsfile2))
        assert op.exists(epsfile2)
        pdffile = Path(tmpfile).with_suffix('.pdf')
        ps_pdf(epsfile2, pdffile)
        assert op.exists(pdffile)
        cmd('pdf2svg %s %s', (pdffile, outfile))
        assert op.exists(outfile)
        with open(outfile, 'r') as f:
            svg = f.read()
        return svg


app = Flask(__name__)


@app.route("/latex/<b64content>")
def convert(b64content):
    preamble = r'\usepackage{chemfig}'
    content = base64.b64decode(b64content).decode('utf-8')
    outfile = op.join(op.dirname(__file__), 'output.svg')
    svg = make_svg(content, preamble=preamble, outfile=outfile)
    return Response(svg, mimetype='image/svg+xml')


@app.route("/")
def main():
    return render_template('index.html')
