package org.talk2nature.station;

/** Tracks whether the stopped-session event list needs rebuilding. */
public final class EventListSnapshot {
    private String renderedKey;

    public boolean needsRender(String eventsJson, String markersJson) {
        return renderedKey == null || !renderedKey.equals(key(eventsJson, markersJson));
    }

    public void markRendered(String eventsJson, String markersJson) {
        renderedKey = key(eventsJson, markersJson);
    }

    /** Returns true when callers should clear views rendered from the previous session. */
    public boolean reset() {
        boolean hadRenderedState = renderedKey != null;
        renderedKey = null;
        return hadRenderedState;
    }

    private static String key(String eventsJson, String markersJson) {
        return normalize(eventsJson) + '\u0000' + normalize(markersJson);
    }

    private static String normalize(String json) {
        return json == null ? "[]" : json;
    }
}
