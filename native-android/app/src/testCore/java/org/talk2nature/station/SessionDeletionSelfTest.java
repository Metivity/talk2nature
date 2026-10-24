package org.talk2nature.station;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.concurrent.atomic.AtomicBoolean;

/** Failure-path checks for the manifest-first local clip removal contract. */
public final class SessionDeletionSelfTest {
    public static void main(String[] args) throws Exception {
        metadataFailurePreservesEncryptedAudio();
        committedRemovalDeletesAudio();
        failedCleanupIsReportedAfterRemovalCommits();
        System.out.println("Session deletion checks passed: manifest-first ordering and cleanup failure reporting.");
    }

    private static void metadataFailurePreservesEncryptedAudio() throws Exception {
        Path directory = Files.createTempDirectory("talk2nature-delete-metadata-failure-");
        Path audio = directory.resolve("event.enc");
        Files.write(audio, new byte[]{1, 2, 3});
        boolean failed = false;
        try {
            DeleteAudioAfterManifestCommit.run(audio.toFile(), () -> { throw new IOException("simulated manifest failure"); });
        } catch (IOException expected) {
            failed = true;
        }
        check(failed, "a failed manifest commit must surface to the caller");
        check(Files.exists(audio), "encrypted audio must remain if the manifest commit fails");
        Files.deleteIfExists(audio);
        Files.deleteIfExists(directory);
    }

    private static void committedRemovalDeletesAudio() throws Exception {
        Path directory = Files.createTempDirectory("talk2nature-delete-success-");
        Path audio = directory.resolve("event.enc");
        Files.write(audio, new byte[]{4, 5, 6});
        AtomicBoolean committed = new AtomicBoolean();
        DeleteAudioAfterManifestCommit.run(audio.toFile(), () -> committed.set(true));
        check(committed.get(), "the manifest must commit before media cleanup");
        check(!Files.exists(audio), "the encrypted clip file must be removed after commit");
        Files.deleteIfExists(directory);
    }

    private static void failedCleanupIsReportedAfterRemovalCommits() throws Exception {
        Path directory = Files.createTempDirectory("talk2nature-delete-cleanup-pending-");
        Path nonEmptyDirectory = Files.createDirectory(directory.resolve("not-a-file"));
        Path child = Files.write(nonEmptyDirectory.resolve("child"), new byte[]{7});
        AtomicBoolean committed = new AtomicBoolean();
        boolean cleanupPending = false;
        try {
            DeleteAudioAfterManifestCommit.run(nonEmptyDirectory.toFile(), () -> committed.set(true));
        } catch (DeleteAudioAfterManifestCommit.CleanupPendingException expected) {
            cleanupPending = true;
        }
        check(committed.get(), "metadata removal must commit before cleanup is attempted");
        check(cleanupPending, "failed media cleanup must be distinguished from metadata failure");
        check(Files.exists(child), "the failed cleanup fixture must remain for whole-session cleanup");
        Files.deleteIfExists(child);
        Files.deleteIfExists(nonEmptyDirectory);
        Files.deleteIfExists(directory);
    }

    private static void check(boolean condition, String message) {
        if (!condition) throw new AssertionError(message);
    }
}
