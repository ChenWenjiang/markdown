# markdown/searializers.py
#
# Add x/html serialization to Elementree
# Taken from ElementTree 1.3 preview with slight modifications
#
# Copyright (c) 1999-2007 by Fredrik Lundh.  All rights reserved.
#
# fredrik@pythonware.com
# http://www.pythonware.com
#
# --------------------------------------------------------------------
# The ElementTree toolkit is
#
# Copyright (c) 1999-2007 by Fredrik Lundh
#
# By obtaining, using, and/or copying this software and/or its
# associated documentation, you agree that you have read, understood,
# and will comply with the following terms and conditions:
#
# Permission to use, copy, modify, and distribute this software and
# its associated documentation for any purpose and without fee is
# hereby granted, provided that the above copyright notice appears in
# all copies, and that both that copyright notice and this permission
# notice appear in supporting documentation, and that the name of
# Secret Labs AB or the author not be used in advertising or publicity
# pertaining to distribution of the software without specific, written
# prior permission.
#
# SECRET LABS AB AND THE AUTHOR DISCLAIMS ALL WARRANTIES WITH REGARD
# TO THIS SOFTWARE, INCLUDING ALL IMPLIED WARRANTIES OF MERCHANT-
# ABILITY AND FITNESS.  IN NO EVENT SHALL SECRET LABS AB OR THE AUTHOR
# BE LIABLE FOR ANY SPECIAL, INDIRECT OR CONSEQUENTIAL DAMAGES OR ANY
# DAMAGES WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS,
# WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS
# ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR PERFORMANCE
# OF THIS SOFTWARE.
# --------------------------------------------------------------------


from __future__ import absolute_import
from __future__ import unicode_literals
from xml.etree.ElementTree import ProcessingInstruction
from . import util
ElementTree = util.etree.ElementTree
QName = util.etree.QName
if hasattr(util.etree, 'test_comment'):  # pragma: no cover
    Comment = util.etree.test_comment
else:  # pragma: no cover
    Comment = util.etree.Comment

__all__ = ['to_html_string', 'to_xhtml_string']

HTML_EMPTY = ("area", "base", "basefont", "br", "col", "frame", "hr",
              "img", "input", "isindex", "link", "meta", "param")

try:
    HTML_EMPTY = set(HTML_EMPTY)
except NameError:  # pragma: no cover
    pass


def _raise_serialization_error(text):  # pragma: no cover
    raise TypeError(
        "cannot serialize %r (type %s)" % (text, type(text).__name__)
        )


def _escape_cdata(text):
    # escape character data
    try:
        # it's worth avoiding do-nothing calls for strings that are
        # shorter than 500 character, or so.  assume that's, by far,
        # the most common case in most applications.
        if "&" in text:
            text = text.replace("&", "&amp;")
        if "<" in text:
            text = text.replace("<", "&lt;")
        if ">" in text:
            text = text.replace(">", "&gt;")
        return text
    except (TypeError, AttributeError):  # pragma: no cover
        _raise_serialization_error(text)


def _escape_attrib(text):
    # escape attribute value
    try:
        if "&" in text:
            text = text.replace("&", "&amp;")
        if "<" in text:
            text = text.replace("<", "&lt;")
        if ">" in text:
            text = text.replace(">", "&gt;")
        if "\"" in text:
            text = text.replace("\"", "&quot;")
        if "\n" in text:
            text = text.replace("\n", "&#10;")
        return text
    except (TypeError, AttributeError):  # pragma: no cover
        _raise_serialization_error(text)


def _escape_attrib_html(text):
    # escape attribute value
    try:
        if "&" in text:
            text = text.replace("&", "&amp;")
        if "<" in text:
            text = text.replace("<", "&lt;")
        if ">" in text:
            text = text.replace(">", "&gt;")
        if "\"" in text:
            text = text.replace("\"", "&quot;")
        return text
    except (TypeError, AttributeError):  # pragma: no cover
        _raise_serialization_error(text)


def _serialize_html(write, elem, format):
    tag = elem.tag
    text = elem.text
    if tag is Comment:
        write("<!--%s-->" % _escape_cdata(text))
    elif tag is ProcessingInstruction:
        write("<?%s?>" % _escape_cdata(text))
    elif tag is None:
        if text:
            write(_escape_cdata(text))
        for e in elem:
            _serialize_html(write, e, format)
    else:
        namespace_uri = None
        if isinstance(tag, QName):
            # QNAME objects store their data as a string: `{uri}tag`
            if tag.text[:1] == "{":
                namespace_uri, tag = tag.text[1:].split("}", 1)
            else:
                raise ValueError('QName objects must define a tag.')
        write("<" + tag)
        items = elem.items()
        if items:
            items = sorted(items)  # lexical order
            for k, v in items:
                if isinstance(k, QName):
                    # Assume a text only QName
                    k = k.text
                if isinstance(v, QName):
                    # Assume a text only QName
                    v = v.text
                else:
                    v = _escape_attrib_html(v)
                if k == v and format == 'html':
                    # handle boolean attributes
                    write(" %s" % v)
                else:
                    write(' %s="%s"' % (k, v))
        if namespace_uri:
            write(' xmlns="%s"' % (_escape_attrib(namespace_uri)))
        if format == "xhtml" and tag.lower() in HTML_EMPTY:
            write(" />")
        else:
            write(">")
            if text:
                if tag.lower() in ["script", "style"]:
                    write(text)
                else:
                    write(_escape_cdata(text))
            for e in elem:
                _serialize_html(write, e, format)
            if tag.lower() not in HTML_EMPTY:
                write("</" + tag + ">")
    if elem.tail:
        write(_escape_cdata(elem.tail))


def _write_html(root, format="html"):
    assert root is not None
    data = []
    write = data.append
    _serialize_html(write, root, format)
    return "".join(data)


# --------------------------------------------------------------------
# public functions

def to_html_string(element):
    return _write_html(ElementTree(element).getroot(), format="html")


def to_xhtml_string(element):
    return _write_html(ElementTree(element).getroot(), format="xhtml")
