#! /usr/bin/env python3
# Author: Scott Hawley
# Source: Igor Gadelha  https://github.com/igorgad/dpm/blob/master/prepare_data.py

# Used simple echo plugin from Faust examples, https://github.com/grame-cncm/faust/blob/master-dev/examples/delayEcho/echo.dsp
# Pasted source into Faust Online Compiler https://faust.grame.fr/onlinecompiler/
# and Generated exec file for Linux, 'vst-64bits' architecture

import numpy as np
import vstRender.vstRender as vr
import librosa
import argparse
import os

class Plugin():
    def __init__(self, plugin_file,sr=44100):
        print("Initializing plugin file",args.plugin_file)
        self.vst = vr.vstRender(sr, 512)
        self.vst.loadPlugin(plugin_file)

        # get vst parameters (names of 'knobs', etc)
        self.nparams = self.vst.getPluginParameterSize()
        self.params_description = self.vst.getPluginParametersDescription()
        self.params_description = [[int(i.split(':')[0]), i.split(':')[1].replace(' ', ''), float(i.split(':')[2]), int(i.split(':')[3])]
                              for i in self.params_description.split('\n')[:-1]]
        print("Plugin: nparams =",self.nparams)
        print("Plugin: params_description =",self.params_description)

    def vst_process_samples(self, samples, params):  # where the actual audio processing call happens
        pidx = params[0]    # list of 'knob' numbers
        pval = params[1]    # list of knob settings for each knob

        # match knob numbers with knob values
        parg = tuple([(int(i), float(j)) for i, j in zip(pidx, pval)])
        self.vst.setParams(parg)
        audio = samples.copy()         # renderAudio operates 'in place'
        self.vst.renderAudio(audio)
        return audio

    def run(self, audio_in, params):
        # call the plugin to apply to the audio
        audio_out = self.vst_process_samples(audio_in, params).astype(np.float32)
        return audio_out


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--plugin_file', type=str, default='./faust_delay.so', help='plugin to model')
    parser.add_argument('--audio_file', default='./music.wav', type=str, help='audio file to read from')
    parser.add_argument('--outfile', default='./vst_out.wav', type=str, help='wav file to create')
    parser.add_argument('--sr', default=44100, type=int, help='sample rate in Hertz')

    args = parser.parse_args()

    plugin = Plugin(args.plugin_file)     # load and initialize the plugin

    if os.path.isfile(args.audio_file):
        print ('Reading audio from',args.audio_file)
        audio_in, sr = librosa.core.load(args.audio_file, args.sr, mono=True)

        # set parameter values (randomly)
        pidx = np.arange(plugin.nparams)           # indices for parameters
        pval = np.random.random([plugin.nparams])  # values for those parameters
        params = [pidx, pval]

        audio_out = plugin.run(audio_in, params)   # apply the plugin to input audio

        print("Writing output to",args.outfile)
        librosa.output.write_wav(args.outfile, audio_out, args.sr)
    else:
        print("Error, audio file",args.audio_file,"not found")
