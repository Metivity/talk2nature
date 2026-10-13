package org.talk2nature.station.engine;

import java.util.ArrayDeque;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collections;
import java.util.Comparator;
import java.util.List;

/** A small bounded energy detector. Events are acoustic highlights, never inferred meanings. */
public final class CaptureEngine {
    public static final int MAX_EVENTS = 24;
    public static final int MAX_AUDIO_BYTES = 24 * 1024 * 1024;
    private static final double CALIBRATION_SECONDS = 3.0;
    private static final double PRE_ROLL_SECONDS = 1.0;
    private static final double MAX_CLIP_SECONDS = 6.0;
    private static final double QUIET_END_SECONDS = 0.5;
    private static final double HYSTERESIS_DB = 4.0;
    private final int sampleRate;
    private final ArrayDeque<Frame> ring = new ArrayDeque<>();
    private final ArrayList<Double> calibration = new ArrayList<>();
    private Active active;
    private long samplesSeen;
    private long clippedSamples;
    private long totalSamples;
    private long retainedBytes;
    private double threshold = Double.NaN;
    private int nextId = 1;
    private int retainedEvents;
    private boolean stopped;
    private String stopReason;

    public CaptureEngine(int sampleRate) {
        if (sampleRate < 8000 || sampleRate > 96000) throw new IllegalArgumentException("Unsupported sample rate.");
        this.sampleRate = sampleRate;
    }

    public synchronized Result accept(short[] input, int length) {
        if (stopped || input == null || length < 1 || length > input.length || length > sampleRate / 5)
            throw new IllegalStateException("Capture is stopped or the audio frame is invalid.");
        double start = elapsedSeconds();
        double sumSquares = 0.0;
        double peak = 0.0;
        int clipped = 0;
        short[] pcm = Arrays.copyOf(input, length);
        for (short sample : pcm) {
            double value = sample / 32768.0;
            double magnitude = Math.abs(value);
            sumSquares += value * value;
            peak = Math.max(peak, magnitude);
            if (magnitude >= 0.999) clipped++;
        }
        samplesSeen += length;
        totalSamples += length;
        clippedSamples += clipped;
        double end = elapsedSeconds();
        double rms = Math.sqrt(sumSquares / length);
        double dbfs = Math.max(-100.0, 20.0 * Math.log10(Math.max(rms, 0.00001)));
        Frame frame = new Frame(start, end, pcm);

        if (Double.isNaN(threshold)) {
            calibration.add(dbfs);
            if (end >= CALIBRATION_SECONDS) {
                ArrayList<Double> levels = new ArrayList<>(calibration);
                Collections.sort(levels);
                double baseline = levels.get(levels.size() / 2);
                threshold = Math.min(-3.0, Math.max(-50.0, baseline + 12.0));
            }
        } else {
            boolean loud = dbfs >= (active == null ? threshold : threshold - HYSTERESIS_DB);
            if (active == null && loud) active = new Active(new ArrayList<>(ring), start);
            if (active != null) {
                active.frames.add(frame);
                active.peak = Math.max(active.peak, peak);
                active.quietSeconds = loud ? 0.0 : active.quietSeconds + length / (double) sampleRate;
                if (loud) active.lastLoudEnd = end;
                if (active.quietSeconds >= QUIET_END_SECONDS || end - active.frames.get(0).start >= MAX_CLIP_SECONDS)
                    return finishEvent(active.quietSeconds >= QUIET_END_SECONDS ? "quiet" : "clip_limit");
            }
        }

        addToRing(frame);
        return Result.empty();
    }

    public synchronized Result stop(String reason) {
        if (stopped) return Result.empty();
        Result result = active == null ? Result.empty() : finishEvent(reason);
        stopped = true;
        stopReason = result.storageLimit ? "storage_limit" : reason;
        ring.clear();
        active = null;
        return result;
    }

    public synchronized double elapsedSeconds() { return samplesSeen / (double) sampleRate; }
    public synchronized double thresholdDbfs() { return Double.isNaN(threshold) ? Double.NaN : round(threshold); }
    public synchronized double nearFullScaleFraction() { return totalSamples == 0 ? 0.0 : clippedSamples / (double) totalSamples; }
    public synchronized boolean isStopped() { return stopped; }
    public synchronized String stopReason() { return stopReason; }

    public synchronized Marker marker(String note) {
        if (stopped) throw new IllegalStateException("The session has stopped.");
        if (note == null || note.trim().isEmpty() || note.trim().length() > 300)
            throw new IllegalArgumentException("Add a short observation note (up to 300 characters).");
        return new Marker(round(elapsedSeconds()), note.trim());
    }

    private Result finishEvent(String reason) {
        Active current = active;
        active = null;
        if (current == null || current.frames.isEmpty()) return Result.empty();
        int sampleCount = 0;
        for (Frame frame : current.frames) sampleCount += frame.pcm.length;
        int pcmBytes = sampleCount * 2;
        int id = nextId++;
        double onset = round(current.onset);
        if (retainedEvents >= MAX_EVENTS || retainedBytes + pcmBytes + 44 > MAX_AUDIO_BYTES) {
            stopped = true;
            stopReason = "storage_limit";
            ring.clear();
            return new Result(null, new Tombstone(id, onset), true);
        }
        short[] samples = new short[sampleCount];
        int offset = 0;
        for (Frame frame : current.frames) {
            System.arraycopy(frame.pcm, 0, samples, offset, frame.pcm.length);
            offset += frame.pcm.length;
        }
        Event event = new Event(id, onset, round(current.lastLoudEnd), round(current.frames.get(0).start),
                round(current.frames.get(current.frames.size() - 1).end), round(threshold), round(current.peak), reason, samples);
        retainedEvents++;
        retainedBytes += pcmBytes + 44;
        ring.clear();
        boolean limit = retainedEvents >= MAX_EVENTS || retainedBytes >= MAX_AUDIO_BYTES;
        if (limit) {
            stopped = true;
            stopReason = "storage_limit";
        }
        return new Result(event, null, limit);
    }

    private void addToRing(Frame frame) {
        ring.addLast(frame);
        while (!ring.isEmpty() && frame.end - ring.peekFirst().start > PRE_ROLL_SECONDS + 0.05) ring.removeFirst();
    }

    private static double round(double value) { return Math.round(value * 10000.0) / 10000.0; }

    private static final class Frame {
        final double start, end;
        final short[] pcm;
        Frame(double start, double end, short[] pcm) { this.start = start; this.end = end; this.pcm = pcm; }
    }

    private static final class Active {
        final ArrayList<Frame> frames;
        final double onset;
        double lastLoudEnd;
        double quietSeconds;
        double peak;
        Active(ArrayList<Frame> frames, double onset) { this.frames = frames; this.onset = onset; this.lastLoudEnd = onset; }
    }

    public static final class Event {
        public final int id;
        public final double onsetSeconds, lastLoudSeconds, clipStartSeconds, clipEndSeconds, thresholdDbfs, peak;
        public final String endedBy;
        public final short[] pcm;
        Event(int id, double onset, double lastLoud, double clipStart, double clipEnd, double threshold, double peak, String reason, short[] pcm) {
            this.id=id; this.onsetSeconds=onset; this.lastLoudSeconds=lastLoud; this.clipStartSeconds=clipStart;
            this.clipEndSeconds=clipEnd; this.thresholdDbfs=threshold; this.peak=peak; this.endedBy=reason; this.pcm=pcm;
        }
    }

    public static final class Tombstone {
        public final int id;
        public final double onsetSeconds;
        public Tombstone(int id, double onset) { this.id=id; this.onsetSeconds=onset; }
    }

    public static final class Marker {
        public final double atSeconds;
        public final String note;
        Marker(double at, String note) { this.atSeconds=at; this.note=note; }
    }

    public static final class Result {
        public final Event event;
        public final Tombstone tombstone;
        public final boolean storageLimit;
        Result(Event event, Tombstone tombstone, boolean limit) { this.event=event; this.tombstone=tombstone; this.storageLimit=limit; }
        static Result empty() { return new Result(null, null, false); }
    }
}
