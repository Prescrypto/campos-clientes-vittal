#!/usr/bin/env python

#
# Generated Sun Apr  2 03:02:59 2023 by generateDS.py version 2.41.3.
# Python 2.7.13 (default, Sep 26 2018, 18:42:22)  [GCC 6.3.0 20170516]
#
# Command line options:
#   ('-o', 'RequestCFD_v40.py')
#   ('-s', 'RequestCFD_v40subs.py')
#
# Command line arguments:
#   ResponseAdmon30v_CFDi40v.xsd
#
# Command line:
#   /vagrant/virtualenv/bin/generateDS -o "RequestCFD_v40.py" -s "RequestCFD_v40subs.py" ResponseAdmon30v_CFDi40v.xsd
#
# Current working directory (os.getcwd()):
#   models
#

import os
import sys
from lxml import etree as etree_

import ??? as supermod

def parsexml_(infile, parser=None, **kwargs):
    if parser is None:
        # Use the lxml ElementTree compatible parser so that, e.g.,
        #   we ignore comments.
        parser = etree_.ETCompatXMLParser()
    try:
        if isinstance(infile, os.PathLike):
            infile = os.path.join(infile)
    except AttributeError:
        pass
    doc = etree_.parse(infile, parser=parser, **kwargs)
    return doc

def parsexmlstring_(instring, parser=None, **kwargs):
    if parser is None:
        # Use the lxml ElementTree compatible parser so that, e.g.,
        #   we ignore comments.
        try:
            parser = etree_.ETCompatXMLParser()
        except AttributeError:
            # fallback to xml.etree
            parser = etree_.XMLParser()
    element = etree_.fromstring(instring, parser=parser, **kwargs)
    return element

#
# Globals
#

ExternalEncoding = ''
SaveElementTreeNode = True

#
# Data representation classes
#


class ResponseAdmonSub(supermod.ResponseAdmon):
    def __init__(self, version='3.0', fechaCreacion=None, Transaccion=None, CFD=None, Proveedor=None, TFD=None, Error=None, **kwargs_):
        super(ResponseAdmonSub, self).__init__(version, fechaCreacion, Transaccion, CFD, Proveedor, TFD, Error,  **kwargs_)
supermod.ResponseAdmon.subclass = ResponseAdmonSub
# end class ResponseAdmonSub


class TransaccionTypeSub(supermod.TransaccionType):
    def __init__(self, id=None, tipo=None, estatus=None, folioConfirmacion=None, **kwargs_):
        super(TransaccionTypeSub, self).__init__(id, tipo, estatus, folioConfirmacion,  **kwargs_)
supermod.TransaccionType.subclass = TransaccionTypeSub
# end class TransaccionTypeSub


class CFDTypeSub(supermod.CFDType):
    def __init__(self, serie=None, folio=None, fecha=None, sello=None, noAprobacion=None, anoAprobacion=None, noCertificado=None, cadenaOriginal=None, comprobanteStr=None, codigoDeBarras=None, **kwargs_):
        super(CFDTypeSub, self).__init__(serie, folio, fecha, sello, noAprobacion, anoAprobacion, noCertificado, cadenaOriginal, comprobanteStr, codigoDeBarras,  **kwargs_)
supermod.CFDType.subclass = CFDTypeSub
# end class CFDTypeSub


class ProveedorTypeSub(supermod.ProveedorType):
    def __init__(self, rfc=None, nombre=None, noAutorizacion=None, fechaAutorizacion=None, sello=None, noCertificado=None, **kwargs_):
        super(ProveedorTypeSub, self).__init__(rfc, nombre, noAutorizacion, fechaAutorizacion, sello, noCertificado,  **kwargs_)
supermod.ProveedorType.subclass = ProveedorTypeSub
# end class ProveedorTypeSub


class TFDTypeSub(supermod.TFDType):
    def __init__(self, UUID=None, FechaTimbrado=None, noCertificadoSAT=None, selloSAT=None, **kwargs_):
        super(TFDTypeSub, self).__init__(UUID, FechaTimbrado, noCertificadoSAT, selloSAT,  **kwargs_)
supermod.TFDType.subclass = TFDTypeSub
# end class TFDTypeSub


class ErrorTypeSub(supermod.ErrorType):
    def __init__(self, noIdentificacion=None, descripcion=None, **kwargs_):
        super(ErrorTypeSub, self).__init__(noIdentificacion, descripcion,  **kwargs_)
supermod.ErrorType.subclass = ErrorTypeSub
# end class ErrorTypeSub


def get_root_tag(node):
    tag = supermod.Tag_pattern_.match(node.tag).groups()[-1]
    rootClass = None
    rootClass = supermod.GDSClassesMapping.get(tag)
    if rootClass is None and hasattr(supermod, tag):
        rootClass = getattr(supermod, tag)
    return tag, rootClass


def parse(inFilename, silence=False):
    parser = None
    doc = parsexml_(inFilename, parser)
    rootNode = doc.getroot()
    rootTag, rootClass = get_root_tag(rootNode)
    if rootClass is None:
        rootTag = 'ResponseAdmon'
        rootClass = supermod.ResponseAdmon
    rootObj = rootClass.factory()
    rootObj.build(rootNode)
    # Enable Python to collect the space used by the DOM.
    if not SaveElementTreeNode:
        doc = None
        rootNode = None
    if not silence:
        sys.stdout.write('<?xml version="1.0" ?>\n')
        rootObj.export(
            sys.stdout, 0, name_=rootTag,
            namespacedef_='',
            pretty_print=True)
    return rootObj


def parseEtree(inFilename, silence=False):
    parser = None
    doc = parsexml_(inFilename, parser)
    rootNode = doc.getroot()
    rootTag, rootClass = get_root_tag(rootNode)
    if rootClass is None:
        rootTag = 'ResponseAdmon'
        rootClass = supermod.ResponseAdmon
    rootObj = rootClass.factory()
    rootObj.build(rootNode)
    mapping = {}
    rootElement = rootObj.to_etree(None, name_=rootTag, mapping_=mapping)
    reverse_mapping = rootObj.gds_reverse_node_mapping(mapping)
    # Enable Python to collect the space used by the DOM.
    if not SaveElementTreeNode:
        doc = None
        rootNode = None
    if not silence:
        content = etree_.tostring(
            rootElement, pretty_print=True,
            xml_declaration=True, encoding="utf-8")
        sys.stdout.write(content)
        sys.stdout.write('\n')
    return rootObj, rootElement, mapping, reverse_mapping


def parseString(inString, silence=False):
    if sys.version_info.major == 2:
        from StringIO import StringIO
    else:
        from io import BytesIO as StringIO
    parser = None
    rootNode= parsexmlstring_(inString, parser)
    rootTag, rootClass = get_root_tag(rootNode)
    if rootClass is None:
        rootTag = 'ResponseAdmon'
        rootClass = supermod.ResponseAdmon
    rootObj = rootClass.factory()
    rootObj.build(rootNode)
    # Enable Python to collect the space used by the DOM.
    if not SaveElementTreeNode:
        rootNode = None
    if not silence:
        sys.stdout.write('<?xml version="1.0" ?>\n')
        rootObj.export(
            sys.stdout, 0, name_=rootTag,
            namespacedef_='')
    return rootObj


def parseLiteral(inFilename, silence=False):
    parser = None
    doc = parsexml_(inFilename, parser)
    rootNode = doc.getroot()
    rootTag, rootClass = get_root_tag(rootNode)
    if rootClass is None:
        rootTag = 'ResponseAdmon'
        rootClass = supermod.ResponseAdmon
    rootObj = rootClass.factory()
    rootObj.build(rootNode)
    # Enable Python to collect the space used by the DOM.
    if not SaveElementTreeNode:
        doc = None
        rootNode = None
    if not silence:
        sys.stdout.write('#from ??? import *\n\n')
        sys.stdout.write('import ??? as model_\n\n')
        sys.stdout.write('rootObj = model_.rootClass(\n')
        rootObj.exportLiteral(sys.stdout, 0, name_=rootTag)
        sys.stdout.write(')\n')
    return rootObj


USAGE_TEXT = """
Usage: python ???.py <infilename>
"""


def usage():
    print(USAGE_TEXT)
    sys.exit(1)


def main():
    args = sys.argv[1:]
    if len(args) != 1:
        usage()
    infilename = args[0]
    parse(infilename)


if __name__ == '__main__':
    #import pdb; pdb.set_trace()
    main()
