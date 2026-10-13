package org.talk2nature.station.engine;

import org.talk2nature.station.SessionZip;

import java.io.ByteArrayOutputStream;
import java.nio.charset.StandardCharsets;
import java.util.Arrays;
public final class CaptureEngineSelfTest {
    private static final int RATE=16000;
    private static void check(boolean value,String message){if(!value)throw new AssertionError(message);}
    private static CaptureEngine.Result feed(CaptureEngine engine,int frames,short sample){
        CaptureEngine.Result last=null;
        for(int i=0;i<frames;i++){
            short[] frame=new short[RATE/10];
            if(sample!=0)java.util.Arrays.fill(frame,sample);
            last=engine.accept(frame,frame.length);
            if(last.storageLimit)return last;
            if(last.event!=null)return last;
        }
        return last;
    }
    private static void silence(CaptureEngine engine,int tenths){feed(engine,tenths,(short)0);}
    private static int u16(byte[] bytes,int at){return (bytes[at]&255)|((bytes[at+1]&255)<<8);}
    private static long u32(byte[] bytes,int at){return (u16(bytes,at)&0xffffL)|((u16(bytes,at+2)&0xffffL)<<16);}

    public static void main(String[] args){
        CaptureEngine engine=new CaptureEngine(RATE);
        silence(engine,30);
        check(Math.abs(engine.thresholdDbfs()+50)<0.01,"quiet calibration must use the lower clamp");
        silence(engine,10);
        CaptureEngine.Result event=feed(engine,2,(short)6000);
        check(event.event==null,"a loud signal must not become a clip until its tail is observed");
        event=feed(engine,5,(short)0);
        check(event.event!=null,"quiet hysteresis must close a retained event");
        check(event.event.id==1,"event ids start at one");
        check(event.event.onsetSeconds>=3.9 && event.event.onsetSeconds<=4.1,"onset uses processed audio time");
        check(event.event.clipStartSeconds<event.event.onsetSeconds,"the clip includes pre-roll");
        check(Math.abs(event.event.pcm.length/(double)RATE-(event.event.clipEndSeconds-event.event.clipStartSeconds))<0.0002,"clip samples match reported bounds");
        check("quiet".equals(event.event.endedBy),"quiet-end reason is preserved");

        CaptureEngine capped=new CaptureEngine(RATE);
        silence(capped,30);
        CaptureEngine.Result last=null;
        for(int n=0;n<CaptureEngine.MAX_EVENTS;n++){
            silence(capped,11);
            feed(capped,2,(short)7000);
            last=feed(capped,5,(short)0);
            check(last.event!=null,"each bounded pulse should close as one event");
            if(n<CaptureEngine.MAX_EVENTS-1)check(!last.storageLimit,"the station must remain available below the clip cap");
        }
        check(last.storageLimit && capped.isStopped(),"reaching the clip cap stops the detector");

        try {
            ByteArrayOutputStream output=new ByteArrayOutputStream();
            SessionZip.write(output,Arrays.asList(
                    new SessionZip.Entry("session.json","{}\n".getBytes(StandardCharsets.UTF_8)),
                    new SessionZip.Entry("READ-ME.txt","Local only".getBytes(StandardCharsets.UTF_8))));
            byte[] zip=output.toByteArray();int end=zip.length-22;long directory=u32(zip,end+16);
            check(u32(zip,0)==0x04034b50L,"the session export starts with the required ZIP entry header");
            check(u16(zip,6)==0 && u16(zip,8)==0,"the browser format requires plain flags and no compression");
            check(u32(zip,end)==0x06054b50L && u16(zip,end+10)==2,"the ZIP directory and file count are valid");
            check(directory+u32(zip,end+12)==end,"the central-directory size and offset end exactly at the ZIP trailer");
            check(directory<end && u32(zip,(int)directory)==0x02014b50L,"the central directory points to the entries");
        } catch(Exception failure) { throw new AssertionError("session ZIP format checks failed",failure); }
        System.out.println("Android core checks passed: detector boundaries and strict browser-compatible ZIP headers.");
    }
}
