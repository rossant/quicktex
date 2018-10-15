import base64
import glob
import hashlib
import os
import os.path as op
from pathlib import Path
import subprocess
import tempfile

from IPython.lib.latextools import genelatex, LaTeXTool
from flask import Flask, Response, render_template, request, jsonify


DEFAULT_PREAMBLE = r'''
\usepackage{chemfig}
\setchemfig{atom sep=1.75em}
'''


DEFAULT_HEADER = r'''
'''


def sha(s):
    return hashlib.sha1(s.encode('utf-8')).hexdigest()


def b64encode(s):
    return base64.b64encode(s.encode('utf-8')).decode('utf-8')


def b64decode(b64):
    return base64.b64decode(b64).decode('utf-8')


def cmd(c, args, tmpdir=None):
    with open(os.devnull, 'w') as devnull:
        try:
            subprocess.check_call(
                (c % args).split(' '), cwd=tmpdir,
                stdout=devnull, stderr=devnull,
            )
        except Exception as e:
            raise(e)


def latex(content, tmpdir=None):
    content = content.strip() or '.'
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


def make_svg(content):
    LaTeXTool.instance().preamble = DEFAULT_PREAMBLE
    content = DEFAULT_HEADER + content
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpfile = latex(content, tmpdir=tmpdir)
        outfile = op.join(tmpdir, 'tmp.svg')
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


def cache_dir():
    cache = op.join(op.dirname(__file__), '.cache')
    if not op.exists(cache):
        os.mkdir(cache)
    return cache


def get_image_path(title):
    return op.join(cache_dir(), str(title) + '.svg')


app = Flask(__name__)


@app.route('/')
def main():
    return render_template('index.html')


@app.route('/images/<string:title>', methods=['POST', 'PUT', 'PATCH'])
def create_image(title):
    path = get_image_path(title)
    content = request.form['content']
    svg = make_svg(content)
    with open(path, 'w') as f:
        f.write(svg)
        # Add content as comment in the XML SVG file.
        f.write('<!--%s-->\n' % b64encode(content))
    return jsonify({'result': 'ok'})


@app.route('/images/<string:title>', methods=['GET'])
def get_image(title):
    path = get_image_path(title)
    if not op.exists(path):
        return jsonify({'error': 'File not found: %s' % path})
    with open(path, 'r') as f:
        svg = f.read()
    return Response(svg, mimetype='image/svg+xml')


@app.route('/images/<string:title>/code', methods=['GET'])
def get_code(title):
    svg = get_image(title).data.decode('utf-8')
    if ('<!--' not in svg):
        return jsonify({'error': 'Comment not found'})
    i = svg.index('<!--') + 4
    j = svg.index('-->')
    return jsonify({'response': b64decode(svg[i:j])})


@app.route('/images/<string:title>', methods=['DELETE'])
def delete_image(title):
    path = get_image_path(title)
    if op.exists(path):
        os.remove(path)
    return jsonify({'result': 'ok'})


@app.route('/images', methods=['GET'])
def list_images():
    images = sorted(
        [op.splitext(op.basename(f))[0]
         for f in glob.glob(op.join(cache_dir(), '*.svg'))])
    return jsonify({'images': images})
