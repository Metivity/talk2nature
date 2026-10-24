package org.talk2nature.station;

/** Permission and session-state checks for the microphone-start control. */
public final class StartButtonPolicySelfTest {
    public static void main(String[] args) {
        check(!can(false,true,false,false,false), "an unchecked care/recording statement must disable Start");
        check(can(true,true,false,false,false), "a checked statement and empty readable store enables Start");
        check(!can(true,false,false,false,false), "unreadable session storage must disable Start");
        check(!can(true,true,true,false,false), "a saved session must be exported or deleted first");
        check(!can(true,true,false,true,false), "active capture must disable a second start");
        check(!can(true,true,false,false,true), "a pending permission prompt must disable repeated starts");
        System.out.println("Start-button checks passed: consent, storage, session, capture and permission states.");
    }

    private static boolean can(boolean consent, boolean readable, boolean exists, boolean active, boolean pending) {
        return StartButtonPolicy.canStart(consent,readable,exists,active,pending);
    }

    private static void check(boolean condition, String message) {
        if (!condition) throw new AssertionError(message);
    }
}
