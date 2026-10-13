package org.talk2nature.station.engine;

/** A monotonic wall-clock bound for one foreground capture session. */
public final class CaptureDeadline {
    private static final long MAX_DURATION_MILLIS = 8L * 60 * 60 * 1000;

    private final long startedAtElapsedMillis;
    private final long durationMillis;

    public CaptureDeadline(long startedAtElapsedMillis, long durationMillis) {
        if (startedAtElapsedMillis < 0 || durationMillis < 1 || durationMillis > MAX_DURATION_MILLIS)
            throw new IllegalArgumentException("Capture duration must be between 1 ms and 8 hours.");
        this.startedAtElapsedMillis = startedAtElapsedMillis;
        this.durationMillis = durationMillis;
    }

    public long remainingMillis(long nowElapsedMillis) {
        long elapsed = nowElapsedMillis <= startedAtElapsedMillis ? 0 : nowElapsedMillis - startedAtElapsedMillis;
        return elapsed >= durationMillis ? 0 : durationMillis - elapsed;
    }

    public boolean isExpired(long nowElapsedMillis) {
        return remainingMillis(nowElapsedMillis) == 0;
    }

    /** Limits the next read to audio that could fit before the monotonic deadline. */
    public int limitSamples(long nowElapsedMillis, int sampleRate, int maximumSamples) {
        if (sampleRate < 1 || maximumSamples < 1)
            throw new IllegalArgumentException("Sample rate and frame bound must be positive.");
        long samplesRemaining = remainingMillis(nowElapsedMillis) * sampleRate / 1000L;
        return (int) Math.min(samplesRemaining, maximumSamples);
    }
}
