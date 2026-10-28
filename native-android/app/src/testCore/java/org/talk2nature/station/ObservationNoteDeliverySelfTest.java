package org.talk2nature.station;

public final class ObservationNoteDeliverySelfTest {
    public static void main(String[] args) {
        check(ObservationNoteDelivery.shouldClearSubmittedText(true,"movement"," movement "),
                "clear only the exact submitted note after the service confirms persistence");
        check(!ObservationNoteDelivery.shouldClearSubmittedText(false,"movement","movement"),
                "keep the note when the service did not confirm persistence");
        check(!ObservationNoteDelivery.shouldClearSubmittedText(true,"movement","new note"),
                "keep text typed while the earlier note was being saved");
        check(!ObservationNoteDelivery.shouldClearSubmittedText(true,null,"movement"),
                "never clear when the submitted value is missing");
        System.out.println("Observation-note delivery checks passed: confirmation and draft retention.");
    }

    private static void check(boolean condition,String message) {
        if (!condition) throw new AssertionError(message);
    }
}
