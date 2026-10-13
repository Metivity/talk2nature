package org.talk2nature.station;

import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;

import org.talk2nature.station.engine.CaptureEngine;

import java.time.Instant;
import java.util.Arrays;

/** Debug-build-only repeatable session fixture; absent from the release manifest and sources. */
public final class DebugSessionSeedReceiver extends BroadcastReceiver {
    public static final String ACTION="org.talk2nature.station.DEBUG_SEED_SYNTHETIC_SESSION";
    @Override public void onReceive(Context context,Intent intent) {
        if(!ACTION.equals(intent.getAction()) || CaptureService.isCapturing())return;
        SessionStore store=null;boolean created=false;
        try {
            store=new SessionStore(context);
            store.begin("synthetic-emulator","other_bird","",16000,"synthetic test input",
                    3600,Instant.now().toString(),"synthetic");
            created=true;
            CaptureEngine engine=new CaptureEngine(16000);
            short[] quiet=new short[1600];
            for(int i=0;i<30;i++)engine.accept(quiet,quiet.length);
            for(int i=0;i<10;i++)engine.accept(quiet,quiet.length);
            short[] tone=new short[1600];Arrays.fill(tone,(short)6000);
            engine.accept(tone,tone.length);engine.accept(tone,tone.length);
            CaptureEngine.Result result=null;
            for(int i=0;i<5;i++)result=engine.accept(quiet,quiet.length);
            if(result==null || result.event==null)throw new IllegalStateException("Synthetic event did not close.");
            store.addEvent(result.event);
            store.addMarker(engine.marker("synthetic emulator workflow check"));
            store.finish("synthetic_test",engine.elapsedSeconds(),engine.thresholdDbfs(),engine.nearFullScaleFraction());
        } catch(Exception ignored) {
            if(created)try { store.recoverInterrupted(); } catch(Exception alsoIgnored) {}
        }
    }
}
