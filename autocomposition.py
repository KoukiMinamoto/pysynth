#!/usr/bin/env python
# coding: utf-8

# In[2]:


from magenta.models.melody_rnn import melody_rnn_sequence_generator
from magenta.models.shared import sequence_generator_bundle
import note_seq
from note_seq.protobuf import generator_pb2
from note_seq.protobuf import music_pb2


# In[4]:


class AutoComposition():
    def __init__(self, bundle, method):
        self.bundle = bundle
        self.method = method
    
    def initialize(self):
        print("Initializing Melody RNN...")
        bundle = sequence_generator_bundle.read_bundle_file(self.bundle)
        generator_map = melody_rnn_sequence_generator.get_generator_map()
        self.melody_rnn = generator_map[self.method](checkpoint=None, bundle=bundle)
        self.melody_rnn.initialize()
    
    def generate(self, input_sequence):
        
        num_steps = 100 # change this for shorter or longer sequences
        temperature = 1.0 # the higher the temperature the more random the sequence.

        # Set the start time to begin on the next step after the last note ends.
        last_end_time = (max(n.end_time for n in input_sequence.notes) if input_sequence.notes else 0)
        qpm = input_sequence.tempos[0].qpm 
        seconds_per_step = 60.0 / qpm / self.melody_rnn.steps_per_quarter
        total_seconds = num_steps * seconds_per_step
        #print("steps_per_quarter: ", self.melody_rnn.steps_per_quarter)
        #print("seconds_per_step: ", seconds_per_step)
        #print("total_seconds: ", total_seconds)

        generator_options = generator_pb2.GeneratorOptions()
        generator_options.args['temperature'].float_value = temperature
        generate_section = generator_options.generate_sections.add(
          start_time=last_end_time + seconds_per_step,
          end_time=total_seconds)

        # Ask the model to continue the sequence.
        sequence = self.melody_rnn.generate(input_sequence, generator_options)

        #print(sequence)
        #note_seq.plot_sequence(sequence)
        #note_seq.play_sequence(sequence)
        
        return sequence
    
    def round_in_bar(self, note_sequence, bar):
        elim_index = []
        bar = note_sequence.total_time - bar
        for note in note_sequence.notes:
            note.start_time = note.start_time - bar
            note.end_time = note.end_time - bar
            
        for i, note in enumerate(note_sequence.notes):
            if note.start_time < 0:
                note.start_time = 0
            if note.end_time < 0:
                note.end_time = 0
        
        note_sequence.total_time = bar
        #note_seq.plot_sequence(note_sequence)
        
        return note_sequence
        
        
            

