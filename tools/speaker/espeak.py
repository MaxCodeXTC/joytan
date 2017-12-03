
from tools.speaker import *
from gui.utils import LANGUAGES, LANGCODES

def getTtsHelp():
    i1 = str(check_output("espeak --voices", shell=True), 'utf-8').strip().split('\n')
    i2 = [' '.join(row.split()) for row in i1]
    i3 = [i.split(' ')[1:4] for i in i2[1:]]
    for info in i3:
        # Remove sex
        info.remove(info[1])
        info.insert(0, info[0].split('-')[0])
    return i3


class Espeak(BaseSpeaker):
    # We want to call TTS help command only once at runtime.
    # Don't call the command every time voice type changed.
    from gui.utils import isWin, isLin
    if isWin or isLin:
        infos = getTtsHelp()

        code2Vids= {key: {'Not Available': None} for key in LANGUAGES}

        for info in infos:
            if info[0] in code2Vids:
                code2Vids[info[0]][info[2]] = info[1]
                if 'Not Available' in code2Vids[info[0]]:
                    del code2Vids[info[0]]['Not Available']

    def __init__(self):
        pass

    def dictate(self, script, voiceId, output=None):
        print("Script: %s (%s)" % (script, voiceId))

        if output:
            os.makedirs(os.path.dirname(output), exist_ok=True)
            self.save(script, output, voiceId=voiceId)
        else:
            cmd = 'espeak -v {vid} "{script}"'.format(vid=voiceId, script=script)
            call(cmd, shell=True)


    def save(self, script, output, voiceId=None):
        if isWin:
            cmd = 'espeak -v {lang} -w {out}.wav "{script}"'.format(lang=voiceId, out=output, script=script)
            call(cmd, shell=True)
            cmd = 'ffmpeg -loglevel panic -i {out}.wav -ac 2 -ar 44100 -ab 64k -f mp3 {out}.mp3'.format(out=output)
            call(cmd, shell=True)
        else:
            cmd = 'espeak -v {vid} "{script}" --stdout | '.format(vid=voiceId, script=script) + \
                  'ffmpeg -loglevel panic -i - -ac 2 -ar 44100 -ab 64k -f mp3 %s.mp3' % (output)
            call(cmd, shell=True)


    def isSupported(self):
        raise NotImplementedError

    def preview(self, voiceId, script='If any proper sample sentence is not found, I read this.'):
        self.dictate(script, voiceId)