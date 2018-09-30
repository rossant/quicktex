import os
import os.path as op
from pathlib import Path
import subprocess
import tempfile

from IPython.lib.latextools import genelatex, LaTeXTool
from PyQt5 import QtCore, QtGui, QtWidgets


def cmd(c, *args, tmpdir=None):
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
        tmpfile, tmpdir=tmpdir)
    return outfile


def dvi_ps(path):
    tmpdir = op.dirname(path)
    cmd('dvips %s -o %s', path, Path(path).with_suffix('.ps'), tmpdir=tmpdir)


def ps_pdf(path, output):
    tmpdir = op.dirname(path)
    cmd('gs -o %s -dNoOutputFonts -sDEVICE=pdfwrite -dEPSCrop %s',
        output, path, tmpdir=tmpdir)


def pdf_ps(path):
    tmpdir = op.dirname(path)
    cmd('pdf2ps %s', Path(path).with_suffix('.pdf'), path, tmpdir=tmpdir)


def dvi_png(path):
    tmpdir = op.dirname(path)
    cmd('dvipng -T tight -x 6000 -z 9 -bg transparent -o %s %s',
        Path(path).with_suffix('.png'),
        Path(path).with_suffix('.dvi'),
        tmpdir=tmpdir)


def make_svg(content, preamble='', outfile=None):
    LaTeXTool.instance().preamble = preamble
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpfile = latex(content, tmpdir=tmpdir)
        assert op.exists(tmpfile)
        cmd('dvisvgm %s -o %s', tmpfile, outfile)
        dvi_ps(tmpfile)
        psfile = Path(tmpfile).with_suffix('.ps')
        epsfile1 = Path(tmpfile).with_suffix('.eps')
        epsfile2 = Path(tmpfile).with_suffix('.tight.eps')
        assert op.exists(psfile)
        cmd('ps2eps %s', psfile)
        assert op.exists(epsfile1)
        cmd('epstool --bbox --copy %s %s', epsfile1, epsfile2)
        assert op.exists(epsfile2)
        pdffile = Path(tmpfile).with_suffix('.pdf')
        ps_pdf(epsfile2, pdffile)
        cmd('pdf2svg %s %s', pdffile, outfile)


def clipboard(path):
    app = QtWidgets.QApplication([])
    data = QtCore.QMimeData()
    url = 'file://' + op.realpath(path)
    data.setUrls([QtCore.QUrl(url)])
    cb = app.clipboard()
    cb.setMimeData(data)


if __name__ == '__main__':
    preamble = r'\usepackage{chemfig}'
    content = r'''

%\setchemfig{cram width=3pt}
\definesubmol{a}{-P(=[::-90,0.75]O)(-[::90,0.75]HO)-}
\chemfig{[:-54]*5((--[::60]O([::-60]!aO([::-60]!aO([::60]!aHO))))<(-OH)
-[,,,,line width=2pt](-OH)>(-N*5(-=N-*6(-(-NH_2)=N-=N-)=_-))-O-)}

    '''
    outfile = 'file.svg'
    make_svg(content, preamble=preamble, outfile=outfile)
    clipboard(outfile)
