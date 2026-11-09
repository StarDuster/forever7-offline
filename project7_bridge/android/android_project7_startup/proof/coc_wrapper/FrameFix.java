import java.util.jar.*;
import java.io.*;
import org.objectweb.asm.*;
public final class FrameFix {
  public static void main(String[] args) throws Exception {
    int count=0;
    try(JarFile input=new JarFile(args[0]);JarOutputStream output=new JarOutputStream(new FileOutputStream(args[1]))) {
      java.util.Enumeration<JarEntry> entries=input.entries();
      while(entries.hasMoreElements()) {
        JarEntry entry=entries.nextElement();byte[] data;
        try(InputStream stream=input.getInputStream(entry)){data=stream.readAllBytes();}
        if(entry.getName().endsWith(".class")) {
          ClassReader reader=new ClassReader(data);
          ClassWriter writer=new ClassWriter(ClassWriter.COMPUTE_FRAMES|ClassWriter.COMPUTE_MAXS);
          reader.accept(writer,ClassReader.SKIP_FRAMES);data=writer.toByteArray();count++;
        }
        JarEntry target=new JarEntry(entry.getName());target.setTime(0);output.putNextEntry(target);output.write(data);output.closeEntry();
      }
    }
    System.out.println("frames_recomputed_classes="+count);
  }
}
