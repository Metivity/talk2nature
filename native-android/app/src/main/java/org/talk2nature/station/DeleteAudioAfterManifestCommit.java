package org.talk2nature.station;

import java.io.File;
import java.io.IOException;

/** Persists the user's removal decision before trying to remove encrypted audio. */
public final class DeleteAudioAfterManifestCommit {
    @FunctionalInterface
    public interface ManifestCommit {
        void commit() throws Exception;
    }

    public static final class CleanupPendingException extends IOException {
        public CleanupPendingException() {
            super("The clip was removed from the session, but encrypted local cleanup is still pending.");
        }
    }

    private DeleteAudioAfterManifestCommit() {}

    public static void run(File audioFile, ManifestCommit commit) throws Exception {
        commit.commit();
        if (audioFile.exists() && !audioFile.delete()) throw new CleanupPendingException();
    }
}
