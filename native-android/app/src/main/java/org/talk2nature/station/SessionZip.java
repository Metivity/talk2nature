package org.talk2nature.station;

import java.io.IOException;
import java.io.OutputStream;
import java.nio.charset.StandardCharsets;
import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.Set;
import java.util.zip.CRC32;

/** The exact flat, uncompressed ZIP subset accepted by the browser's bounded session importer. */
public final class SessionZip {
    private static final int MAX_FILES=26;
    private static final int MAX_PAYLOAD=26*1024*1024;
    private SessionZip() {}

    public static final class Entry {
        public final String name;
        public final byte[] bytes;
        public Entry(String name,byte[] bytes){this.name=name;this.bytes=bytes;}
    }

    public static void write(OutputStream output,List<Entry> entries)throws IOException {
        if(output==null || entries==null || entries.size()<2 || entries.size()>MAX_FILES)
            throw new IllegalArgumentException("A session ZIP needs 2–26 bounded files.");
        Set<String> names=new HashSet<>();List<Central> central=new ArrayList<>();long offset=0,total=0;
        for(Entry entry:entries){
            if(entry==null || entry.name==null || !entry.name.matches("[a-zA-Z0-9][a-zA-Z0-9_.-]{0,119}") || entry.bytes==null || !names.add(entry.name))
                throw new IllegalArgumentException("Invalid or duplicate session filename.");
            byte[] name=entry.name.getBytes(StandardCharsets.US_ASCII),payload=entry.bytes;
            total+=payload.length;
            if(total>MAX_PAYLOAD)throw new IllegalArgumentException("Session export exceeds its size limit.");
            CRC32 crc=new CRC32();crc.update(payload);long checksum=crc.getValue();
            write32(output,0x04034b50L);write16(output,20);write16(output,0);write16(output,0);write16(output,0);write16(output,33);
            write32(output,checksum);write32(output,payload.length);write32(output,payload.length);write16(output,name.length);write16(output,0);
            output.write(name);output.write(payload);
            central.add(new Central(name,payload.length,checksum,offset));
            offset+=30L+name.length+payload.length;
        }
        long directoryOffset=offset;
        long directorySize=0;
        for(Central file:central){
            write32(output,0x02014b50L);write16(output,20);write16(output,20);write16(output,0);write16(output,0);write16(output,0);write16(output,33);
            write32(output,file.crc);write32(output,file.length);write32(output,file.length);write16(output,file.name.length);
            write16(output,0);write16(output,0);write16(output,0);write16(output,0);write32(output,0);write32(output,file.offset);
            output.write(file.name);
            directorySize+=46L+file.name.length;
        }
        write32(output,0x06054b50L);write16(output,0);write16(output,0);write16(output,central.size());write16(output,central.size());
        write32(output,directorySize);write32(output,directoryOffset);write16(output,0);output.flush();
    }

    private static void write16(OutputStream out,long value)throws IOException {out.write((int)value&255);out.write((int)(value>>>8)&255);}
    private static void write32(OutputStream out,long value)throws IOException {write16(out,value);write16(out,value>>>16);}
    private static final class Central {
        final byte[] name;final int length;final long crc,offset;
        Central(byte[] name,int length,long crc,long offset){this.name=name;this.length=length;this.crc=crc;this.offset=offset;}
    }
}
