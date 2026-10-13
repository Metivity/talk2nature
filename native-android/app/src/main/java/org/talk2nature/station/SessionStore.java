package org.talk2nature.station;

import android.content.Context;
import android.security.keystore.KeyGenParameterSpec;
import android.security.keystore.KeyProperties;
import android.util.AtomicFile;

import org.json.JSONArray;
import org.json.JSONObject;

import org.talk2nature.station.engine.CaptureEngine;

import java.io.ByteArrayOutputStream;
import java.io.File;
import java.io.FileOutputStream;
import java.io.InputStream;
import java.nio.charset.StandardCharsets;
import java.security.KeyStore;
import java.security.MessageDigest;
import java.util.Locale;
import java.util.UUID;

import javax.crypto.Cipher;
import javax.crypto.KeyGenerator;
import javax.crypto.SecretKey;
import javax.crypto.spec.GCMParameterSpec;

/** One encrypted, bounded, local session. It has no upload or shared-storage path. */
public final class SessionStore {
    private static final String KEY_ALIAS = "talk2nature-station-local-v1";
    private static final String SESSION_FILE = "session.json.enc";
    private static final int GCM_IV_BYTES = 12;
    private static final int GCM_TAG_BITS = 128;
    private final File directory;
    private final SecretKey key;

    public SessionStore(Context context) throws Exception {
        directory = new File(context.getFilesDir(), "station-v1");
        if (!directory.exists() && !directory.mkdirs()) throw new IllegalStateException("Could not prepare private station storage.");
        key = loadOrCreateKey();
    }

    public synchronized JSONObject read() throws Exception {
        File file = new File(directory, SESSION_FILE);
        if (!file.exists()) return null;
        byte[] bytes = decrypt(readFile(file, 512 * 1024), "session");
        return new JSONObject(new String(bytes, StandardCharsets.UTF_8));
    }

    public synchronized JSONObject begin(String alias, String group, String species, int sampleRate, String inputSource,
                                         int maxSessionSeconds, String startedAtUtc, String origin) throws Exception {
        if (read() != null) throw new IllegalStateException("Export or delete the saved session before starting another.");
        if (!"microphone".equals(origin) && !"synthetic".equals(origin)) throw new IllegalArgumentException("Unsupported recording origin.");
        JSONObject context = new JSONObject().put("group", group).put("species", species).put("basis", "observer-declared");
        JSONObject detector = new JSONObject().put("type", "energy_threshold").put("calibration_seconds", 3)
                .put("margin_db", 12).put("threshold_dbfs", JSONObject.NULL).put("pre_roll_seconds", 1)
                .put("max_clip_seconds_approx", 6).put("max_session_seconds", maxSessionSeconds);
        JSONObject settings = new JSONObject().put("sampleRate", sampleRate).put("channelCount", 1)
                .put("source", inputSource).put("processing", "device processing not reported");
        JSONArray limitations = new JSONArray()
                .put("A simple energy threshold selects some louder sounds; quiet periods are not retained.")
                .put("A sound after a note is not evidence of a reply; undetected sound is not silence.")
                .put("There is no species, speech, behavior, or meaning model in this app.")
                .put("Ordinary phone microphones are not verified for ultrasonic, underwater, or vibration signals.")
                .put("The clock is not synchronized; microphone processing and frequency response are not calibrated.")
                .put("No permission to share, research admission, or training rights are established by this export.")
                .put("The local working copy is encrypted; this exported ZIP is not encrypted.");
        JSONObject record = new JSONObject()
                .put("schema", "talk2nature.station.v2")
                .put("animal_context", context)
                .put("session_id", UUID.randomUUID().toString().toLowerCase(Locale.ROOT))
                .put("started_at_utc", startedAtUtc)
                .put("clock", "device wall clock; event offsets use processed audio samples; not synchronized")
                .put("tool_version", "android-0.1.0")
                .put("station_alias", alias.trim())
                .put("origin", origin)
                .put("sample_rate", sampleRate)
                .put("duration_seconds", 0)
                .put("status", "running")
                .put("stop_reason", JSONObject.NULL)
                .put("detector", detector)
                .put("audio_settings", settings)
                .put("near_full_scale_fraction", 0)
                .put("markers", new JSONArray())
                .put("events", new JSONArray())
                .put("discarded_events", new JSONArray())
                .put("limitations", limitations);
        writeRecord(record);
        return record;
    }

    public synchronized void updateProgress(double seconds, double thresholdDbfs, double clippedFraction) throws Exception {
        JSONObject record = requiredRecord();
        record.put("duration_seconds", round(seconds));
        record.put("near_full_scale_fraction", Math.max(0, Math.min(1, clippedFraction)));
        record.getJSONObject("detector").put("threshold_dbfs", Double.isFinite(thresholdDbfs) ? round(thresholdDbfs) : JSONObject.NULL);
        writeRecord(record);
    }

    public synchronized void addEvent(CaptureEngine.Event event) throws Exception {
        JSONObject record = requiredRecord();
        if (!"running".equals(record.optString("status"))) throw new IllegalStateException("The station session has stopped.");
        byte[] wav = wavBytes(event.pcm, record.getInt("sample_rate"));
        JSONArray events = record.getJSONArray("events");
        JSONArray discarded = record.getJSONArray("discarded_events");
        if (events.length() >= CaptureEngine.MAX_EVENTS || plaintextAudioBytes(record) + wav.length > CaptureEngine.MAX_AUDIO_BYTES) {
            addTombstone(record, new CaptureEngine.Tombstone(event.id, event.onsetSeconds), "storage_limit");
            writeRecord(record);
            return;
        }
        String filename = "talk2nature-" + record.getString("session_id") + "-event-" + event.id + ".wav";
        JSONObject entry = new JSONObject()
                .put("id", event.id)
                .put("onset_seconds", event.onsetSeconds)
                .put("last_loud_seconds", event.lastLoudSeconds)
                .put("clip_start_seconds", event.clipStartSeconds)
                .put("clip_end_seconds", event.clipEndSeconds)
                .put("samples", event.pcm.length)
                .put("threshold_dbfs", event.thresholdDbfs)
                .put("peak", event.peak)
                .put("ended_by", event.endedBy)
                .put("source_label", "unreviewed")
                .put("notes", "")
                .put("audio_filename", filename)
                .put("audio_sha256", sha256(wav));
        File audioFile = eventFile(event.id);
        writeEncrypted(audioFile, wav, "event:" + event.id);
        events.put(entry);
        record.put("duration_seconds", Math.max(record.getDouble("duration_seconds"), event.clipEndSeconds));
        record.getJSONObject("detector").put("threshold_dbfs", event.thresholdDbfs);
        try {
            writeRecord(record);
        } catch (Exception failure) {
            audioFile.delete();
            throw failure;
        }
    }

    public synchronized void addTombstone(CaptureEngine.Tombstone tombstone, String reason) throws Exception {
        JSONObject record = requiredRecord();
        addTombstone(record, tombstone, reason);
        writeRecord(record);
    }

    private void addTombstone(JSONObject record, CaptureEngine.Tombstone tombstone, String reason) throws Exception {
        record.getJSONArray("discarded_events").put(new JSONObject()
                .put("id", tombstone.id).put("onset_seconds", tombstone.onsetSeconds)
                .put("discarded", true).put("reason", reason));
    }

    public synchronized void addMarker(CaptureEngine.Marker marker) throws Exception {
        JSONObject record = requiredRecord();
        JSONArray markers = record.getJSONArray("markers");
        if (markers.length() >= 100) throw new IllegalStateException("This session already has 100 observation notes.");
        markers.put(new JSONObject().put("id", markers.length() + 1).put("at_seconds", marker.atSeconds)
                .put("kind", "observation").put("note", marker.note).put("provenance", "user-entered"));
        record.put("duration_seconds", Math.max(record.getDouble("duration_seconds"), marker.atSeconds));
        writeRecord(record);
    }

    public synchronized void deleteEvent(int id) throws Exception {
        JSONObject record = requiredRecord();
        JSONArray events = record.getJSONArray("events"), kept = new JSONArray();
        JSONObject removed = null;
        for (int i=0;i<events.length();i++) {
            JSONObject event = events.getJSONObject(i);
            if (event.getInt("id") == id) removed = event; else kept.put(event);
        }
        if (removed == null) return;
        record.put("events", kept);
        record.getJSONArray("discarded_events").put(new JSONObject().put("id", id)
                .put("onset_seconds", removed.getDouble("onset_seconds")).put("discarded", true));
        eventFile(id).delete();
        writeRecord(record);
    }

    public synchronized byte[] readEventWav(int id) throws Exception {
        File file = eventFile(id);
        if (!file.exists()) throw new IllegalStateException("That saved clip is no longer available.");
        return decrypt(readFile(file, CaptureEngine.MAX_AUDIO_BYTES + 1024), "event:" + id);
    }

    public synchronized void finish(String reason, double seconds, double thresholdDbfs, double clippedFraction) throws Exception {
        JSONObject record = requiredRecord();
        record.put("duration_seconds", round(seconds));
        record.put("near_full_scale_fraction", Math.max(0, Math.min(1, clippedFraction)));
        record.put("status", "stopped");
        record.put("stop_reason", reason);
        record.getJSONObject("detector").put("threshold_dbfs", Double.isFinite(thresholdDbfs) ? round(thresholdDbfs) : JSONObject.NULL);
        writeRecord(record);
    }

    public synchronized void recoverInterrupted() throws Exception {
        JSONObject record = read();
        if (record != null && "running".equals(record.optString("status"))) {
            record.put("status", "stopped").put("stop_reason", "service_interrupted");
            writeRecord(record);
        }
    }

    public synchronized void clear() throws Exception {
        File[] files = directory.listFiles();
        if (files != null) for (File file : files) if (!file.delete()) throw new IllegalStateException("Could not remove the local session.");
    }

    private JSONObject requiredRecord() throws Exception {
        JSONObject record = read();
        if (record == null) throw new IllegalStateException("No saved station session exists.");
        return record;
    }

    private void writeRecord(JSONObject record) throws Exception {
        writeEncrypted(new File(directory, SESSION_FILE), (record.toString(2) + "\n").getBytes(StandardCharsets.UTF_8), "session");
    }

    private void writeEncrypted(File file, byte[] plaintext, String purpose) throws Exception {
        byte[] packed = encrypt(plaintext, purpose);
        AtomicFile atomic = new AtomicFile(file);
        FileOutputStream stream = null;
        try {
            stream = atomic.startWrite();
            stream.write(packed);
            atomic.finishWrite(stream);
        } catch (Exception failure) {
            if (stream != null) atomic.failWrite(stream);
            throw failure;
        }
    }

    private byte[] encrypt(byte[] plaintext, String purpose) throws Exception {
        Cipher cipher = Cipher.getInstance("AES/GCM/NoPadding");
        cipher.init(Cipher.ENCRYPT_MODE, key);
        cipher.updateAAD(purpose.getBytes(StandardCharsets.UTF_8));
        byte[] iv = cipher.getIV(), encrypted = cipher.doFinal(plaintext);
        ByteArrayOutputStream output = new ByteArrayOutputStream(iv.length + encrypted.length);
        output.write(iv); output.write(encrypted);
        return output.toByteArray();
    }

    private byte[] decrypt(byte[] packed, String purpose) throws Exception {
        if (packed.length < GCM_IV_BYTES + 16) throw new IllegalStateException("Encrypted station data is incomplete.");
        byte[] iv = new byte[GCM_IV_BYTES], ciphertext = new byte[packed.length - GCM_IV_BYTES];
        System.arraycopy(packed, 0, iv, 0, iv.length);
        System.arraycopy(packed, iv.length, ciphertext, 0, ciphertext.length);
        Cipher cipher = Cipher.getInstance("AES/GCM/NoPadding");
        cipher.init(Cipher.DECRYPT_MODE, key, new GCMParameterSpec(GCM_TAG_BITS, iv));
        cipher.updateAAD(purpose.getBytes(StandardCharsets.UTF_8));
        return cipher.doFinal(ciphertext);
    }

    private SecretKey loadOrCreateKey() throws Exception {
        KeyStore store = KeyStore.getInstance("AndroidKeyStore");
        store.load(null);
        if (store.containsAlias(KEY_ALIAS)) return ((KeyStore.SecretKeyEntry) store.getEntry(KEY_ALIAS, null)).getSecretKey();
        KeyGenerator generator = KeyGenerator.getInstance(KeyProperties.KEY_ALGORITHM_AES, "AndroidKeyStore");
        generator.init(new KeyGenParameterSpec.Builder(KEY_ALIAS, KeyProperties.PURPOSE_ENCRYPT | KeyProperties.PURPOSE_DECRYPT)
                .setBlockModes(KeyProperties.BLOCK_MODE_GCM).setEncryptionPaddings(KeyProperties.ENCRYPTION_PADDING_NONE)
                .setKeySize(256).setRandomizedEncryptionRequired(true).build());
        return generator.generateKey();
    }

    private File eventFile(int id) { return new File(directory, "event-" + id + ".wav.enc"); }

    private long plaintextAudioBytes(JSONObject record) throws Exception {
        long bytes=0; JSONArray events=record.getJSONArray("events");
        for (int i=0;i<events.length();i++) bytes += events.getJSONObject(i).getLong("samples") * 2 + 44;
        return bytes;
    }

    private static byte[] readFile(File file, int maximum) throws Exception {
        AtomicFile atomic = new AtomicFile(file);
        try (InputStream input = atomic.openRead(); ByteArrayOutputStream output = new ByteArrayOutputStream()) {
            byte[] buffer = new byte[8192]; int count; int total=0;
            while ((count=input.read(buffer))!=-1) {
                total+=count;
                if (total>maximum) throw new IllegalStateException("Local station data is outside its size limit.");
                output.write(buffer,0,count);
            }
            if(total<1)throw new IllegalStateException("Local station data is empty.");
            return output.toByteArray();
        }
    }

    public static byte[] wavBytes(short[] pcm, int sampleRate) {
        byte[] out = new byte[44 + pcm.length * 2];
        putTag(out,0,"RIFF"); putInt(out,4,out.length-8); putTag(out,8,"WAVE"); putTag(out,12,"fmt "); putInt(out,16,16);
        putShort(out,20,1); putShort(out,22,1); putInt(out,24,sampleRate); putInt(out,28,sampleRate*2);
        putShort(out,32,2); putShort(out,34,16); putTag(out,36,"data"); putInt(out,40,pcm.length*2);
        for(int i=0;i<pcm.length;i++) putShort(out,44+i*2,pcm[i]);
        return out;
    }

    private static void putTag(byte[] out,int at,String text){for(int i=0;i<text.length();i++)out[at+i]=(byte)text.charAt(i);}
    private static void putShort(byte[] out,int at,int value){out[at]=(byte)value;out[at+1]=(byte)(value>>>8);}
    private static void putInt(byte[] out,int at,int value){out[at]=(byte)value;out[at+1]=(byte)(value>>>8);out[at+2]=(byte)(value>>>16);out[at+3]=(byte)(value>>>24);}
    private static String sha256(byte[] bytes) throws Exception {
        byte[] hash=MessageDigest.getInstance("SHA-256").digest(bytes); StringBuilder hex=new StringBuilder(hash.length*2);
        for(byte b:hash)hex.append(String.format(Locale.ROOT,"%02x",b&0xff)); return hex.toString();
    }
    private static double round(double value){return Math.round(value*10000.0)/10000.0;}
}
