package org.talk2nature.station;

import android.app.Notification;
import android.app.NotificationChannel;
import android.app.NotificationManager;
import android.app.PendingIntent;
import android.app.Service;
import android.content.Intent;
import android.content.pm.ServiceInfo;
import android.media.AudioManager;
import android.media.AudioRecord;
import android.media.MediaRecorder;
import android.os.Build;
import android.os.Bundle;
import android.os.IBinder;
import android.os.ResultReceiver;

import org.talk2nature.station.engine.CaptureEngine;
import org.talk2nature.station.engine.CaptureDeadline;

import java.time.Instant;

/** User-started foreground microphone capture. It never uploads, plays to, or identifies animals. */
public final class CaptureService extends Service {
    public static final String ACTION_START = "org.talk2nature.station.START";
    public static final String ACTION_STOP = "org.talk2nature.station.STOP";
    public static final String ACTION_NOTE = "org.talk2nature.station.NOTE";
    public static final String EXTRA_ALIAS = "station_alias";
    public static final String EXTRA_GROUP = "animal_group";
    public static final String EXTRA_SPECIES = "animal_species";
    public static final String EXTRA_SECONDS = "max_seconds";
    public static final String EXTRA_NOTE_RESULT = "note_result";
    public static final int NOTE_SAVED = 1;
    public static final int NOTE_NOT_SAVED = 0;
    private static final String CHANNEL_ID = "nature_station_recording_quiet_v1";
    private static final int NOTIFICATION_ID = 4612;
    private static volatile boolean capturing;
    private volatile boolean stopRequested;
    private volatile String requestedStopReason = "user_stop";
    private volatile AudioRecord recorder;
    private volatile CaptureEngine engine;
    private volatile SessionStore store;
    private Thread captureThread;
    private int maxSeconds;

    public static boolean isCapturing() { return capturing; }

    @Override public void onCreate() {
        super.onCreate();
        NotificationManager manager = getSystemService(NotificationManager.class);
        NotificationChannel channel = new NotificationChannel(CHANNEL_ID, "Nature Station", NotificationManager.IMPORTANCE_LOW);
        channel.setDescription("Silent recording status and Stop control.");
        channel.setSound(null, null);
        channel.enableVibration(false);
        channel.enableLights(false);
        channel.setShowBadge(false);
        manager.createNotificationChannel(channel);
    }

    @Override public int onStartCommand(Intent intent, int flags, int startId) {
        String action = intent == null ? null : intent.getAction();
        if (ACTION_STOP.equals(action)) {
            requestStop("user_stop");
            return START_NOT_STICKY;
        }
        if (ACTION_NOTE.equals(action)) {
            ResultReceiver receiver = noteResultReceiver(intent);
            boolean saved;
            try {
                addNote(intent.getStringExtra("note"));
                saved = true;
            } catch (Exception ignored) { saved = false; }
            if (receiver != null) receiver.send(saved ? NOTE_SAVED : NOTE_NOT_SAVED, Bundle.EMPTY);
            return START_NOT_STICKY;
        }
        if (!ACTION_START.equals(action) || capturing) return START_NOT_STICKY;
        try {
            maxSeconds = Math.max(3600, Math.min(28800, intent.getIntExtra(EXTRA_SECONDS, 3600)));
            startForegroundWithStopAction();
            stopRequested = false;
            requestedStopReason = "user_stop";
            capturing = true;
            captureThread = new Thread(() -> capture(intent), "talk2nature-audio");
            captureThread.start();
        } catch (Exception error) {
            capturing = false;
            stopForeground(STOP_FOREGROUND_REMOVE);
            stopSelf(startId);
        }
        return START_NOT_STICKY;
    }

    private void capture(Intent start) {
        AudioRecord audio = null;
        String reason = "recording_failure";
        long lastProgressWrite = 0;
        try {
            int source = unprocessedSupported() ? MediaRecorder.AudioSource.UNPROCESSED : MediaRecorder.AudioSource.MIC;
            audio = createRecorder(source);
            recorder = audio;
            if (audio == null) throw new IllegalStateException("This device did not provide a supported mono microphone input.");
            int sampleRate = audio.getSampleRate();
            store = new SessionStore(this);
            store.begin(start.getStringExtra(EXTRA_ALIAS), start.getStringExtra(EXTRA_GROUP),
                    start.getStringExtra(EXTRA_SPECIES), sampleRate,
                    source == MediaRecorder.AudioSource.UNPROCESSED ? "unprocessed requested" : "device microphone",
                    maxSeconds, Instant.now().toString(), "microphone");
            engine = new CaptureEngine(sampleRate);
            audio.startRecording();
            if (audio.getRecordingState() != AudioRecord.RECORDSTATE_RECORDING) throw new IllegalStateException("The microphone did not start.");
            capturing = true;
            CaptureDeadline deadline = new CaptureDeadline(android.os.SystemClock.elapsedRealtime(), maxSeconds * 1000L);
            int frameSamples = Math.max(1, sampleRate / 10);
            short[] buffer = new short[Math.max(frameSamples, AudioRecord.getMinBufferSize(sampleRate,
                    android.media.AudioFormat.CHANNEL_IN_MONO, android.media.AudioFormat.ENCODING_PCM_16BIT) / 2)];
            while (!stopRequested) {
                long checkAt = android.os.SystemClock.elapsedRealtime();
                long wallRemainingMillis = deadline.remainingMillis(checkAt);
                double remaining = maxSeconds - engine.elapsedSeconds();
                if (wallRemainingMillis == 0 || remaining <= 0.0001) { reason = "time_limit"; break; }
                int requestedByAudio = (int)Math.min(frameSamples, Math.max(1, Math.ceil(remaining * sampleRate)));
                int requested = deadline.limitSamples(checkAt, sampleRate, requestedByAudio);
                if (requested == 0) { reason = "time_limit"; break; }
                int count = audio.read(buffer, 0, requested, AudioRecord.READ_NON_BLOCKING);
                if (count > 0) {
                    CaptureEngine.Result result = engine.accept(buffer, count);
                    persist(result);
                    if (result.storageLimit) { reason = "storage_limit"; break; }
                    if (deadline.isExpired(android.os.SystemClock.elapsedRealtime())
                            || engine.elapsedSeconds() >= maxSeconds) { reason = "time_limit"; break; }
                    long now = android.os.SystemClock.elapsedRealtime();
                    if (now - lastProgressWrite >= 30000) {
                        store.updateProgress(engine.elapsedSeconds(), engine.thresholdDbfs(), engine.nearFullScaleFraction());
                        lastProgressWrite = now;
                    }
                } else if (count == 0 && !stopRequested) {
                    long waitMillis = deadline.remainingMillis(android.os.SystemClock.elapsedRealtime());
                    if (waitMillis == 0) { reason = "time_limit"; break; }
                    try {
                        Thread.sleep(Math.min(50L, waitMillis));
                    } catch (InterruptedException interrupted) {
                        Thread.currentThread().interrupt();
                        reason = stopRequested ? requestedStopReason : "audio_interruption";
                        break;
                    }
                } else if (count < 0 && !stopRequested) {
                    reason = count == AudioRecord.ERROR_DEAD_OBJECT ? "audio_interruption" : "recording_failure";
                    break;
                }
            }
            if (stopRequested) reason = requestedStopReason;
        } catch (SecurityException revoked) {
            reason = stopRequested ? requestedStopReason : "permission_revoked";
        } catch (Exception interrupted) {
            reason = stopRequested ? requestedStopReason : "audio_interruption";
        } finally {
            if (audio != null) {
                try { if (audio.getRecordingState() == AudioRecord.RECORDSTATE_RECORDING) audio.stop(); } catch (Exception ignored) {}
                audio.release();
            }
            recorder = null;
            try {
                if (store != null && engine != null) {
                    if (!engine.isStopped()) persist(engine.stop(reason));
                    String actualReason = engine.stopReason() == null ? reason : engine.stopReason();
                    store.finish(actualReason, engine.elapsedSeconds(), engine.thresholdDbfs(), engine.nearFullScaleFraction());
                }
            } catch (Exception ignored) {
                // If final persistence fails, keep the last authenticated checkpoint for recovery.
            }
            capturing = false;
            store = null;
            engine = null;
            stopForeground(STOP_FOREGROUND_REMOVE);
            stopSelf();
        }
    }

    private void persist(CaptureEngine.Result result) throws Exception {
        if (result.event != null) store.addEvent(result.event);
        if (result.tombstone != null) store.addTombstone(result.tombstone, "storage_limit");
        if (result.storageLimit) requestedStopReason = "storage_limit";
    }

    private AudioRecord createRecorder(int source) {
        int[] rates = {48000, 44100, 32000, 16000};
        for (int rate : rates) {
            int minimum = AudioRecord.getMinBufferSize(rate, android.media.AudioFormat.CHANNEL_IN_MONO,
                    android.media.AudioFormat.ENCODING_PCM_16BIT);
            if (minimum <= 0) continue;
            try {
                AudioRecord candidate = new AudioRecord(source, rate, android.media.AudioFormat.CHANNEL_IN_MONO,
                        android.media.AudioFormat.ENCODING_PCM_16BIT, Math.max(minimum, rate / 5 * 2));
                if (candidate.getState() == AudioRecord.STATE_INITIALIZED) return candidate;
                candidate.release();
            } catch (IllegalArgumentException | SecurityException ignored) {}
        }
        return null;
    }

    private boolean unprocessedSupported() {
        try {
            AudioManager manager = getSystemService(AudioManager.class);
            return "true".equalsIgnoreCase(manager.getProperty(AudioManager.PROPERTY_SUPPORT_AUDIO_SOURCE_UNPROCESSED));
        } catch (Exception ignored) { return false; }
    }

    private void addNote(String note) throws Exception {
        CaptureEngine current = engine;
        SessionStore currentStore = store;
        if (!capturing || current == null || currentStore == null)
            throw new IllegalStateException("The observation session is no longer active.");
        currentStore.addMarker(current.marker(note));
    }

    @SuppressWarnings("deprecation")
    private ResultReceiver noteResultReceiver(Intent intent) {
        if (Build.VERSION.SDK_INT >= 33)
            return intent.getParcelableExtra(EXTRA_NOTE_RESULT, ResultReceiver.class);
        return intent.getParcelableExtra(EXTRA_NOTE_RESULT);
    }

    private void requestStop(String reason) {
        requestedStopReason = reason;
        stopRequested = true;
        AudioRecord current = recorder;
        if (current != null) {
            try { current.stop(); } catch (Exception ignored) {}
        }
        if (!capturing && (captureThread == null || !captureThread.isAlive())) {
            stopForeground(STOP_FOREGROUND_REMOVE);
            stopSelf();
        }
    }

    private void startForegroundWithStopAction() {
        PendingIntent stop = PendingIntent.getService(this, 4613,
                new Intent(this, CaptureService.class).setAction(ACTION_STOP),
                PendingIntent.FLAG_UPDATE_CURRENT | PendingIntent.FLAG_IMMUTABLE);
        Notification notification = new Notification.Builder(this, CHANNEL_ID)
                .setSmallIcon(android.R.drawable.ic_lock_silent_mode_off)
                .setContentTitle("Nature Station is listening")
                .setContentText("Local only · stop any time · no animal playback")
                .setCategory(Notification.CATEGORY_SERVICE)
                .setOngoing(true)
                .setOnlyAlertOnce(true)
                .addAction(new Notification.Action.Builder(android.R.drawable.ic_media_pause, "Stop listening", stop).build())
                .build();
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.R)
            startForeground(NOTIFICATION_ID, notification, ServiceInfo.FOREGROUND_SERVICE_TYPE_MICROPHONE);
        else startForeground(NOTIFICATION_ID, notification);
    }

    @Override public void onTaskRemoved(Intent rootIntent) {
        // The visible foreground notification remains the stop/review route while the screen is away.
        super.onTaskRemoved(rootIntent);
    }

    @Override public void onDestroy() {
        if (capturing) requestStop("service_destroyed");
        super.onDestroy();
    }

    @Override public IBinder onBind(Intent intent) { return null; }
}
