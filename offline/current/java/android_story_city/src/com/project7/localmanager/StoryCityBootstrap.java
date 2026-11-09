package com.project7.localmanager;
import android.content.Context;
import java.io.IOException;
/** Production startup owner for the source city catalog and COC policy assets. */
public final class StoryCityBootstrap {
 private StoryCityBootstrap() {}
 public static void prepare(Context context) throws IOException {
  StoryCityPolicy.prepare(context);
  StoryCityCocPolicy.prepare(context);
  StoryMenuEntryData.prepare(context);
  StoryMenuShared.prepare(context);
 }
}
