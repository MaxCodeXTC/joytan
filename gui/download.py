import os, requests

from bavl.parser import Parsers
from gui.progress import ProgressDialog
from gui.utils import processCoreEvents

def onDownload(mw):
    # Look up Frame Manager of the MainWindow for the state of contents in bundles
    # to choose the right downloading method, i.e. needs to download partially or totally?
    # And also probably selecting a dictionary parser and passing it to the method,
    # which abstract parser for each downloading method sounds good.
    # - e.g partialDownload(mw, parser)
    parser = Parsers[mw.fm.targetDict]()
    ignorantDownload(mw.fm, parser)

    mw.framelist.updateBundles()


def ignorantDownload(fm, parser, gstat=False):
    pd = ProgressDialog(fm.getFrameLength(), msg="Downloading...")
    pd.show()

    for cnt, name in enumerate(fm.getBundleNames()):
        # This tip probably makes pd faster to display.
        pd.setValue(cnt)
        processCoreEvents()

        r = requests.get(fm.dictURLs[fm.targetDict] + name)
        data = r.text
        bitems = parser.run(data)

        downloadGstaticSound(name, "{dir}/{name}/gstatic.mp3".format(dir=fm.getRootPath(), name=name))

        fm.setBitemByName(name, bitems)

def downloadGstaticSound(word, filename):
    url = "http://ssl.gstatic.com/dictionary/static/sounds/oxford/"
    gb1 = "--_gb_1.mp3"  # A trailing type for gstatic dictionary
    gb18 = "--_gb_1.8.mp3"  # A trailing type for gstatic dictionary

    for w_key in [word + gb1, word + gb18, "x" + word + gb18]:
        r = requests.get(url + w_key, stream=True)
        if r.ok:
            break
        elif w_key == "x" + word and not r.ok:
            raise Exception("Audio for '" + word + "' not found")

    os.makedirs(os.path.dirname(filename), exist_ok=True)

    with open(filename, "wb") as f:
        f.write(r.content)