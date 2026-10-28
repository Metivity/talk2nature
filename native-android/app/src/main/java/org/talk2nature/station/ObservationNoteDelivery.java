package org.talk2nature.station;

/** Conservative input-clearing rule for an asynchronously persisted observation note. */
public final class ObservationNoteDelivery {
    private ObservationNoteDelivery() {}

    public static boolean shouldClearSubmittedText(boolean persisted, String submitted, String currentText) {
        return persisted && submitted != null && currentText != null && submitted.equals(currentText.trim());
    }
}
