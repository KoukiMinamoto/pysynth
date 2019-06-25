pySynth
====
pySynth - Code-based Synthesizer on Python.

## Description
- Most soft synthesizers are processing on VST or AU environments on DAW software. 
  Futhermore, there is not a synthesizer such as processing with pure programming code, especially, **on python**.
  Thus, I made a module of the code-based synthesizer, **pySynth**, and this module can be used as a future synthesizer 
  using ML(Machine Learning) or **Neural Network**.
- You can use pySynth with extremely simple grammer!!! Enjoy!!
  
## Requirement
- pyaudio  
    ```sh
    $ pip3 install pyaudio 
    ```  
- pygame  
    ```sh
    $ pip3 install pygame
    ```  
  
You may need to install other dependencies. In that case, reference some detail of installation by yorself, sorry;)

## Install
1. Clone this repository on your PC.
    ```sh
    $ git clone https://github.com/KoukiMinamoto/pysynth.git
    ```
1. Add your directory path your pySynth is to PYTHONPATH.
    ```python
    import sys
    sys.path.append("<The directory path of pysynth>")
    ```
    or  
    `.bash_profile`
    ```sh
    eport PYTHONPATH='<The directory path of pysynth>'
    ```

## Usage with Example
1. Import modules you need.
    ```python
    from pysynth.synth import Series
    from pysynth.interface import MidiFromPCkey
    from pysynth.oscillator import SineWave
    from pysynth.amplifier import SimpleAmp
    from pysynth.controller import Envelope
    ```
1. First, instance a empty synth like below.
    ```python
    synth = Series()
    ```
1. Second, using `Series.stack()`, stack `Interface module`. 
   First layer of your synth must be Interface module.
    ```python
    in_layer = synth.stack(MidiFromPCkey())
    ```
1. Third, stack `Oscillator module`.
   Second layer of your synth must be Oscillator or Sampler module.
    ```python
    osc_sine = synth.stack(SineWave())
    ```
1. At last layer of your synth, You must add `Amplifier module` and can define master volume here.
    ```python
    amp_simple = synth.stack(SimpleAmp(volume=0.5))
    ```
1. In initial status, Envelope is not set on amplifier. So, you need to set `envelope module`.
    ```python
    # Make envelope (A: Attack, D: Decay, S: Sustain, R: Release).
    env = Envelope(A=0.1, D=0.1, S=1.0, R=0.1)
    # Assign master volume to env
    env.assign(amp_simple.amp).
    # Add env to your synth
    synth.implement(env)
    ```
1. If you finished assembly of your synth, run `series.completed()`.
    ```python
    synth.completed()
    ```
1. Finally, play your synth!! Have a good synth:)
   In case you stack `MidiFromPCkey`, C3 ~ C4, 1oct range, corresponds to key A ~ key K on PC key.
    ```python
    synth.play()
    ```
Detail and other example are in [/example]. Please refer to that.
    
## Author
- Name: FooU*
- Email: tomatomusicstudio@gmail.com
