b = NetAddr("127.0.0.1", port:9999)

// use reset to return notochord to a naive state (the beginning of a performance)
b.sendMsg("/notochord/reset")

////////// FEED //////////

// use feed to inform notochord of MIDI events in the stream
// instrument, pitch, delta time (in seconds), velocity
// dt of the very first event doesn't really matter, but should be close to 0
//instrument = grand piano (1), pitch=C (60), dt=0, velocity=99
b.sendMsg("/notochord/feed", 1, 60, 0, 99)
// dt is the elapsed time since the previous event.
// to tell notochord the note lasted for half a second:
b.sendMsg("/notochord/feed", 1, 60, 0.5, 0) // dt=500ms, noteOff (velocity=0)
// you can have polyphony simply by starting everal notes before sending any noteoffs,
// but note that delta time is *not* note duration,
// it's the time between events in the stream.
// for example to play a chord, use dt=0 to represent simultaneous events:
(
b.sendMsg("/notochord/feed", 1, 60, 0.1, 99);
b.sendMsg("/notochord/feed", 1, 64, 0, 99);
b.sendMsg("/notochord/feed", 1, 67, 0, 99);
b.sendMsg("/notochord/feed", 1, 60, 0.5, 0); // sustain for 0.5 seconds
b.sendMsg("/notochord/feed", 1, 64, 0, 0);
b.sendMsg("/notochord/feed", 1, 67, 0, 0);
)
// notchord represents multiple parts using general MIDI instruments instead of channels.
// this means you can have more than 16 parts, but only one part per instrument.
// these are numbered from 1, so they match the table here: https://en.wikipedia.org/wiki/General_MIDI#Program_change_events
// instruments 129-256 are drumkits
// there are also 'anonymous' parts, numbered 257-288 (melodic) and 289-320 (drums)

////////// QUERY //////////
OSCdef.trace(false)
// use query to ask notochord for predictions on the next event in the stream
(
OSCdef(\notoreturn, { arg msg;
	msg[0].postln;
	// assign the prediction to p:
	p = Dictionary.newFrom(msg[1..]).postln;
}, "/return/notochord/query")
)
// a completely random sample from the notochord distribution on next event:
b.sendMsg("/notochord/query")
// sample conditional on the constraint that the next instrument will be grand piano and it will be a NoteOn:
b.sendMsg("/notochord/query", \next_inst, 1, \min_vel, 1)
// next_inst is a hard constrain that the next instrument will be exactly 1 (grand piano)
// min_vel is a soft constraint that the next velocity is anything other than 0 (noteOff)

// suppose 2.5 seconds have elapsed since the last event in stream, and you want to query
// for a new event -- you should ask notochord not predict a delta time smaller than
// 2.5, which would be in the past:
b.sendMsg("/notochord/query", \min_time, 2.5)

// by default, notochord doesn't 'feed' the events you query --
// since you might want to mess with the predictions first,
// or do something other than actually play them.
// if you *do* want to accept notochord's prediction, you can do it in one call with
// query_feed, which feeds the result of the query internally:
b.sendMsg("/notochord/query_feed", \min_time, 2.5)
// query_feed accepts all the same parameters as query

// there is also feed_query which accepts the 4 positional arguments to feed,
// followed by any of the key-value pairs of argments to query.
// this lets you feed an event and immediately get a query on the next event:
(
// play a random note of duration 0.2 and ask which note starts next:
b.sendMsg("/notochord/feed", 1, p[\pitch], 0, 99);
b.sendMsg("/notochord/feed_query", 1, p[\pitch], 0.2, 0, \next_inst, 1, \min_vel, 1)
)




