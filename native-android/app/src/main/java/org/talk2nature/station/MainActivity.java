package org.talk2nature.station;

import android.Manifest;
import android.app.Activity;
import android.app.AlertDialog;
import android.content.Intent;
import android.content.pm.PackageManager;
import android.content.res.ColorStateList;
import android.graphics.Color;
import android.graphics.Typeface;
import android.graphics.drawable.GradientDrawable;
import android.media.AudioFormat;
import android.media.AudioManager;
import android.media.AudioTrack;
import android.net.Uri;
import android.os.Build;
import android.os.Bundle;
import android.os.Handler;
import android.os.Looper;
import android.provider.Settings;
import android.view.Gravity;
import android.view.View;
import android.view.ViewGroup;
import android.widget.ArrayAdapter;
import android.widget.Button;
import android.widget.CheckBox;
import android.widget.EditText;
import android.widget.LinearLayout;
import android.widget.ScrollView;
import android.widget.Spinner;
import android.widget.TextView;
import android.widget.Toast;

import org.json.JSONArray;
import org.json.JSONObject;
import org.talk2nature.station.engine.CaptureEngine;

import java.io.OutputStream;
import java.nio.ByteBuffer;
import java.nio.ByteOrder;
import java.security.MessageDigest;
import java.util.Locale;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.ArrayList;
import java.util.List;

/** Simple owner-free, local-first field tool. Google sign-in and cloud collection are absent. */
public final class MainActivity extends Activity {
    private static final int REQUEST_AUDIO_PERMISSION = 11;
    private static final int REQUEST_NOTIFICATION_PERMISSION = 12;
    private static final int CREATE_ZIP = 13;
    private static final int INK = Color.rgb(236, 245, 241);
    private static final int MUTED = Color.rgb(169, 190, 188);
    private static final int MINT = Color.rgb(114, 224, 180);
    private static final int PANEL = Color.rgb(24, 39, 47);
    private static final String[] GROUPS = {"unknown","parrot","other_bird","other_mammal","dog","cat","amphibian","reptile","fish","invertebrate","other_animal","multiple"};
    private static final String[] GROUP_LABELS = {"Not sure yet","Parrot","Other bird","Other mammal","Dog","Cat","Amphibian","Reptile","Fish","Insect or other invertebrate","Another animal","Several animals / mixed scene"};
    private static final int[] SCHEDULE_SECONDS = {3600,14400,28800};
    private final Handler handler = new Handler(Looper.getMainLooper());
    private final ExecutorService io = Executors.newSingleThreadExecutor();
    private SessionStore store;
    private Spinner groupSpinner, scheduleSpinner;
    private EditText speciesField, aliasField, noteField;
    private CheckBox consent;
    private Button startButton, stopButton, noteButton, exportButton, deleteButton, compareButton;
    private TextView sessionHeading, sessionDetail, observationLimit;
    private LinearLayout sessionPanel, eventList;
    private volatile AudioTrack playback;
    private boolean permissionRequestInFlight;
    private final EventListSnapshot eventListSnapshot = new EventListSnapshot();

    @Override protected void onCreate(Bundle state) {
        super.onCreate(state);
        getWindow().setStatusBarColor(Color.rgb(9,19,27));
        getWindow().setNavigationBarColor(Color.rgb(9,19,27));
        getWindow().setSoftInputMode(android.view.WindowManager.LayoutParams.SOFT_INPUT_ADJUST_RESIZE);
        try { store = new SessionStore(this); }
        catch (Exception error) { toast("Private encrypted storage could not be opened on this device."); finish(); return; }
        buildScreen();
    }

    @Override protected void onResume() {
        super.onResume();
        refreshSession();
        handler.post(refreshLoop);
    }

    @Override protected void onPause() {
        handler.removeCallbacks(refreshLoop);
        stopPlayback();
        super.onPause();
    }

    @Override protected void onDestroy() {
        io.shutdownNow();
        super.onDestroy();
    }

    private final Runnable refreshLoop = new Runnable() {
        @Override public void run() { refreshSession(); handler.postDelayed(this, 2000); }
    };

    private void buildScreen() {
        ScrollView scroll = new ScrollView(this);
        scroll.setFillViewport(true);
        scroll.setBackground(new GradientDrawable(GradientDrawable.Orientation.TOP_BOTTOM,
                new int[]{Color.rgb(11,28,35), Color.rgb(12,23,31), Color.rgb(9,18,27)}));
        LinearLayout page = new LinearLayout(this);
        page.setOrientation(LinearLayout.VERTICAL);
        page.setPadding(dp(20),dp(18),dp(20),dp(30));
        scroll.addView(page);

        TextView eyebrow = text("TALK2NATURE   /   FIELD COMPANION",12,MINT,true);
        eyebrow.setLetterSpacing(0.08f);
        page.addView(eyebrow,space(0,0,0,18));
        TextView title = text("A little field station\nfor a big question.",31,INK,true);
        page.addView(title,space(0,0,0,10));
        page.addView(text("Notice sounds and context. Let the evidence stay bigger than the guess.",16,MUTED,false),space(0,0,0,20));

        LinearLayout setup = card();
        page.addView(setup,space(0,0,0,14));
        setup.addView(text("01   Set up your observation",19,INK,true),space(0,0,0,6));
        setup.addView(text("Any animal is welcome. A label is what you observed, not an automatic identification.",14,MUTED,false),space(0,0,0,14));
        groupSpinner = spinner(GROUP_LABELS);
        setup.addView(labelFor("Who might be nearby?",groupSpinner));
        setup.addView(groupSpinner,space(0,5,0,8));
        speciesField = field("Species, if known (optional)");
        setup.addView(speciesField,space(0,2,0,8));
        aliasField = field("Station name"); aliasField.setText("field-station");
        setup.addView(aliasField,space(0,2,0,8));
        scheduleSpinner = spinner(new String[]{"Observe for 1 hour","Observe for 4 hours","Observe for 8 hours"});
        setup.addView(labelFor("Choose a stop time",scheduleSpinner));
        setup.addView(scheduleSpinner,space(0,5,0,10));
        observationLimit = text("The detector keeps up to 24 short sound highlights (24 MB max). Quiet audio is not saved, so this is not continuous or unbiased monitoring.",13,MUTED,false);
        setup.addView(observationLimit,space(0,2,0,10));
        setup.addView(text("A regular phone microphone is not a bat-ultrasound, underwater or vibration sensor. Frequency response and device processing are not calibrated.",13,MUTED,false),space(0,0,0,6));

        consent = new CheckBox(this);
        consent.setText("I can record here, nearby people know the microphone may be active, and I will observe without provoking or playing sounds to animals.");
        consent.setTextColor(INK); consent.setTextSize(14); consent.setButtonTintList(ColorStateList.valueOf(MINT));
        consent.setPadding(0,dp(8),0,dp(6));
        setup.addView(consent,space(0,4,0,6));
        startButton = button("Start listening",MINT,Color.rgb(8,37,31));
        setup.addView(startButton,space(0,4,0,0));
        startButton.setOnClickListener(v -> requestStart());

        sessionPanel = card();
        page.addView(sessionPanel,space(0,0,0,14));
        sessionPanel.addView(text("02   Your local session",19,INK,true),space(0,0,0,8));
        sessionHeading = text("Ready when you are",16,MINT,true);
        sessionPanel.addView(sessionHeading,space(0,0,0,4));
        sessionDetail = text("Nothing is recording. Nothing has been uploaded.",14,MUTED,false);
        sessionPanel.addView(sessionDetail,space(0,0,0,12));
        stopButton = button("Stop listening now",Color.rgb(255,137,124),Color.rgb(45,17,17));
        sessionPanel.addView(stopButton,space(0,0,0,8));
        stopButton.setOnClickListener(v -> sendServiceAction(CaptureService.ACTION_STOP));
        noteField = field("What did you notice? (optional)");
        sessionPanel.addView(noteField,space(0,0,0,7));
        noteButton = button("Add observation note",Color.rgb(101,185,157),Color.rgb(8,31,29));
        sessionPanel.addView(noteButton,space(0,0,0,10));
        noteButton.setOnClickListener(v -> addObservationNote());
        eventList = new LinearLayout(this); eventList.setOrientation(LinearLayout.VERTICAL);
        sessionPanel.addView(eventList,space(0,2,0,8));
        exportButton = button("Export unencrypted ZIP",Color.rgb(112,157,194),Color.rgb(10,24,37));
        sessionPanel.addView(exportButton,space(0,0,0,8));
        exportButton.setOnClickListener(v -> chooseExportDestination());
        compareButton = button("Open the local review tools",Color.rgb(51,75,83),INK);
        sessionPanel.addView(compareButton,space(0,0,0,8));
        compareButton.setOnClickListener(v -> startActivity(new Intent(Intent.ACTION_VIEW, Uri.parse("https://metivity.github.io/talk2nature/app/compare/"))));
        deleteButton = button("Delete this encrypted session",Color.rgb(67,47,48),Color.rgb(255,201,193));
        sessionPanel.addView(deleteButton,space(0,0,0,0));
        deleteButton.setOnClickListener(v -> confirmDelete());

        LinearLayout note = card();
        page.addView(note,space(0,0,0,14));
        note.addView(text("Built for careful listening",17,INK,true),space(0,0,0,6));
        note.addView(text("A pattern, a species guess, or a sound after a voice is not a translation. Keep people and wildlife safe; follow local recording rules. Your working copy stays encrypted on this phone. Export creates a regular, unencrypted ZIP that you choose where to save.",14,MUTED,false));
        scroll.setClipToPadding(false);
        setContentView(scroll);
        refreshSession();
    }

    private void requestStart() {
        if (!consent.isChecked()) { toast("Please check the recording and wildlife-care statement first."); return; }
        if (permissionRequestInFlight) return;
        try {
            JSONObject current = store.read();
            if (current != null) { toast("Export or delete the saved session before starting another."); return; }
        } catch (Exception error) { toast("Could not read encrypted session storage."); return; }
        requestNextPermission();
    }

    private void requestNextPermission() {
        if (Build.VERSION.SDK_INT >= 33 && checkSelfPermission(Manifest.permission.POST_NOTIFICATIONS) != PackageManager.PERMISSION_GRANTED) {
            permissionRequestInFlight=true;
            requestPermissions(new String[]{Manifest.permission.POST_NOTIFICATIONS},REQUEST_NOTIFICATION_PERMISSION);
            return;
        }
        if (checkSelfPermission(Manifest.permission.RECORD_AUDIO) != PackageManager.PERMISSION_GRANTED) {
            permissionRequestInFlight=true;
            requestPermissions(new String[]{Manifest.permission.RECORD_AUDIO},REQUEST_AUDIO_PERMISSION);
            return;
        }
        permissionRequestInFlight=false;
        startSession();
    }

    @Override public void onRequestPermissionsResult(int requestCode,String[] permissions,int[] results) {
        super.onRequestPermissionsResult(requestCode,permissions,results);
        permissionRequestInFlight=false;
        boolean granted=results.length>0 && results[0]==PackageManager.PERMISSION_GRANTED;
        if (requestCode==REQUEST_NOTIFICATION_PERMISSION) {
            if (granted) requestNextPermission();
            else explainNotificationPermissionDenied();
        } else if (requestCode==REQUEST_AUDIO_PERMISSION) {
            if (granted) startSession();
            else explainMicrophonePermissionDenied();
        }
    }

    private void explainMicrophonePermissionDenied() {
        new AlertDialog.Builder(this)
                .setTitle("Microphone access is off")
                .setMessage("Nothing started or was saved. To record later, allow Microphone in Talk2Nature Station's Android app settings. Choose Not now to return without recording.")
                .setNegativeButton("Not now", (dialog, which) -> {})
                .setPositiveButton("Open app settings", (dialog, which) -> openSettings())
                .show();
    }

    private void explainNotificationPermissionDenied() {
        new AlertDialog.Builder(this)
                .setTitle("Notifications are off")
                .setMessage("Nothing started or was saved. This Station requires an ongoing notification with a Stop control while it listens. To try later, allow notifications in Talk2Nature Station's Android app settings. Choose Not now to return without recording.")
                .setNegativeButton("Not now", (dialog, which) -> {})
                .setPositiveButton("Open app settings", (dialog, which) -> openSettings())
                .show();
    }

    private void startSession() {
        String alias=aliasField.getText().toString().trim(), species=speciesField.getText().toString().trim();
        if (alias.isEmpty() || alias.length()>80) { aliasField.setError("Use a station name of 1–80 characters."); return; }
        if (species.length()>80) { speciesField.setError("Use at most 80 characters."); return; }
        int index=groupSpinner.getSelectedItemPosition(), schedule=scheduleSpinner.getSelectedItemPosition();
        Intent intent=new Intent(this,CaptureService.class).setAction(CaptureService.ACTION_START)
                .putExtra(CaptureService.EXTRA_ALIAS,alias)
                .putExtra(CaptureService.EXTRA_GROUP,GROUPS[index])
                .putExtra(CaptureService.EXTRA_SPECIES,species)
                .putExtra(CaptureService.EXTRA_SECONDS,SCHEDULE_SECONDS[schedule]);
        try {
            startForegroundService(intent);
            toast("Station starting. Stop is also in the ongoing notification.");
            refreshSession();
        } catch (SecurityException error) { toast("Android did not allow microphone recording to start."); }
    }

    private void addObservationNote() {
        String note=noteField.getText().toString().trim();
        if (note.isEmpty() || note.length()>300) { noteField.setError("Add a short note of 1–300 characters."); return; }
        sendServiceAction(CaptureService.ACTION_NOTE,note);
        noteField.setText("");
        toast("Note added to the session timeline.");
    }

    private void sendServiceAction(String action) { sendServiceAction(action,null); }
    private void sendServiceAction(String action,String note) {
        Intent intent=new Intent(this,CaptureService.class).setAction(action);
        if(note!=null)intent.putExtra("note",note);
        try { startService(intent); } catch (Exception error) { toast("The station could not receive that action."); }
        handler.postDelayed(this::refreshSession,500);
    }

    private void refreshSession() {
        if (store==null || isFinishing()) return;
        try {
            JSONObject record=store.read();
            if (record==null) {
                sessionHeading.setText("Ready when you are");
                sessionDetail.setText("Nothing is recording. Nothing has been uploaded.");
                setSessionControls(false,false,false);
                if (eventListSnapshot.reset()) eventList.removeAllViews();
                return;
            }
            if ("running".equals(record.optString("status")) && !CaptureService.isCapturing()) {
                store.recoverInterrupted();
                record=store.read();
            }
            boolean active="running".equals(record.optString("status")) && CaptureService.isCapturing();
            double duration=record.optDouble("duration_seconds",0);
            JSONArray events=record.optJSONArray("events");
            int count=events==null?0:events.length();
            sessionHeading.setText(active?"LISTENING · Stop is always available":"Saved on this phone · not uploaded");
            sessionHeading.setTextColor(active?MINT:INK);
            String detail=String.format(Locale.ROOT,"%s · %d retained sound highlight%s · max %s\nThe detector does not interpret sounds.",
                    formatTime(duration),count,count==1?"":"s",formatTime(record.optJSONObject("detector").optInt("max_session_seconds",3600)));
            if(!active && "service_interrupted".equals(record.optString("stop_reason"))) detail+="\nThe service ended unexpectedly; the partial session is marked stopped.";
            sessionDetail.setText(detail);
            setSessionControls(active,!active,!active);
            if(!active) {
                JSONArray markers=record.optJSONArray("markers");
                String eventsJson=events==null?null:events.toString();
                String markersJson=markers==null?null:markers.toString();
                if(eventListSnapshot.needsRender(eventsJson,markersJson)) {
                    renderEvents(events,markers);
                    eventListSnapshot.markRendered(eventsJson,markersJson);
                }
            }
        } catch (Exception error) {
            sessionHeading.setText("Session needs attention");
            sessionDetail.setText("Encrypted session data could not be read. Keep the app data intact and export is unavailable until this is resolved.");
            setSessionControls(false,false,false);
        }
    }

    private void setSessionControls(boolean active,boolean stopped,boolean hasSession) {
        stopButton.setVisibility(active?View.VISIBLE:View.GONE);
        noteField.setVisibility(active?View.VISIBLE:View.GONE);
        noteButton.setVisibility(active?View.VISIBLE:View.GONE);
        exportButton.setVisibility(stopped && hasSession?View.VISIBLE:View.GONE);
        compareButton.setVisibility(stopped && hasSession?View.VISIBLE:View.GONE);
        deleteButton.setVisibility(hasSession?View.VISIBLE:View.GONE);
    }

    private void renderEvents(JSONArray events,JSONArray markers) throws Exception {
        eventList.removeAllViews();
        if(events==null || events.length()==0) {
            eventList.addView(text("No sound highlights were retained. This is not evidence that the scene was silent.",13,MUTED,false));
        } else {
            for(int i=0;i<events.length();i++) {
                JSONObject event=events.getJSONObject(i);
                LinearLayout row=new LinearLayout(this); row.setOrientation(LinearLayout.VERTICAL);
                row.setPadding(dp(13),dp(11),dp(13),dp(11)); row.setBackground(shape(Color.rgb(32,51,58),Color.rgb(55,81,84),16));
                LinearLayout.LayoutParams rp=space(0,0,0,8); eventList.addView(row,rp);
                String label=String.format(Locale.ROOT,"Moment %d · %s–%s",event.getInt("id"),formatTime(event.optDouble("clip_start_seconds")),formatTime(event.optDouble("clip_end_seconds")));
                row.addView(text(label,15,INK,true),space(0,0,0,3));
                row.addView(text("Unreviewed sound highlight · source is not identified",12,MUTED,false),space(0,0,0,7));
                LinearLayout actions=new LinearLayout(this); actions.setOrientation(LinearLayout.HORIZONTAL); row.addView(actions);
                Button play=button("Play clip",Color.rgb(101,185,157),Color.rgb(8,31,29));
                Button discard=button("Delete clip",Color.rgb(67,47,48),Color.rgb(255,201,193));
                LinearLayout.LayoutParams half=new LinearLayout.LayoutParams(0,dp(44),1); half.setMarginEnd(dp(7)); actions.addView(play,half);
                LinearLayout.LayoutParams half2=new LinearLayout.LayoutParams(0,dp(44),1); actions.addView(discard,half2);
                int id=event.getInt("id"); play.setOnClickListener(v -> playEvent(id));
                discard.setOnClickListener(v -> new AlertDialog.Builder(this).setTitle("Delete this clip?")
                        .setMessage("The encrypted audio will be deleted. A small tombstone will remain so the session does not imply this moment was silent.")
                        .setNegativeButton("Keep it",null).setPositiveButton("Delete clip",(d,w)->deleteEvent(id)).show());
            }
        }
        if(markers!=null && markers.length()>0) {
            eventList.addView(text("Your observation notes",14,INK,true),space(0,7,0,5));
            for(int i=0;i<markers.length();i++) {
                JSONObject marker=markers.getJSONObject(i);
                eventList.addView(text(formatTime(marker.optDouble("at_seconds"))+" · "+marker.optString("note"),13,MUTED,false),space(0,0,0,5));
            }
        }
    }

    private void deleteEvent(int id) {
        try { store.deleteEvent(id); toast("Clip deleted from encrypted local storage."); refreshSession(); }
        catch (Exception error) { toast("The clip could not be deleted."); }
    }

    private void playEvent(int id) {
        stopPlayback();
        io.execute(() -> {
            try {
                byte[] wav=store.readEventWav(id);
                int rate=ByteBuffer.wrap(wav,24,4).order(ByteOrder.LITTLE_ENDIAN).getInt();
                int count=(wav.length-44)/2; short[] samples=new short[count];
                ByteBuffer pcm=ByteBuffer.wrap(wav,44,wav.length-44).order(ByteOrder.LITTLE_ENDIAN);
                for(int i=0;i<count;i++)samples[i]=pcm.getShort();
                AudioTrack track=new AudioTrack(AudioManager.STREAM_MUSIC,rate,AudioFormat.CHANNEL_OUT_MONO,
                        AudioFormat.ENCODING_PCM_16BIT,Math.max(2,samples.length*2),AudioTrack.MODE_STATIC);
                if(track.getState()!=AudioTrack.STATE_INITIALIZED)throw new IllegalStateException("Audio output unavailable.");
                int written=track.write(samples,0,samples.length);
                if(written!=samples.length)throw new IllegalStateException("Could not load the full clip for playback.");
                playback=track; track.play();
                Thread.sleep(Math.max(250,(long)(samples.length*1000.0/rate)+150));
                if(playback==track) { playback=null; track.release(); }
            } catch(Exception error) {
                runOnUiThread(()->toast("Clip playback failed. The original export may still be available."));
            }
        });
        toast("Playing only the clip you selected.");
    }

    private void stopPlayback() {
        AudioTrack track=playback; playback=null;
        if(track!=null)try{track.pause();track.flush();track.stop();track.release();}catch(Exception ignored){}
    }

    private void confirmDelete() {
        new AlertDialog.Builder(this).setTitle("Delete this whole session?")
                .setMessage("This removes the encrypted journal and retained audio from this phone. There is no recycle bin. Export first if you want a copy; the exported ZIP is unencrypted.")
                .setNegativeButton("Cancel",null).setPositiveButton("Delete session",(d,w)->{
                    try{store.clear();toast("Local session deleted.");refreshSession();}catch(Exception error){toast("The session could not be deleted.");}
                }).show();
    }

    private void chooseExportDestination() {
        Intent intent=new Intent(Intent.ACTION_CREATE_DOCUMENT).setType("application/zip")
                .addCategory(Intent.CATEGORY_OPENABLE).putExtra(Intent.EXTRA_TITLE,"talk2nature-session.zip");
        startActivityForResult(intent,CREATE_ZIP);
    }

    @Override protected void onActivityResult(int requestCode,int resultCode,Intent data) {
        super.onActivityResult(requestCode,resultCode,data);
        if(requestCode==CREATE_ZIP && resultCode==RESULT_OK && data!=null && data.getData()!=null) exportTo(data.getData());
    }

    private void exportTo(Uri uri) {
        toast("Preparing your unencrypted local export…");
        io.execute(() -> {
            try(OutputStream output=getContentResolver().openOutputStream(uri,"w")) {
                if(output==null)throw new IllegalStateException("The selected file location could not be opened.");
                JSONObject record=store.read();
                if(record==null || !"stopped".equals(record.optString("status")))throw new IllegalStateException("Stop the session before exporting it.");
                JSONArray events=record.getJSONArray("events");
                if(events.length()>CaptureEngine.MAX_EVENTS)throw new IllegalStateException("This session exceeds the supported clip count.");
                List<SessionZip.Entry> files=new ArrayList<>();
                files.add(new SessionZip.Entry("talk2nature-"+record.getString("session_id")+".json",(record.toString(2)+"\n").getBytes(java.nio.charset.StandardCharsets.UTF_8)));
                for(int i=0;i<events.length();i++) {
                    JSONObject event=events.getJSONObject(i); int id=event.getInt("id"); byte[] wav=store.readEventWav(id);
                    if(!sha256(wav).equals(event.getString("audio_sha256")))throw new IllegalStateException("A clip failed its checksum. No export was written.");
                    files.add(new SessionZip.Entry(event.getString("audio_filename"),wav));
                }
                String readme="Talk2Nature Android Station session\n\nOpen this original ZIP in Talk2Nature > Compare to review the journal and its clips on this device.\nThe journal records a session scheduled for at most eight hours, a simple energy trigger and retained sound highlights only; quiet periods are not saved.\nA detected sound does not identify an animal or establish meaning, a reply, or causation. Observer notes are not verified labels.\nThe phone working copy is encrypted. This chosen export is an unencrypted ZIP; review it before sharing.\nNo files were uploaded. Research admission, consent to share and training rights are not established by this export.\n";
                files.add(new SessionZip.Entry("READ-ME.txt",readme.getBytes(java.nio.charset.StandardCharsets.UTF_8)));
                SessionZip.write(output,files);
                runOnUiThread(()->toast("Session exported. It remains encrypted on this phone until you delete it."));
            } catch(Exception error) {
                runOnUiThread(()->toast("Export failed: "+(error.getMessage()==null?"check the destination":error.getMessage())));
            }
        });
    }

    private static String sha256(byte[] bytes)throws Exception {
        byte[] hash=MessageDigest.getInstance("SHA-256").digest(bytes);StringBuilder result=new StringBuilder();for(byte b:hash)result.append(String.format(Locale.ROOT,"%02x",b&255));return result.toString();
    }

    private void openSettings() { startActivity(new Intent(Settings.ACTION_APPLICATION_DETAILS_SETTINGS,Uri.parse("package:"+getPackageName()))); }
    private void toast(String value) { Toast.makeText(this,value,Toast.LENGTH_LONG).show(); }
    private int dp(float value) { return (int)(value*getResources().getDisplayMetrics().density+0.5f); }
    private LinearLayout.LayoutParams space(int left,int top,int right,int bottom) {
        LinearLayout.LayoutParams params=new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT,ViewGroup.LayoutParams.WRAP_CONTENT);
        params.setMargins(dp(left),dp(top),dp(right),dp(bottom));return params;
    }
    private TextView text(String value,float size,int color,boolean bold) {
        TextView view=new TextView(this);view.setText(value);view.setTextSize(size);view.setTextColor(color);view.setGravity(Gravity.START);
        if(bold)view.setTypeface(Typeface.DEFAULT,Typeface.BOLD);view.setLineSpacing(dp(2),1.02f);return view;
    }
    private TextView label(String value) { TextView view=text(value,13,MUTED,true);view.setPadding(dp(1),dp(5),0,0);return view; }
    private TextView labelFor(String value,View target) { TextView view=label(value);view.setLabelFor(target.getId());return view; }
    private EditText field(String hint) {
        EditText input=new EditText(this);input.setId(View.generateViewId());input.setHint(hint);input.setHintTextColor(Color.rgb(137,160,161));input.setTextColor(INK);input.setTextSize(15);
        input.setSingleLine(true);input.setPadding(dp(13),dp(10),dp(13),dp(10));input.setBackground(shape(Color.rgb(13,27,34),Color.rgb(58,79,82),14));
        return input;
    }
    private Spinner spinner(String[] values) {
        Spinner view=new Spinner(this);view.setId(View.generateViewId());view.setAdapter(new ArrayAdapter<String>(this,android.R.layout.simple_spinner_item,values) {
            @Override public View getView(int position,View convert,ViewGroup parent){TextView item=(TextView)super.getView(position,convert,parent);item.setTextColor(INK);item.setTextSize(15);item.setPadding(dp(12),dp(5),dp(12),dp(5));return item;}
            @Override public View getDropDownView(int position,View convert,ViewGroup parent){TextView item=new TextView(MainActivity.this);item.setText(getItem(position));item.setTextColor(INK);item.setTextSize(15);item.setPadding(dp(16),dp(13),dp(16),dp(13));item.setBackgroundColor(Color.rgb(22,38,45));return item;}
        });
        view.setBackground(shape(Color.rgb(13,27,34),Color.rgb(58,79,82),14));view.setPadding(dp(5),dp(2),dp(8),dp(2));view.setDropDownVerticalOffset(dp(4));return view;
    }
    private Button button(String label,int background,int foreground) {
        Button view=new Button(this);view.setText(label);view.setTextColor(foreground);view.setTextSize(14);view.setAllCaps(false);view.setTypeface(Typeface.DEFAULT,Typeface.BOLD);
        view.setMinHeight(dp(48));view.setPadding(dp(12),dp(8),dp(12),dp(8));view.setBackground(shape(background,background,15));return view;
    }
    private LinearLayout card() {
        LinearLayout view=new LinearLayout(this);view.setOrientation(LinearLayout.VERTICAL);view.setPadding(dp(17),dp(17),dp(17),dp(17));
        view.setBackground(shape(PANEL,Color.rgb(45,67,72),22));return view;
    }
    private GradientDrawable shape(int fill,int stroke,int radius) {
        GradientDrawable drawable=new GradientDrawable();drawable.setColor(fill);drawable.setCornerRadius(dp(radius));drawable.setStroke(dp(1),stroke);return drawable;
    }
    private String formatTime(double seconds) {
        long total=Math.max(0,(long)seconds), hours=total/3600,minutes=(total%3600)/60,secs=total%60;
        return hours>0?String.format(Locale.ROOT,"%d:%02d h",hours,minutes):String.format(Locale.ROOT,"%d:%02d",minutes,secs);
    }
}
