import mido
import songstruct as music
import re
import music21
from music21 import midi
from mido import MidiFile
from mido import messages
import numpy as np
import operator



class MidiInvalidException(Exception):
    pass


class MidiConnector:


    midi_in = ("/home/ibis/Desktop/midi_learning/PythonMidi/midi_data/bwv775.mid")
    mid = mido.MidiFile("/home/ibis/Desktop/midi_learning/PythonMidi/midi_data/bwv775.mid")


    # If MIDI_TRACK_COUNT IS > 3 RUN THIS FUNCTION ON MID
    def merge_remove_duplicates(mid):
        message_numbers = []
        duplicates = []

        for track in mid.tracks:
            if len(track) in message_numbers:
                duplicates.append(track)
            else:
                message_numbers.append(len(track))

        for track in duplicates:
            mid.tracks.remove(track)


    def letter_filt(self):
        return ''.join(filter(lambda x: x.isdigit(), list(self)))

        #batch this function so it creates a list of keys every few notes
    def get_key(midi_in):
        score = music21.converter.parse(midi_in)
        key = score.analyze('Krumhansl')
        return key.tonic.name, key.mode

        #TODO FIX
    #def time_signature_calc(mid):
    def tracks_len(mid):
        len_list = []
        one = len(mid.tracks[0])
        two = len(mid.tracks[1])
        three = len(mid.tracks[2])
        len_list = [
        one,
        two,
        three
        ]
        return len_list

    def printStatements(midtype):
        print('Programing starting.....\nReading MIDI file & extracting general information')
        print('MIDI type is {}'.format(midtype))
        print('Key of the MIDI = {}'.format(MIDI_TRACK_KEY))
        print('BPM of the MIDI = {}'.format(MIDI_TRACK_KEY))
        print('MIDI track length = {}'.format(MIDI_TRACK_LENGTH))
        print('MIDI tick per beat = {}'.format(MIDI_TICKS_PER_BEAT))
        print('MIDI track info:')
        print([i for i in mid.tracks])
        print('\n')

    def timeSignature_calc():
        pass

    #not sure if this works
    def grab_dataTime(mid, MIDI_TICKS_PER_BEAT, tempo):
        import mido
        microseconds_per_beat= 60 * 1000000 / tempo
        tickLength = microseconds_per_beat / MIDI_TICKS_PER_BEAT  #60,000 / 750 ms = 80 BPM
        last_event_ticks = 0
        microseconds = 0
        delta_microseconds = 0
        event_ticks = 0
        for i, track in enumerate(mid.tracks[1:]):
            for message in track:
                event_ticks = message.time
                if event_ticks > 0:
                    currentMillis = event_ticks * 60000 / MIDI_TICKS_PER_BEAT / tempo
                    microseconds += currentMillis
                    seconds = microseconds / 1000
                    delta_ticks = event_ticks - last_event_ticks
                    last_event_ticks = event_ticks
                    delta_microseconds = tempo * delta_ticks / MIDI_TICKS_PER_BEAT
                    microseconds += delta_microseconds


    META_INFO_TYPES = [  # Info Can safely be ignored
        'midi_port',
        'track_name',
        'lyrics',
        'end_of_track',
        'copyright',
        'marker',
        'text'
    ]


    META_TEMPO_TYPES = [  # Have an impact on how the song is played
        'key_signature',
        'set_tempo',
        'time_signature'
    ]

    MIDI_MINIMUM_TRACK_LENGTH = 4  # Bellow this value, the track will be ignored

    MIDI_CHANNEL_DRUMS = 10  # The channel reserved for the drums (according to the specs)

    MIDI_TYPE = mid.type # Storn{}'e Track type or later usage.

    MIDI_TICKS_PER_BEAT = mid.ticks_per_beat

    MIDI_TRACKS_BPM = 120

    MIDI_TRACKS_COUNT = (len(mid.tracks))

    MIDI_TRACK_LENGTH = tracks_len(mid)

    MIDI_TRACK_KEY = get_key(midi_in)

    MIDI_TRACK_BPM = 1



    # 3 midi types:
    #---------------------------
    # * type 0 (single track): all messages are saved in one multi-channel track
    # * type 1 (synchronous): all tracks start at the same time
    # * type 2 (asynchronous): each track is independent of the others


    printStatements(mid.type, MIDI_TRACK_KEY, MIDI_TRACK_KEY, MIDI_TRACK_LENGTH, MIDI_TICKS_PER_BEAT, mid.tracks)

    if MIDI_TRACKS_COUNT > 3:
        merge_remove_duplicates(mid)


    tempo_map = mid.tracks[0]
    key = []
    n_song = music.Song()

    # Merge tracks ? < Not when creating the dataset
    #midi_data.tracks = [mido.merge_tracks(midi_data.tracks)] ??

    #Creating an intial Tempo Map
    for message in tempo_map:
        if not isinstance(message, mido.MetaMessage):
            raise MidiInvalidException('Tempo map should not contains notes')
        if message.type in META_INFO_TYPES:
            pass
            # TODO take out unccesary information
            #possible
        elif message.type == 'set_tempo':
            n_song.tempo_map.append(message)
        elif message.type in META_TEMPO_TYPES:
            key.append(message)
        elif message.type == 'smpte_offset':
            pass  #TODO handle SMTPE_OFFSET
        else:
            err_msg = 'Header track contains unsupported meta-message type ({})'.format(message.type)
            raise MidiInvalidException(err_msg)


    #FORMATING TIME SIGNATURE information
    #TODO Make more efficent for formatting.
    # I am sure there is a better way to do this
    sig = []
    formated = []
    time_sig = re.sub('<meta message time_signature ', '', str(key))
    time_sig = re.sub('clocks_per_', '', time_sig)
    time_sig = re.sub('_notes_', ' ', time_sig)
    time_sig = re.sub('_', ', ', time_sig)
    time_sig = re.sub('>', '', time_sig)
    time_sig = re.sub('per, beat', 'per_beat', time_sig)
    time_sig = re.sub(', ', '=', time_sig)

    #List Spllits
    #This is not neccesary right now
    not_allowed = [
        '<meta',
        'message',
        'clocks_per_',
        '_notes_',
        'time_signature'
    ]

    #<meta message time_signature numerator=4 denominator=4
    #clocks_per_click=24 notated_32nd_notes_per_beat=8 time=0>

    #META MESSAGES FORMATING
    sig_lst = [sig for sig in time_sig.split(" ")]
    sig_lst = [s.replace('=', ' ') for s in sig_lst]
    for item in sig_lst[0:5]:
        formated.append(item)

    # Intial Time Signature veriables
    numerator = []
    denominator = []
    clocks_per_click = []
    notated_in = []
    per_beat = []

    #Add and seperate values
    for itemX in formated:
        numerator.append(itemX)
        denominator.append(itemX)
        clocks_per_click.append(itemX)
        notated_in.append(itemX)
        per_beat.append(itemX)

    #Filter Digites out of values

    numerator = letter_filt(numerator[0])
    denominator = letter_filt(denominator[1])
    clocks_per_click = letter_filt(clocks_per_click[2])
    notated_in = letter_filt(notated_in[3])
    per_beat = letter_filt(per_beat[4])

    info_string = ('Time signature = {}/{}, clocks per click = {} and is notated in {} notes per beat = {}\n\n')
    print(info_string.format(numerator, denominator, clocks_per_click, notated_in, per_beat))

                         # We ignore the tempo
    for i, track in enumerate(mid.tracks[1:]):  # We ignore the tempo map
        i += 1
        # We ignore the tempo map
        # Warning: We have skipped the track 0 so shift the track id
        #tqdm.write('Track {}: {}'.format(i, track.name))

        n_track = music.Track()

        buffer_notes = []  # Store the current notes (pressed but not released)
        abs_tick = 0  # Absolute nb of ticks from the beginning of the track
        for message in track: #Iterating through MIDI tracks 1int
            abs_tick += message.time #Assigning absolute numbers of ticks to abs_ticks
            if isinstance(message, mido.MetaMessage): # Lyrics, track name and other meta info
                if message.type in META_INFO_TYPES:
                    message = [y for y in track if type(y) != mido.MetaMessage]
                    # Iterate remove of Meta Message
                elif track.type in META_TEMPO_TYPES:
                        # TODO: Could be just a warning
                        #TODORE-assign to a veriable contanin updated info
                    raise MidiInvalidException('Track {} should not contain {}'.format(i, messages.type))
                else:
                    err_msg = 'Track {} contains unsupported meta-message type ({})'.format(i, messages.type)

                    raise MidiInvalidException(err_msg)
                # What about 'sequence_number', cue_marker ???

            else: # Adding note events to Class Note: in Songstruct
                if message.type == 'note_on' and message.velocity != 0:  # Note added
                    new_note = music.Note() #Define class call
                    new_note.tick = abs_tick
                    new_note.note = message.note
