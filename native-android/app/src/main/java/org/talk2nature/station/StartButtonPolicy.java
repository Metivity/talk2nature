package org.talk2nature.station;

/** Fail-closed visibility policy for the native microphone-start control. */
public final class StartButtonPolicy {
    private StartButtonPolicy() {}

    public static boolean canStart(boolean consentChecked, boolean sessionReadable, boolean sessionExists,
                                    boolean captureActive, boolean permissionPending) {
        return consentChecked && sessionReadable && !sessionExists && !captureActive && !permissionPending;
    }
}
